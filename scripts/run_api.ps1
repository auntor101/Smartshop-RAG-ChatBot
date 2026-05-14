# ShopSmart BD — run FastAPI locally.
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$env:TQDM_DISABLE = "1"
$env:HF_HUB_DISABLE_PROGRESS_BARS = "1"
$env:TOKENIZERS_PARALLELISM = "false"

if (-not (Test-Path (Join-Path $RepoRoot ".env"))) {
    Copy-Item (Join-Path $RepoRoot ".env.example") (Join-Path $RepoRoot ".env")
    Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
python -m pip install -r (Join-Path $RepoRoot "requirements.txt") -q

Write-Host "API docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
