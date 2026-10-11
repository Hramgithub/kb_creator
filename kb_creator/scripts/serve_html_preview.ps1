[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HtmlPath,

    [ValidateRange(1024, 65535)]
    [int]$Port = 8765
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedHtml = (Resolve-Path -LiteralPath $HtmlPath).Path
if ([System.IO.Path]::GetExtension($resolvedHtml) -notin @(".html", ".htm")) {
    throw "HtmlPath must point to an .html or .htm file: $resolvedHtml"
}

$previewRoot = Split-Path -Parent $resolvedHtml
$previewFile = Split-Path -Leaf $resolvedHtml
$encodedFile = [System.Uri]::EscapeDataString($previewFile)
$previewUrl = "http://127.0.0.1:$Port/$encodedFile"

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
$pythonArguments = @("-m", "http.server", $Port, "--bind", "127.0.0.1", "--directory", $previewRoot)

if ($null -eq $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    $pythonArguments = @("-3", "-m", "http.server", $Port, "--bind", "127.0.0.1", "--directory", $previewRoot)
}

if ($null -eq $pythonCommand) {
    throw "Python was not found on PATH. Install Python or use the bundled Codex Python runtime."
}

Write-Host "HTML preview root: $previewRoot"
Write-Host "Open: $previewUrl"
Write-Host "Press Ctrl+C after visual verification to stop the preview server."

& $pythonCommand.Source @pythonArguments
