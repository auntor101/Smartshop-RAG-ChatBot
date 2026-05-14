# ShopSmart BD — run Streamlit locally (Windows-friendly).
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$env:TQDM_DISABLE = "1"
$env:HF_HUB_DISABLE_PROGRESS_BARS = "1"
$env:TOKENIZERS_PARALLELISM = "false"

if (-not (Test-Path (Join-Path $RepoRoot ".env"))) {
    Copy-Item (Join-Path $RepoRoot ".env.example") (Join-Path $RepoRoot ".env")
    Write-Host "Created .env from .env.example — set GROQ_API_KEY (or change LLM_PROVIDER)." -ForegroundColor Yellow
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
python -m pip install -r (Join-Path $RepoRoot "requirements.txt") -q

Write-Host "Starting Streamlit at http://localhost:8501 ..." -ForegroundColor Green
# Blank line skips Streamlit first-run email prompt when stdin is not a TTY.
cmd /c "echo.| python -m streamlit run app.py"
