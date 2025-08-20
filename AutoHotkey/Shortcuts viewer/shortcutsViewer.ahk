#Requires AutoHotkey v2.0
; AutoHotkey v2 Script - Shortcuts Viewer with Sleep Control
; https://github.com/TheArkive/JXON_ahk2
#Include JXON.ahk
#Include Browser_shortcuts/browserShortcuts.ahk
#Include Mute_micro.ahk
; #Include Mute_copilot_windows.ahk
; #Include OCR_trad.ahk

; Global variables for sleep control
sleepDisabled := false

; Chemin vers le fichier JSON
filePath := A_ScriptDir "\shortcuts.json"

; Raccourci pour ouvrir l'interface (Win+Shift+/)
#+/:: ShowShortcutsGUI()

; Sleep control shortcut (Shift+Win+V)
+#v:: ToggleSleepMode()

; Inclure les raccourcis personnels

ShowShortcutsGUI() {
    global filePath

    if !FileExist(filePath)
        FileAppend('{"General": ""}', filePath, "UTF-8")

    jsonText := FileRead(filePath, "UTF-8")
    data := jxon_load(&jsonText)

    ; Utiliser une valeur par défaut vide si "General" n'est pas trouvé
    displayText := data.Has("General") ? data["General"] : ""

    ShortcutsGUI := Gui()
    ShortcutsGUI.Opt("+AlwaysOnTop")
    ShortcutsGUI.BackColor := "1A1A1A"
    ShortcutsGUI.Title := "Shortcut Viewer 1.0"

    ShortcutsGUI.SetFont("s14 c916c35", "Segoe UI")
    ShortcutsGUI.Add("Text", "w600", "Mes raccourcis :")

    ShortcutsGUI.SetFont("s12 cC0C0C0", "Consolas")
    edit := ShortcutsGUI.Add("Edit", "r30 w590 vShortcutsEdit", displayText)
    edit.Opt("+Background2A2A2A")

    ShortcutsGUI.SetFont("s10 cC0C0C0", "Segoe UI")
    closeButton := ShortcutsGUI.Add("Button", "w100", "Fermer")
    closeButton.OnEvent("Click", (*) => SaveAndClose(ShortcutsGUI))

    ShortcutsGUI.OnEvent("Close", (*) => SaveAndClose(ShortcutsGUI))
    ShortcutsGUI.OnEvent("Escape", (*) => SaveAndClose(ShortcutsGUI))

    ShortcutsGUI.Show()
    closeButton.Focus()
}

SaveAndClose(ShortcutsGUI) {
    global filePath
    newContent := ShortcutsGUI["ShortcutsEdit"].Value

    data := Map()
    data["General"] := newContent

    jsonText := jxon_dump(data, 2)  ; Indentation de 2 espaces pour une meilleure lisibilité

    try {
        ; Ouvrir le fichier en mode écriture pour remplacer son contenu
        file := FileOpen(filePath, "w", "UTF-8")
        if !IsObject(file) {
            ; Utiliser Error() pour générer une exception
            Error("Erreur lors de l'ouverture du fichier pour l'écriture.")
        }
        file.Write(jsonText)
        file.Close()
    } catch as err {
        MsgBox("Erreur lors de l'enregistrement du fichier : " . err.Message)
    }
    ShortcutsGUI.Destroy()
}

; Sleep control function
ToggleSleepMode() {
    global sleepDisabled

    if (!sleepDisabled) {
        ; Disable sleep mode
        DllCall("kernel32.dll\SetThreadExecutionState", "UInt", 0x80000003) ; ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        sleepDisabled := true
        ShowMessage("Mode veille DÉSACTIVÉ", "Votre PC ne rentrera pas en mode veille")
    } else {
        ; Re-enable sleep mode
        DllCall("kernel32.dll\SetThreadExecutionState", "UInt", 0x80000000) ; ES_CONTINUOUS only to reset
        sleepDisabled := false
        ShowMessage("Mode veille ACTIVÉ", "Votre PC peut maintenant rentrer en mode veille normalement")
    }
}

; Function to show status message
global msgGui := 0

ShowMessage(title, message) {
    global msgGui
    if msgGui {
        msgGui.Destroy()
    }
    msgGui := Gui()
    msgGui.Opt("+AlwaysOnTop +Owner +Border")
    msgGui.Title := title
    msgGui.SetFont("s13 bold", "Segoe UI")
    msgGui.MarginX := 30
    msgGui.MarginY := 20
    msgGui.BackColor := "F8F8F8"
    msgGui.Add("Text", "w380 r3 Center", message)
    btn := msgGui.Add("Button", "w120 h35 Center", "OK")
    btn.SetFont("s12 bold", "Segoe UI")
    btn.OnEvent("Click", (*) => (msgGui.Destroy(), msgGui := 0))
    msgGui.OnEvent("Escape", (*) => (msgGui.Destroy(), msgGui := 0))
    msgGui.Show("w420 h150")
    btn.Focus()
    ; Fermeture automatique après 4 secondes
    SetTimer((*) => (msgGui ? (msgGui.Destroy(), msgGui := 0) : msgGui := 0), -4000)
}

; Clean exit function to restore normal sleep settings
OnExit(ExitFunc)

ExitFunc(ExitReason, ExitCode) {
    global sleepDisabled
    ; Ensure normal settings are restored before exit
    if (sleepDisabled) {
        DllCall("kernel32.dll\SetThreadExecutionState", "UInt", 0x80000000)
    }
}
