# Invokes Hermes to verify recent changes against AGENTS.md rules and acceptance tests
param(
    [string]$Milestone = "current"
)

$hermesPython = "C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$hermesAgent = "C:\Users\user\AppData\Local\hermes\hermes-agent"

if (-not (Test-Path $hermesPython)) {
    Write-Error "Hermes Python interpreter not found."
    exit 1
}

# Safely check if HEAD exists
$hasHead = git rev-parse --verify HEAD 2>$null
if ($hasHead) {
    $diff = git diff HEAD
} else {
    $diff = "(Initial repository state before first commit)"
}
$status = git status --short

$prompt = @"
You are acting as the Verifier for Malaysian Thesis Institution System (MTIS).
Review the following git status and diff for milestone '$Milestone'.
Verify that:
1. No secrets or .env files are staged or committed.
2. Acceptance tests have not been weakened or deleted.
3. blueprint.json is untouched.
4. Tenant isolation is respected.
Provide a concise verifier verdict: PASS or FAIL with reasons.

Git Status:
$status

Git Diff:
$diff
"@

$promptFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($promptFile, $prompt, [System.Text.Encoding]::UTF8)

try {
    & $hermesPython -c "import sys; sys.path.insert(0, r'$hermesAgent'); from hermes_cli.main import main; p = open(r'$promptFile', encoding='utf-8').read(); sys.argv=['hermes', '-z', p]; main()"
} finally {
    if (Test-Path $promptFile) {
        Remove-Item $promptFile -Force -ErrorAction SilentlyContinue
    }
}
