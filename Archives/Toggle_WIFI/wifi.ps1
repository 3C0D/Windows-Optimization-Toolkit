$ethernet = Get-NetAdapter | Where-Object { $_.Name -like "*Ethernet*" -and $_.Status -eq "Up" }

if (-not $ethernet) {
    # Ethernet est débranché → désactiver la connexion Wi-Fi (mais garder le widget visible)
    netsh interface set interface name="Wi-Fi" admin=disable
}

