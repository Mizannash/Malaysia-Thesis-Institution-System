# Isolated test runner preventing PYTHONPATH leakage from other tools
$env:PYTHONPATH = ""
$env:PYTHONHOME = ""
$venvPython = "$PSScriptRoot\..\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment python not found at $venvPython"
    exit 1
}

& $venvPython -m pytest -q $args
exit $LASTEXITCODE
