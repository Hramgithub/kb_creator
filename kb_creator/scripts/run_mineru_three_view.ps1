[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("hybrid_high", "pipeline_ocr", "pipeline_txt", "vlm_local")]
  [string]$Profile,

  [Parameter(Mandatory = $true)]
  [string]$InputPath,

  [Parameter(Mandatory = $true)]
  [string]$OutputPath,

  [string]$MinerURoot,

  [string]$ToolRoot,

  [string]$SourceRoot,

  [string]$RuntimeRoot,

  [ValidateSet("en", "ch", "chinese_cht", "korean", "japan", "latin", "arabic", "east_slavic", "cyrillic", "devanagari", "ta", "te", "ka", "th", "el")]
  [string]$OcrLanguage = "en",

  [int]$StartPage,
  [int]$EndPage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$cpuFirst = $PSBoundParameters.ContainsKey("ToolRoot")
if ($cpuFirst) {
  if ($PSBoundParameters.ContainsKey("MinerURoot")) {
    throw "-ToolRoot and legacy -MinerURoot are mutually exclusive."
  }
  if (-not $PSBoundParameters.ContainsKey("SourceRoot")) {
    $SourceRoot = Join-Path $PSScriptRoot "..\..\MinerU"
  }
  $sourceRootPath = [System.IO.Path]::GetFullPath($SourceRoot)
  $profileCommon = Join-Path $sourceRootPath "scripts\profile-common.ps1"
  if (-not (Test-Path -LiteralPath $profileCommon -PathType Leaf)) {
    throw "CPU-first SourceRoot must contain MinerU scripts/profile-common.ps1: $sourceRootPath"
  }
  . $profileCommon
  $roots = Get-MinerUProfileRoots -ToolRoot $ToolRoot
  if (-not [System.IO.Path]::GetFullPath($roots.SourceRoot).Equals($sourceRootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "CPU-first SourceRoot did not produce the verified MinerU profile root."
  }
  $profileId = if ($Profile -in @("pipeline_txt", "pipeline_ocr")) { "pipeline-cpu-v1" } else { "windows-cu128-v1" }
  $definition = Get-MinerUProfileDefinition -Profile $profileId -Roots $roots
  foreach ($path in @($definition.Python, $definition.MinerU, $definition.Config, $definition.VerifyReceipt)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
      throw "Verified MinerU profile input is missing: $path"
    }
  }
  $receiptHelper = Join-Path $roots.SourceRoot "scripts\profile_receipt.py"
  $modelManifest = Join-Path $roots.SourceRoot "models\manifest.json"
  $processHelper = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\pipeline\windows_process_tree.py"))
  if (-not (Test-Path -LiteralPath $receiptHelper -PathType Leaf) -or
      -not (Test-Path -LiteralPath $modelManifest -PathType Leaf) -or
      -not (Test-Path -LiteralPath $processHelper -PathType Leaf)) {
    throw "MinerU verification input or closed process-tree helper is missing."
  }
  & $definition.Python $receiptHelper validate-verify --receipt $definition.VerifyReceipt --profile $definition.PublicName --manifest $modelManifest 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "MinerU profile verification receipt is invalid."
  }
  if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf) -or [System.IO.Path]::GetExtension($InputPath) -notmatch '^(?i)\.pdf$') {
    throw "Input must be an existing PDF."
  }
  $hasStartPage = $PSBoundParameters.ContainsKey("StartPage")
  $hasEndPage = $PSBoundParameters.ContainsKey("EndPage")
  if (-not $hasStartPage -or -not $hasEndPage -or $StartPage -lt 0 -or $EndPage -lt $StartPage) {
    throw "CPU-first execution requires an exact zero-based StartPage/EndPage range."
  }
  $output = [System.IO.Path]::GetFullPath($OutputPath)
  if (Test-Path -LiteralPath $output) {
    throw "CPU-first MinerU output path must be absent."
  }
  $input = (Resolve-Path -LiteralPath $InputPath).Path
  $runtime = if ($PSBoundParameters.ContainsKey("RuntimeRoot")) {
    [System.IO.Path]::GetFullPath($RuntimeRoot)
  }
  else {
    $definition.RuntimeRoot
  }
  $homeRoot = Join-Path $runtime "home"
  $roamingAppData = Join-Path $homeRoot "AppData\Roaming"
  $localAppData = Join-Path $homeRoot "AppData\Local"
  $invocationRoot = Join-Path $runtime "invocations"
  $runtimePaths = @(
    (Join-Path $runtime "tmp"),
    (Join-Path $runtime "hf"),
    (Join-Path $runtime "hf\hub"),
    (Join-Path $runtime "hf\xet"),
    (Join-Path $runtime "modelscope"),
    $homeRoot,
    $roamingAppData,
    $localAppData,
    (Join-Path $runtime "python-user"),
    (Join-Path $runtime "xdg-cache"),
    $invocationRoot
  )
  if ($PSBoundParameters.ContainsKey("RuntimeRoot")) {
    Assert-MinerUPathContained -Base (Split-Path -Parent $output) -Candidate $runtime | Out-Null
  }
  else {
    Assert-MinerUPathContained -Base $roots.ToolRoot -Candidate $runtime | Out-Null
  }
  foreach ($runtimePath in $runtimePaths) {
    Assert-MinerUPathContained -Base $runtime -Candidate $runtimePath | Out-Null
  }
  New-Item -ItemType Directory -Force -Path (@($output) + $runtimePaths) | Out-Null
  $arguments = @("--path", $input, "--output", $output, "--backend")
  if ($Profile -in @("pipeline_txt", "pipeline_ocr")) {
    $arguments += @("pipeline", "--method", $(if ($Profile -eq "pipeline_txt") { "txt" } else { "ocr" }), "--lang", $OcrLanguage)
  }
  elseif ($Profile -eq "hybrid_high") {
    $arguments += @("hybrid-engine", "--method", "txt", "--effort", "high")
  }
  else {
    # VLM method is not applicable and --method is deliberately omitted.
    $arguments += @("vlm-engine")
  }
  $arguments += @("--formula", "True", "--table", "True", "--start", [string]$StartPage, "--end", [string]$EndPage)

  # MinerU's API client otherwise uses its internal 3600-second result wait.
  # Keep an explicit 3600-second margin inside the closed runner's 21600-second
  # active timeout for artifact download and cleanup.
  $innerTaskResultTimeoutSeconds = 18000
  $allowedEnvironment = [ordered]@{
    SystemRoot = $env:SystemRoot
    WINDIR = $env:WINDIR
    ComSpec = $env:ComSpec
    PATHEXT = $env:PATHEXT
    PATH = ((Join-Path $definition.VenvRoot "Scripts") + ";" + (Join-Path $env:SystemRoot "System32"))
    TEMP = (Join-Path $runtime "tmp")
    TMP = (Join-Path $runtime "tmp")
    USERPROFILE = $homeRoot
    HOME = $homeRoot
    APPDATA = $roamingAppData
    LOCALAPPDATA = $localAppData
    PYTHONUSERBASE = (Join-Path $runtime "python-user")
    PYTHONNOUSERSITE = "1"
    PYTHONUTF8 = "1"
    PYTHONIOENCODING = "utf-8:backslashreplace"
    XDG_CACHE_HOME = (Join-Path $runtime "xdg-cache")
    HF_HOME = (Join-Path $runtime "hf")
    HUGGINGFACE_HUB_CACHE = (Join-Path $runtime "hf\hub")
    HF_XET_CACHE = (Join-Path $runtime "hf\xet")
    MODELSCOPE_CACHE = (Join-Path $runtime "modelscope")
    HF_HUB_OFFLINE = "1"
    TRANSFORMERS_OFFLINE = "1"
    MINERU_TOOLS_CONFIG_JSON = $definition.Config
    MINERU_DEVICE_MODE = $(if ($profileId -eq "pipeline-cpu-v1") { "cpu" } else { "cuda" })
    MINERU_PROCESSING_WINDOW_SIZE = "1"
    MINERU_API_MAX_CONCURRENT_REQUESTS = "1"
    MINERU_TASK_RESULT_TIMEOUT_SECONDS = [string]$innerTaskResultTimeoutSeconds
    NO_PROXY = "127.0.0.1,localhost"
  }
  if ($profileId -eq "windows-cu128-v1") {
    $allowedEnvironment.MINERU_LMDEPLOY_DEVICE = "cuda"
    $allowedEnvironment.TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER = "0"
  }
  function Read-MinerUStableLog {
    param([Parameter(Mandatory = $true)][string]$Path, [int]$ByteLimit = 65536)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
      return [pscustomobject]@{ Text = ""; ByteTruncated = $false }
    }
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
    try {
      $utf8 = [System.Text.UTF8Encoding]::new($false, $false)
      if ($stream.Length -le $ByteLimit) {
        $buffer = [byte[]]::new([int]$stream.Length); $null = $stream.Read($buffer, 0, $buffer.Length)
        return [pscustomobject]@{ Text = $utf8.GetString($buffer); ByteTruncated = $false }
      }
      $marker = [System.Text.Encoding]::UTF8.GetBytes("`n...[middle omitted]`n")
      $available = $ByteLimit - $marker.Length; $headLength = [System.Math]::Floor($available / 2); $tailLength = $available - $headLength
      $head = [byte[]]::new($headLength); $null = $stream.Read($head, 0, $head.Length)
      $stream.Seek(-$tailLength, [System.IO.SeekOrigin]::End) | Out-Null
      $tail = [byte[]]::new($tailLength); $null = $stream.Read($tail, 0, $tail.Length)
      return [pscustomobject]@{ Text = ($utf8.GetString($head) + [System.Text.Encoding]::UTF8.GetString($marker) + $utf8.GetString($tail)); ByteTruncated = $true }
    }
    finally {
      $stream.Dispose()
    }
  }
  function Convert-MinerUFailureChunk {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text, [Parameter(Mandatory = $true)][hashtable]$State, [switch]$Final)
    $builder = [System.Text.StringBuilder]::new()
    for ($index = 0; $index -lt $Text.Length; $index++) {
      $character = $Text[$index]
      if ($State.PendingCR) {
        $State.PendingCR = $false
        if ($character -eq "`n") { [void]$builder.Append("`n"); continue }
        [void]$builder.Append("`n")
      }
      switch ([string]$State.Mode) {
        "Normal" {
          if ($character -eq "`r") { $State.PendingCR = $true }
          elseif ($character -eq "`e") { $State.Mode = "Escape" }
          elseif ([int][char]$character -eq 10) { [void]$builder.Append("`n") }
          elseif (([int][char]$character -ge 0 -and [int][char]$character -le 8) -or ([int][char]$character -ge 11 -and [int][char]$character -le 31) -or [int][char]$character -eq 127) { [void]$builder.Append("?") }
          else { [void]$builder.Append($character) }
        }
        "Escape" { if ($character -eq "[") { $State.Mode = "CSI" } elseif ($character -eq "]") { $State.Mode = "OSC" } else { $State.Mode = "Normal" } }
        "CSI" { if ([int][char]$character -ge 64 -and [int][char]$character -le 126) { $State.Mode = "Normal" } }
        "OSC" { if ([int][char]$character -eq 7) { $State.Mode = "Normal" } elseif ($character -eq "`e") { $State.Mode = "OSC_Escape" } }
        "OSC_Escape" { if ($character -eq "\") { $State.Mode = "Normal" } else { $State.Mode = "OSC" } }
      }
    }
    if ($Final) { if ($State.PendingCR) { [void]$builder.Append("`n"); $State.PendingCR = $false }; $State.Mode = "Normal" }
    return $builder.ToString()
  }
  function Read-MinerUFailureLogStream {
    param([Parameter(Mandatory = $true)][string]$Source, [Parameter(Mandatory = $true)][string]$Destination)
    $temporary = "$Destination.tmp-$([System.Guid]::NewGuid().ToString('N'))"
    $inputStream = $null; $reader = $null; $outputStream = $null; $writer = $null
    try {
      $utf8 = [System.Text.UTF8Encoding]::new($false, $false)
      $inputStream = [System.IO.File]::Open($Source, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete)
      $reader = [System.IO.StreamReader]::new($inputStream, $utf8, $true, 8192)
      $outputStream = [System.IO.File]::Open($temporary, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
      $writer = [System.IO.StreamWriter]::new($outputStream, $utf8, 8192)
      $buffer = [char[]]::new(8192); $state = @{ Mode = "Normal"; PendingCR = $false }
      while (($count = $reader.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $writer.Write((Convert-MinerUFailureChunk -Text (-join $buffer[0..($count - 1)]) -State $state))
      }
      $writer.Write((Convert-MinerUFailureChunk -Text "" -State $state -Final))
      $writer.Flush(); $writer.Dispose(); $writer = $null; $outputStream.Dispose(); $outputStream = $null
      Move-Item -LiteralPath $temporary -Destination $Destination
    }
    finally {
      if ($writer) { $writer.Dispose() }; if ($outputStream) { $outputStream.Dispose() }
      if ($reader) { $reader.Dispose() }; if ($inputStream) { $inputStream.Dispose() }
      if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
  }
  function Get-MinerUFailureIdentity {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$RelativePath)
    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
      $bytes = $hash.ComputeHash([System.IO.File]::ReadAllBytes($Path))
    } finally { $hash.Dispose() }
    $tailBuilder = [System.Text.StringBuilder]::new()
    $reader = [System.IO.StreamReader]::new($Path, [System.Text.UTF8Encoding]::new($false, $false), $true, 8192)
    $buffer = [char[]]::new(8192); $totalChars = 0
    try {
      while (($count = $reader.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $totalChars += $count; [void]$tailBuilder.Append((-join $buffer[0..($count - 1)]))
        if ($tailBuilder.Length -gt 16384) { $tailBuilder.Remove(0, $tailBuilder.Length - 16384) | Out-Null }
      }
    } finally { $reader.Dispose() }
    $length = (Get-Item -LiteralPath $Path).Length
    [ordered]@{ path = $RelativePath; bytes = [int64]$length; sha256 = [System.Convert]::ToHexString($bytes); tail = $tailBuilder.ToString(); inline_truncated = ($totalChars -gt 16384) }
  }
  function Write-MinerUFailureLogs {
    param([Parameter(Mandatory = $true)][string]$StdoutPath, [Parameter(Mandatory = $true)][string]$StderrPath, [Parameter(Mandatory = $true)][string]$InvocationId)
    $logs = [ordered]@{}
    $artifactRoot = Join-Path $output "artifacts"
    New-Item -ItemType Directory -Force -Path $artifactRoot | Out-Null
    foreach ($item in @(@{ Name = "stdout"; Source = $StdoutPath }, @{ Name = "stderr"; Source = $StderrPath })) {
      $fileName = "failure-$InvocationId-$($item.Name)-full.log"
      $destination = Join-Path $artifactRoot $fileName
      if (Test-Path -LiteralPath $item.Source -PathType Leaf) {
        Read-MinerUFailureLogStream -Source $item.Source -Destination $destination
      }
      else {
        [System.IO.File]::WriteAllText($destination, "", [System.Text.UTF8Encoding]::new($false))
      }
      $logs[$item.Name] = Get-MinerUFailureIdentity -Path $destination -RelativePath "artifacts/$fileName"
    }
    return $logs
  }
  function Complete-MinerUResult {
    param([Parameter(Mandatory = $true)]$Result)
    if ([int]$Result.ExitCode -ne 0) {
      $Result | Add-Member -NotePropertyName FailureLogs -NotePropertyValue (Write-MinerUFailureLogs -StdoutPath $stdoutPath -StderrPath $stderrPath -InvocationId $Result.InvocationId) -Force
    }
    return $Result
  }
  function Invoke-MinerUClosedProcess {
    param(
      [Parameter(Mandatory = $true)][string[]]$Arguments,
      [Parameter(Mandatory = $true)][int]$ActiveTimeoutSeconds
    )
    $invocationId = [System.Guid]::NewGuid().ToString("N")
    $specPath = Join-Path $invocationRoot "$invocationId.spec.json"
    $resultPath = Join-Path $invocationRoot "$invocationId.result.json"
    $stdoutPath = Join-Path $invocationRoot "$invocationId.stdout.log"
    $stderrPath = Join-Path $invocationRoot "$invocationId.stderr.log"
    $specTemporary = "$specPath.tmp"
    foreach ($temporaryPath in @($specPath, $specTemporary, $resultPath, $stdoutPath, $stderrPath)) {
      Assert-MinerUPathContained -Base $runtime -Candidate $temporaryPath | Out-Null
    }
    $spec = [ordered]@{
      schema = "kb_creator.windows_process_tree_spec.v1"
      executable = $definition.MinerU
      arguments = @($Arguments)
      working_directory = $roots.WorkspaceRoot
      environment = $allowedEnvironment
      stdout_path = $stdoutPath
      stderr_path = $stderrPath
      active_timeout_seconds = $ActiveTimeoutSeconds
      cleanup_timeout_seconds = 30
    }
    try {
      [System.IO.File]::WriteAllText($specTemporary, (($spec | ConvertTo-Json -Depth 10) + "`n"), [System.Text.UTF8Encoding]::new($false))
      Move-Item -LiteralPath $specTemporary -Destination $specPath
      & $definition.Python -B $processHelper --spec $specPath --result $resultPath --runtime-root $runtime
      $helperExitCode = $LASTEXITCODE
      if (-not (Test-Path -LiteralPath $resultPath -PathType Leaf)) {
        return Complete-MinerUResult ([pscustomobject]@{
          InvocationId = $invocationId
          ExitCode = 125; Stdout = ""; Stderr = "closed process-tree helper did not write its result"
          StdoutByteTruncated = $false; StderrByteTruncated = $false; RunnerState = "helper_error"
          TimedOut = $false; CleanupCompleted = $false
        })
      }
      $runner = Get-Content -Raw -LiteralPath $resultPath | ConvertFrom-Json -DateKind String
      $expectedResultKeys = @("cleanup_completed", "exit_code", "helper_error", "schema", "state", "timed_out")
      $actualResultKeys = @($runner.PSObject.Properties.Name | Sort-Object)
      $resultCouplingValid = (
        ($runner.state -ceq "completed" -and $runner.timed_out -eq $false -and $runner.cleanup_completed -eq $true -and $null -eq $runner.helper_error) -or
        ($runner.state -ceq "active_timeout" -and $runner.exit_code -eq 124 -and $runner.timed_out -eq $true -and $runner.cleanup_completed -eq $true -and $null -eq $runner.helper_error) -or
        ($runner.state -ceq "cleanup_timeout" -and $runner.cleanup_completed -eq $false -and $null -eq $runner.helper_error) -or
        ($runner.state -ceq "helper_error" -and $runner.exit_code -eq 125 -and $runner.cleanup_completed -eq $false -and $runner.helper_error -is [string] -and $runner.helper_error.Length -gt 0)
      )
      if (($actualResultKeys -join "`n") -cne (($expectedResultKeys | Sort-Object) -join "`n") -or
          $runner.schema -cne "kb_creator.windows_process_tree_result.v2" -or
          $runner.state -notin @("completed", "active_timeout", "cleanup_timeout", "helper_error") -or
          $runner.exit_code -isnot [long] -or $runner.timed_out -isnot [bool] -or
          $runner.cleanup_completed -isnot [bool] -or
          ($null -ne $runner.helper_error -and $runner.helper_error -isnot [string]) -or
          -not $resultCouplingValid) {
        return Complete-MinerUResult ([pscustomobject]@{
          InvocationId = $invocationId
          ExitCode = 125; Stdout = ""; Stderr = "closed process-tree helper returned an invalid result"
          StdoutByteTruncated = $false; StderrByteTruncated = $false; RunnerState = "helper_error"
          TimedOut = $false; CleanupCompleted = $false
        })
      }
      $stdout = Read-MinerUStableLog -Path $stdoutPath
      $stderr = Read-MinerUStableLog -Path $stderrPath
      $helperMessage = if ($null -eq $runner.helper_error) { "" } else { [string]$runner.helper_error }
      if ($helperExitCode -ne 0 -and -not $helperMessage) {
        $helperMessage = "closed process-tree helper exited with code $helperExitCode"
      }
      $effectiveExitCode = if ($runner.state -ceq "completed" -and $runner.cleanup_completed -eq $true -and $helperExitCode -eq 0) {
        [int]$runner.exit_code
      }
      elseif ($runner.state -ceq "active_timeout") { 124 }
      elseif ($runner.state -ceq "cleanup_timeout") { 126 }
      else { 125 }
      Complete-MinerUResult ([pscustomobject]@{
        InvocationId = $invocationId
        ExitCode = $effectiveExitCode
        Stdout = $stdout.Text
        Stderr = (($stderr.Text, $helperMessage | Where-Object { $_ }) -join "`n")
        StdoutByteTruncated = [bool]$stdout.ByteTruncated
        StderrByteTruncated = [bool]$stderr.ByteTruncated
        RunnerState = [string]$runner.state
        TimedOut = [bool]$runner.timed_out
        CleanupCompleted = [bool]$runner.cleanup_completed
      })
    }
    catch {
      $stdout = Read-MinerUStableLog -Path $stdoutPath
      $stderr = Read-MinerUStableLog -Path $stderrPath
      $message = "closed process-tree invocation failed: $($_.Exception.Message)"
      return Complete-MinerUResult ([pscustomobject]@{
        InvocationId = $invocationId
        ExitCode = 125; Stdout = $stdout.Text; Stderr = (($stderr.Text, $message | Where-Object { $_ }) -join "`n")
        StdoutByteTruncated = [bool]$stdout.ByteTruncated; StderrByteTruncated = [bool]$stderr.ByteTruncated
        RunnerState = "helper_error"; TimedOut = $false; CleanupCompleted = $false
      })
    }
    finally {
      foreach ($temporaryPath in @($specPath, $specTemporary, $resultPath, $stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $temporaryPath) { Remove-Item -LiteralPath $temporaryPath -Force }
      }
    }
  }
  function Get-MinerUBoundedSanitizedText {
    param([AllowNull()][string]$Text, [int]$Limit = 16384)
    $value = if ($null -eq $Text) { "" } else { $Text }
    $value = ($value -replace "`r`n", "`n") -replace "`r", "`n"
    $value = $value -replace "`e(?:\[[0-?]*[ -/]*[@-~]|\][^`a]*(?:`a|$))", ""
    $value = $value -replace "[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "?"
    $truncated = $value.Length -gt $Limit
    if ($truncated) {
      $marker = "`n...[middle omitted]`n"; $available = $Limit - $marker.Length
      $headLength = [System.Math]::Floor($available / 2); $tailLength = $available - $headLength
      $value = $value.Substring(0, $headLength) + $marker + $value.Substring($value.Length - $tailLength)
    }
    [pscustomobject]@{ Text = $value; Truncated = $truncated }
  }
  function Write-MinerUFailureEvidence {
    param(
      [Parameter(Mandatory = $true)][string]$Phase,
      [Parameter(Mandatory = $true)]$Result,
      [Parameter(Mandatory = $true)][string[]]$ClosedArguments
    )
    $stdout = Get-MinerUBoundedSanitizedText -Text $Result.Stdout
    $stderr = Get-MinerUBoundedSanitizedText -Text $Result.Stderr
    $portable = [ordered]@{
      schema = "kb_creator.mineru_closed_invocation_failure.v3"
      profile = $Profile
      argv_shape_version = 1
      phase = $Phase
      arguments = @($ClosedArguments)
      environment = $allowedEnvironment
      exit_code = [int]$Result.ExitCode
      stdout = $stdout.Text
      stderr = $stderr.Text
      stdout_truncated = [bool]($stdout.Truncated -or $Result.StdoutByteTruncated)
      stderr_truncated = [bool]($stderr.Truncated -or $Result.StderrByteTruncated)
      stdout_total_bytes = if ($null -ne $Result.FailureLogs) { [int64]$Result.FailureLogs.stdout.bytes } else { 0 }
      stderr_total_bytes = if ($null -ne $Result.FailureLogs) { [int64]$Result.FailureLogs.stderr.bytes } else { 0 }
      full_logs = if ($null -ne $Result.FailureLogs) { $Result.FailureLogs } else { [ordered]@{} }
      runner = [ordered]@{
        state = $Result.RunnerState
        timed_out = [bool]$Result.TimedOut
        cleanup_completed = [bool]$Result.CleanupCompleted
      }
    }
    $canonical = $portable | ConvertTo-Json -Depth 10 -Compress
    $hash = [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($canonical))
    $portable.failure_sha256 = [System.Convert]::ToHexString($hash)
    $destination = Join-Path $output "failure.json"
    $temporary = "$destination.tmp-$([System.Guid]::NewGuid().ToString('N'))"
    [System.IO.File]::WriteAllText($temporary, (($portable | ConvertTo-Json -Depth 10) + "`n"), [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $destination
  }
  $version = Invoke-MinerUClosedProcess -Arguments @("--version") -ActiveTimeoutSeconds 120
  $help = Invoke-MinerUClosedProcess -Arguments @("--help") -ActiveTimeoutSeconds 120
  if ($version.ExitCode -ne 0 -or $help.ExitCode -ne 0) {
    if ($version.ExitCode -ne 0) {
      Write-MinerUFailureEvidence -Phase "version" -Result $version -ClosedArguments @("--version")
    }
    else {
      Write-MinerUFailureEvidence -Phase "help" -Result $help -ClosedArguments @("--help")
    }
    throw "MinerU CLI version/help surface is unavailable."
  }
  $helpText = $help.Stdout + $help.Stderr
  foreach ($flag in @("--path", "--output", "--backend", "--formula", "--table", "--start", "--end")) {
    if (-not $helpText.Contains($flag)) { throw "MinerU CLI no longer exposes reviewed flag $flag." }
  }
  if ($Profile -in @("pipeline_txt", "pipeline_ocr") -and (-not $helpText.Contains("--method") -or -not $helpText.Contains("--lang"))) {
    throw "MinerU pipeline CLI no longer exposes reviewed method/language flags."
  }
  if ($Profile -eq "hybrid_high" -and (-not $helpText.Contains("--method") -or -not $helpText.Contains("--effort"))) {
    throw "MinerU hybrid CLI no longer exposes reviewed method/effort flags."
  }
  $result = Invoke-MinerUClosedProcess -Arguments $arguments -ActiveTimeoutSeconds 21600
  if ($result.ExitCode -ne 0) {
    Write-MinerUFailureEvidence -Phase "execute" -Result $result -ClosedArguments $arguments
    throw "MinerU failed with exit code $($result.ExitCode)."
  }
  [ordered]@{
    schema = "kb_creator.mineru_closed_invocation.v2"
    profile = $Profile
    argv_shape_version = 1
    arguments = $arguments
    environment = $allowedEnvironment
    version_output = ($version.Stdout + $version.Stderr).Trim()
    exit_code = 0
    runner = [ordered]@{
      state = $result.RunnerState
      timed_out = [bool]$result.TimedOut
      cleanup_completed = [bool]$result.CleanupCompleted
    }
  } | ConvertTo-Json -Depth 8 -Compress
  return
}

if ($Profile -notin @("hybrid_high", "pipeline_ocr")) {
  throw "Profile '$Profile' requires CPU-first -ToolRoot execution; legacy -MinerURoot accepts only hybrid_high or pipeline_ocr."
}
if (-not $PSBoundParameters.ContainsKey("MinerURoot")) {
  throw "Legacy execution requires -MinerURoot."
}

$minerRoot = (Resolve-Path -LiteralPath $MinerURoot).Path
$mineru = Join-Path $minerRoot ".venv\Scripts\mineru.exe"
$runtime = Join-Path $minerRoot ".runtime"
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$initialize = Join-Path $workspaceRoot "MinerU\scripts\initialize.ps1"

if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
  throw "Input PDF does not exist: $InputPath"
}
if ([System.IO.Path]::GetExtension($InputPath) -notmatch '^(?i)\.pdf$') {
  throw "Input must be a PDF: $InputPath"
}
if (-not (Test-Path -LiteralPath $mineru -PathType Leaf) -or -not (Test-Path -LiteralPath $initialize -PathType Leaf)) {
  throw "MinerU tool installation or portable initializer is missing: $minerRoot"
}
$hasStartPage = $PSBoundParameters.ContainsKey("StartPage")
$hasEndPage = $PSBoundParameters.ContainsKey("EndPage")
if ($hasStartPage -xor $hasEndPage) {
  throw "Specify both StartPage and EndPage, or omit both for the full document."
}
if ($hasStartPage -and ($StartPage -lt 0 -or $EndPage -lt $StartPage)) {
  throw "Invalid page range: $StartPage..$EndPage"
}

$configPath = & $initialize -ToolRoot $minerRoot
New-Item -ItemType Directory -Force -Path $OutputPath, (Join-Path $runtime "tmp"), (Join-Path $runtime "hf") | Out-Null
foreach ($name in @("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "GIT_HTTP_PROXY", "GIT_HTTPS_PROXY", "http_proxy", "https_proxy", "all_proxy")) {
  if (Test-Path "Env:$name") { Remove-Item "Env:$name" }
}
$env:NO_PROXY = "*"
$env:no_proxy = "*"
$env:HF_HOME = Join-Path $runtime "hf"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $runtime "hf\hub"
$env:HF_XET_CACHE = Join-Path $runtime "hf\xet"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
$env:TEMP = Join-Path $runtime "tmp"
$env:TMP = $env:TEMP
$env:MINERU_TOOLS_CONFIG_JSON = $configPath
$env:MINERU_LMDEPLOY_BACKEND = "pytorch"
$env:TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER = "0"
if (Test-Path "Env:TORCH_COMPILE_DISABLE") { Remove-Item "Env:TORCH_COMPILE_DISABLE" }

$arguments = @("--path", (Resolve-Path -LiteralPath $InputPath).Path, "--output", (Resolve-Path -LiteralPath $OutputPath).Path, "--formula", "True", "--table", "True")
if ($Profile -eq "hybrid_high") {
  $arguments += @("--backend", "hybrid-engine", "--effort", "high")
} else {
  $arguments += @("--backend", "pipeline", "--method", "ocr")
}
if ($hasStartPage) { $arguments += @("--start", $StartPage, "--end", $EndPage) }

Write-Host "MinerU profile: $Profile"
Write-Host "MinerU root: $minerRoot"
Write-Host "Torch compile: enabled; static CUDA launcher: disabled"
& $mineru @arguments
if ($LASTEXITCODE -ne 0) { throw "MinerU failed with exit code $LASTEXITCODE." }
