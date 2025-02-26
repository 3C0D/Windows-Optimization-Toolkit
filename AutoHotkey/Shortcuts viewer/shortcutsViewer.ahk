#Requires AutoHotkey v2.0
;https://github.com/TheArkive/JXON_ahk2
#Include JXON.ahk
#Include Personal_shortcuts/personalShortcuts.ahk
#Include Translate_in_browser/translateInBrowser.ahk
#Include TTS/TTS.ahk
#Include Browser_shortcuts/browserShortcuts.ahk

; Chemin vers le fichier JSON
filePath := A_ScriptDir "\shortcuts.json"

; Raccourci pour ouvrir l'interface (Win+Shift+/)
#+/:: ShowShortcutsGUI()

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
