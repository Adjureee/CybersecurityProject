$python = "C:\Users\lozad\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Bundled Python was not found. Please install Python from python.org, then run:"
    Write-Host "python local_preview.py"
    pause
    exit
}

Write-Host ""
Write-Host "Starting Secure Registration and Login System..."
Write-Host "Open this link in your browser:"
Write-Host "http://127.0.0.1:5000"
Write-Host ""
Write-Host "Keep this window open while testing. Press Ctrl + C to stop the system."
Write-Host ""

& $python local_preview.py
