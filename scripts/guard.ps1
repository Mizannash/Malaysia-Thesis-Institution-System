$expectedHash = "9bb22aa230cc3d9a5adf65fc44328631f20f795b29c485ac49212f325d747d85"
$currentHash = (Get-FileHash -Path "$PSScriptRoot\..\blueprint.json" -Algorithm SHA256).Hash.ToLower()

if ($currentHash -ne $expectedHash) {
    Write-Error "Guard failed: blueprint.json has been modified! Expected $expectedHash but got $currentHash."
    exit 1
}

# Verify all 11 acceptance test files exist
$acceptanceDir = "$PSScriptRoot\..\tests\acceptance"
$expectedTestFiles = @(
    "test_f1_auth.py",
    "test_f2_auth.py",
    "test_f3_topic_search.py",
    "test_f4_gap_analysis.py",
    "test_f5_title_suggestions.py",
    "test_f6_deep_dive_search.py",
    "test_f7_objectives_methodology.py",
    "test_f8_usage_quota.py",
    "test_f9_usage_quota.py",
    "test_f10_project_history.py",
    "test_quality.py"
)

foreach ($file in $expectedTestFiles) {
    if (-not (Test-Path "$acceptanceDir\$file")) {
        Write-Error "Guard failed: Acceptance test file $file is missing!"
        exit 1
    }
}

Write-Host "Guard passed: blueprint.json is untouched and all 11 acceptance test files are present." -ForegroundColor Green
exit 0
