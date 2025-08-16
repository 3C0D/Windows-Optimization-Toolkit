; AutoHotkey V2 - Toggle Copilot rapidement
; Appuyez sur Ctrl+Alt+C pour basculer

^!c:: {
    ; Méthode 1 : Utiliser le raccourci Windows natif
    Send("#{c}")  ; Win+C pour ouvrir/fermer Copilot
}

; Alternative - Désactiver/activer via registre (plus radical)
^!x:: {
    ; Toggle registry value
    try {
        currentValue := RegRead("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "DisableCopilot", 0)
        newValue := currentValue ? 0 : 1
        RegWrite(newValue, "REG_DWORD", "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "DisableCopilot")
        
        ; Redémarrer explorer pour appliquer
        Run("taskkill /f /im explorer.exe && start explorer.exe", , "Hide")
        
        if (newValue) {
            ToolTip("Copilot DÉSACTIVÉ - Redémarrage d'Explorer...")
        } else {
            ToolTip("Copilot ACTIVÉ - Redémarrage d'Explorer...")
        }
        SetTimer(() => ToolTip(), -2000)
    }
}

; Tuer le processus Copilot s'il traîne
^!k:: {
    RunWait("taskkill /f /im Copilot.exe /t", , "Hide")
    RunWait("taskkill /f /im Microsoft.Copilot.exe /t", , "Hide")
    ToolTip("Processus Copilot tués")
    SetTimer(() => ToolTip(), -1000)
}