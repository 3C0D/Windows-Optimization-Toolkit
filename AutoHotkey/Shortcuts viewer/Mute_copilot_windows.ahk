; ============================================
; COPILOT MIC CONTROLLER - AutoHotkey v2
; ============================================
; Script pour contrôler automatiquement le micro de Copilot
; quand la reconnaissance vocale Windows (Win+H) est activée

#Requires AutoHotkey v2.0
#SingleInstance Force
#NoTrayIcon

; Variables globales
global copilotMuted := false
global voiceRecognitionActive := false
global copilotWindow := 0
global monitoring := true

; Configuration
global copilotTitles := ["Copilot", "Microsoft Copilot", "Bing Chat", "Copilot avec Bing"]
global copilotProcesses := ["msedge.exe", "Copilot.exe", "CopilotApp.exe"]

; ============================================
; FONCTIONS PRINCIPALES
; ============================================

; Trouve la fenêtre Copilot
FindCopilotWindow() {
    global copilotWindow, copilotTitles
    
    ; Recherche par titre de fenêtre
    for title in copilotTitles {
        try {
            if WinExist(title) {
                copilotWindow := WinGetID(title)
                DisplayStatus("✓ Fenêtre Copilot trouvée: " . title)
                return true
            }
        }
    }
    
    ; Recherche partielle dans toutes les fenêtres
    windows := WinGetList()
    for hwnd in windows {
        try {
            winTitle := WinGetTitle(hwnd)
            for title in copilotTitles {
                if InStr(winTitle, title) {
                    copilotWindow := hwnd
                    DisplayStatus("✓ Fenêtre Copilot trouvée: " . winTitle)
                    return true
                }
            }
        }
    }
    
    DisplayStatus("✗ Fenêtre Copilot non trouvée")
    return false
}

; Trouve les coordonnées du bouton micro
FindMicButton() {
    global copilotWindow
    
    if !copilotWindow {
        return false
    }
    
    try {
        ; Activer la fenêtre Copilot
        WinActivate(copilotWindow)
        Sleep(500)
        
        ; Obtenir les dimensions de la fenêtre
        WinGetPos(&x, &y, &width, &height, copilotWindow)
        
        ; Position typique du bouton micro dans Copilot
        ; (généralement en bas à droite de la zone de saisie)
        micX := x + width - 100  ; 100 pixels depuis la droite
        micY := y + height - 75  ; 75 pixels depuis le bas
        
        return {x: micX, y: micY}
    } catch {
        return false
    }
}

; Active/désactive le micro dans Copilot
ToggleCopilotMic() {
    global copilotMuted, copilotWindow
    
    DisplayStatus("`n🎯 Tentative de contrôle du micro Copilot...")
    
    ; Trouver la fenêtre Copilot
    if !FindCopilotWindow() {
        DisplayStatus("✗ Impossible de trouver Copilot")
        return false
    }
    
    ; Localiser le bouton micro
    micCoords := FindMicButton()
    if !micCoords {
        DisplayStatus("✗ Impossible de localiser le bouton micro")
        return false
    }
    
    try {
        ; Sauvegarder la position actuelle de la souris
        MouseGetPos(&originalX, &originalY)
        
        ; Activer la fenêtre Copilot
        WinActivate(copilotWindow)
        Sleep(200)
        
        ; Cliquer sur le bouton micro
        Click(micCoords.x, micCoords.y)
        
        ; Restaurer la position de la souris
        MouseMove(originalX, originalY, 0)
        
        ; Mettre à jour l'état
        copilotMuted := !copilotMuted
        status := copilotMuted ? "🔇 COUPÉ" : "🔊 ACTIVÉ"
        DisplayStatus("✓ Micro Copilot " . status)
        
        return true
    } catch as e {
        DisplayStatus("✗ Erreur lors du clic: " . e.Message)
        return false
    }
}

; ============================================
; GESTIONNAIRES D'ÉVÉNEMENTS
; ============================================

