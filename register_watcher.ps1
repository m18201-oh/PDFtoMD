$AppName = "PDFtoMD_Watcher"
$PythonExe = "C:\Code\PDFtoMD\.venv\Scripts\python.exe"
$WatcherScript = "C:\Code\PDFtoMD\watcher.py"
$WorkingDir = "C:\Code\PDFtoMD"
$RunKeyPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not (Test-Path $WatcherScript)) {
    throw "Watcher script not found: $WatcherScript"
}

$Command = "`"$PythonExe`" `"$WatcherScript`""

New-Item -Path $RunKeyPath -Force | Out-Null
Set-ItemProperty -Path $RunKeyPath -Name $AppName -Value $Command

Write-Host "Successfully registered $AppName in HKCU Run for logon startup." -ForegroundColor Green
Write-Host "Command: $Command" -ForegroundColor DarkGray
