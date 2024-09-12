$interfaceName = "Wi-Fi"

# Fonction pour vérifier si le script est exécuté en tant qu'administrateur
# function Test-Administrator {
#     $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
#     $currentPrincipal = New-Object Security.Principal.WindowsPrincipal($currentUser)
#     return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
# }

# Relancer le script avec des privilèges élevés si ce n'est pas le cas
# if (-not (Test-Administrator)) {
#     Write-Output "This script requires administrator privileges. Relaunching..."
#     Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
#     exit
# } else {
#     Write-Output "Script is running with administrator privileges."
# }

# Vérifier la connectivité Internet en pingant un site fiable
$pingResult = Test-Connection -ComputerName google.com -Count 1 -Quiet
Write-Output "Ping result: $pingResult"

# Gestion des adaptateurs réseau
$adapter = Get-NetAdapter -Name $interfaceName -ErrorAction SilentlyContinue

if ($null -eq $adapter) {
    Write-Output "No adapter found with the name $interfaceName"
    exit
}

# Vérifier le résultat du ping et activer/désactiver le Wi-Fi en conséquence
if ($pingResult) {
    Write-Output "Internet is connected. Disabling Wi-Fi..."
    try {
        Disable-NetAdapter -Name $interfaceName -Confirm:$false
        Write-Output "Wi-Fi is now disabled."
    } catch {
        Write-Output "Failed to disable Wi-Fi: $_"
    }
} else {
    Write-Output "Internet is not connected. Enabling Wi-Fi..."
    try {
        Enable-NetAdapter -Name $interfaceName -Confirm:$false
        Write-Output "Wi-Fi is now enabled. it takes at least 2s"
    } catch {
        Write-Output "Failed to enable Wi-Fi: $_"
    }
}

# Pause