; Quand Win+H est pressé
OnWinHPressed(*) {
    global voiceRecognitionActive, copilotMuted
    
    DisplayStatus("`n🎤 Win+H détecté - Reconnaissance vocale Windows activée")
    voiceRecognitionActive := true
    
    ; Couper le micro de Copilot s'il n'est pas déjà coupé
    if !copilotMuted {
        ToggleCopilotMic()
    }
}

; Quand Escape est pressé
OnEscapePressed(*) {
    global voiceRecognitionActive, copilotMuted
    
    if voiceRecognitionActive && copilotMuted {
        DisplayStatus("`n🔄 Réactivation du micro Copilot...")
        ToggleCopilotMic()
        voiceRecognitionActive := false
    }
}

; Quand Ctrl+Q est pressé
OnCtrlQPressed(*) {
    global monitoring, copilotMuted
    
    DisplayStatus("`n🛑 Arrêt du script...")
    monitoring := false
    
    ; Réactiver le micro si nécessaire
    if copilotMuted {
        ToggleCopilotMic()
    }
    
    ExitApp()
}

; ============================================
; FONCTIONS UTILITAIRES
; ============================================

; Affiche un message dans la console (OutputDebug) et optionnellement dans une tooltip
DisplayStatus(msg) {
    OutputDebug(msg . "`n")
    
    ; Afficher aussi dans une tooltip temporaire
    ToolTip(msg)
    SetTimer(() => ToolTip(), -3000)  ; Effacer après 3 secondes
}

; Affiche le message de bienvenue
ShowWelcomeDialog() {
    welcome := "
    (
    ============================================================
    🎯 SCRIPT DE CONTRÔLE DU MICRO COPILOT - AHK v2
    ============================================================
    
    ⚡ Ce script coupe automatiquement le micro de Copilot
       quand vous activez la reconnaissance vocale Windows (Win+H)
    
    📌 Raccourcis clavier:
       • Win+H   : Active la reconnaissance vocale et coupe le micro Copilot
       • Escape  : Réactive le micro Copilot
       • Ctrl+Q  : Quitte le script
    
    ⚠️  Assurez-vous que Copilot est ouvert dans Edge ou l'app Windows
    ============================================================
    )"
    
    MsgBox(welcome, "Copilot Mic Controller", "Icon!")
}

; Test initial de connexion à Copilot
TestCopilotConnection() {
    DisplayStatus("`n🔍 Recherche de Copilot...")
    
    if FindCopilotWindow() {
        DisplayStatus("✅ Prêt à contrôler le micro de Copilot!")
        
        ; Afficher une notification système
        TrayTip("Copilot Mic Controller", "✅ Connecté à Copilot`nAppuyez sur Win+H pour commencer", 1)
    } else {
        DisplayStatus("⚠️  Copilot non détecté, ouvrez-le et le script le détectera automatiquement")
        
        ; Afficher une notification système
        TrayTip("Copilot Mic Controller", "⚠️ Copilot non détecté`nOuvrez Copilot et appuyez sur Win+H", 2)
    }
}

; ============================================
; CONFIGURATION DES HOTKEYS
; ============================================

; Win+H pour la reconnaissance vocale
#h::OnWinHPressed()

; Escape pour réactiver le micro
Escape::OnEscapePressed()

; Ctrl+Q pour quitter
^q::OnCtrlQPressed()

; ============================================
; SCRIPT PRINCIPAL
; ============================================

; Activer l'icône dans la barre système
TraySetIcon("Shell32.dll", 277)  ; Icône de microphone
A_IconTip := "Copilot Mic Controller - Win+H pour activer"

; Afficher le message de bienvenue
ShowWelcomeDialog()

; Tester la connexion initiale
TestCopilotConnection()

; Message de démarrage
DisplayStatus("`n🚀 Surveillance du clavier activée...")
DisplayStatus("📌 Le script est prêt et attend vos commandes")

; Le script reste actif et attend les hotkeys
; (AutoHotkey gère automatiquement la boucle d'événements)
