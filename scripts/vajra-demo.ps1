param(
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Question
)

$ErrorActionPreference = 'Stop'
Write-Host '██    ██    ████       █████  ██████      ████' -ForegroundColor White
Write-Host '██    ██   ██  ██         ██  ██    ██   ██  ██' -ForegroundColor White
Write-Host '██    ██   ██  ██         ██  ██    ██   ██  ██' -ForegroundColor White
Write-Host ' ██  ██    ██████         ██  ██████     ██████' -ForegroundColor White
Write-Host ' ██  ██    ██  ██   ██    ██  ██  ██     ██  ██' -ForegroundColor White
Write-Host '  ████     ██  ██    ██████   ██    ██   ██  ██' -ForegroundColor White
Write-Host 'THE OPEN AGENT RESEARCH ECOSYSTEM' -ForegroundColor White
Write-Host '─────────────────────────────────────────────────────────────────' -ForegroundColor DarkGray

$questionText = ($Question -join ' ').Trim()
if ([string]::IsNullOrWhiteSpace($questionText)) {
    $questionText = (Read-Host 'vajra ➔').Trim()
}
if ([string]::IsNullOrWhiteSpace($questionText)) {
    Write-Error 'Please enter a research question.'
    exit 2
}

$mode = if ([string]::IsNullOrWhiteSpace($env:VAJRA_MODE)) { 'standard' } else { $env:VAJRA_MODE }
Write-Host "Running real Vajra research (mode: $mode)..."
& vajra research $questionText --mode $mode
exit $LASTEXITCODE