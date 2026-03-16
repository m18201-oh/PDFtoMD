$TaskName = "PDFtoMD_Watcher"
$PythonExe = "C:\Code\PDFtoMD\.venv\Scripts\python.exe"
$WatcherScript = "C:\Code\PDFtoMD\watcher.py"
$WorkingDir = "C:\Code\PDFtoMD"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $WatcherScript -WorkingDirectory $WorkingDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 365)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host "Successfully registered $TaskName to run at Logon." -ForegroundColor Green
