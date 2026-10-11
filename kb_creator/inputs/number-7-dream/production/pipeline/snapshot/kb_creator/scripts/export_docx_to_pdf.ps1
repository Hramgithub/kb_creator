[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [Parameter(Mandatory = $true)][string]$Pdf,
    [Parameter(Mandatory = $true)][string]$StageRoot,
    [string]$EvidenceOutput,
    [ValidateRange(10, 600)][int]$TimeoutSeconds = 120,
    [switch]$TransientBridge
)

$ErrorActionPreference = 'Stop'

function Get-FileIdentity {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -Force
    return [ordered]@{
        path = [IO.Path]::GetFullPath($Path)
        bytes = [int64]$item.Length
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
    }
}

function Resolve-ContainedPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Extension,
        [switch]$MustExist
    )
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $rootFull -PathType Container)) { throw "Stage root must exist: $rootFull" }
    $rootItem = Get-Item -LiteralPath $rootFull -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Stage root cannot be a reparse point' }
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $rootFull + [IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Target escapes assigned stage root' }
    if ([IO.Path]::GetExtension($full).ToLowerInvariant() -ne $Extension) { throw "Target must use $Extension" }
    $parent = Split-Path -Parent $full
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'Target parent must already exist' }
    $cursor = Get-Item -LiteralPath $parent -Force
    while ($true) {
        if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Target path contains a reparse point' }
        if ($cursor.FullName.TrimEnd('\') -ieq $rootFull.TrimEnd('\')) { break }
        $cursor = $cursor.Parent
        if ($null -eq $cursor) { throw 'Target parent escapes assigned stage root' }
    }
    if ($MustExist) {
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw 'Required input is missing' }
        $item = Get-Item -LiteralPath $full -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Input cannot be a reparse point' }
    } elseif (Test-Path -LiteralPath $full) {
        throw 'Output must be absent'
    }
    return $full
}

$stageFull = [IO.Path]::GetFullPath($StageRoot)
$docxFull = Resolve-ContainedPath -Path $Docx -Root $stageFull -Extension '.docx' -MustExist
$pdfFull = Resolve-ContainedPath -Path $Pdf -Root $stageFull -Extension '.pdf'
if ($TransientBridge -and $EvidenceOutput) { throw 'TransientBridge forbids evidence output' }
if (-not $TransientBridge -and -not $EvidenceOutput) { throw 'Final export requires EvidenceOutput' }
$evidenceFull = $null
if ($EvidenceOutput) {
    $evidenceFull = Resolve-ContainedPath -Path $EvidenceOutput -Root $stageFull -Extension '.json'
}

$word = $null
$document = $null
$tempPdf = Join-Path (Split-Path -Parent $pdfFull) ('.' + [IO.Path]::GetFileNameWithoutExtension($pdfFull) + '.export-' + [guid]::NewGuid().ToString('N') + '.tmp.pdf')
$cleanup = 'fail'
$failure = $null
$wordPath = $null
$wordVersion = $null
$started = [DateTime]::UtcNow

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $wordVersion = [string]$word.Version
    $wordPath = Join-Path ([string]$word.Path) 'WINWORD.EXE'
    $document = $word.Documents.Open($docxFull, $false, $true, $false)
    $document.ExportAsFixedFormat(
        $tempPdf,
        17,
        $false,
        0,
        0,
        1,
        1,
        0,
        $true,
        $true,
        1,
        $true,
        $true,
        $false
    )
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $previousLength = -1L
    $stable = 0
    while ([DateTime]::UtcNow -lt $deadline) {
        if (Test-Path -LiteralPath $tempPdf -PathType Leaf) {
            $length = (Get-Item -LiteralPath $tempPdf).Length
            if ($length -gt 0 -and $length -eq $previousLength) { $stable += 1 } else { $stable = 0 }
            if ($stable -ge 1) { break }
            $previousLength = $length
        }
        Start-Sleep -Milliseconds 200
    }
    if (-not (Test-Path -LiteralPath $tempPdf -PathType Leaf) -or (Get-Item -LiteralPath $tempPdf).Length -lt 1) {
        throw 'Word did not produce a stable non-empty PDF before timeout'
    }
    Move-Item -LiteralPath $tempPdf -Destination $pdfFull
} catch {
    $failure = $_
} finally {
    try { if ($null -ne $document) { $document.Close($false) } } catch { }
    try { if ($null -ne $word) { $word.Quit() } } catch { }
    try { if ($null -ne $document -and [Runtime.InteropServices.Marshal]::IsComObject($document)) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) } } catch { }
    try { if ($null -ne $word -and [Runtime.InteropServices.Marshal]::IsComObject($word)) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) } } catch { }
    $document = $null
    $word = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    if (Test-Path -LiteralPath $tempPdf) { Remove-Item -LiteralPath $tempPdf -Force }
    $cleanup = if (-not (Test-Path -LiteralPath $tempPdf)) { 'pass' } else { 'fail' }
}

if ($null -ne $failure) {
    [Console]::Error.WriteLine($failure.Exception.Message)
    exit 2
}
if ($cleanup -ne 'pass') {
    [Console]::Error.WriteLine('Word export cleanup failed')
    exit 2
}

if ($TransientBridge) {
    [ordered]@{
        status = 'pass'
        transient_bridge_used = $true
        transient_bridge_cleanup = 'caller_owned'
        word_cleanup = $cleanup
    } | ConvertTo-Json -Compress
    exit 0
}

$evidence = [ordered]@{
    schema = 'kb_creator.word_docx_pdf_export.v1'
    status = 'pass'
    input = Get-FileIdentity -Path $docxFull
    output = Get-FileIdentity -Path $pdfFull
    word = [ordered]@{ path = $wordPath; version = $wordVersion }
    export = [ordered]@{
        export_format = 17
        optimize_for = 0
        range = 0
        item = 0
        include_doc_props = $true
        create_bookmarks = 1
        doc_structure_tags = $true
        bitmap_missing_fonts = $true
        use_iso_19005_1 = $false
        all_pages = $true
        fresh_export = $true
    }
    cleanup = [ordered]@{ document_closed = $true; word_quit = $true; temporary_output_absent = $true; status = $cleanup }
    elapsed_ms = [int64]([DateTime]::UtcNow - $started).TotalMilliseconds
}
$json = $evidence | ConvertTo-Json -Depth 8
$evidenceTemp = $evidenceFull + '.tmp'
[IO.File]::WriteAllText($evidenceTemp, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
Move-Item -LiteralPath $evidenceTemp -Destination $evidenceFull
$evidence | ConvertTo-Json -Depth 8 -Compress
