#Requires AutoHotkey v2.0

voices := ComObject("SAPI.SpVoice").GetVoices()
voiceList := ""

for v in voices {
    voiceList .= v.GetAttribute("Name") . " (" . v.GetAttribute("Language") . ")`n"
}

MyGui := Gui()
MyGui.Opt("+Resize")
MyGui.Title := "Voix disponibles"

; Utilisation d'un contrôle Edit
MyGui.Add("Edit", "r10 w300 vSelectedVoice ReadOnly", voiceList)

; Ajout d'un bouton pour copier le texte sélectionné
CopyButton := MyGui.Add("Button", "w100", "Copier sélection")
CopyButton.OnEvent("Click", CopySelectedText)

MyGui.Add("Button", "Default w100", "Fermer").OnEvent("Click", (*) => MyGui.Destroy())

MyGui.OnEvent("Close", (*) => MyGui.Destroy())
MyGui.OnEvent("Escape", (*) => MyGui.Destroy())

MyGui.Show()

CopySelectedText(*)
{
    SelectedText := MyGui["SelectedVoice"].Text
    if (SelectedText != "") {
        A_Clipboard := SelectedText
        MsgBox("Texte copié dans le presse-papiers !")
    } else {
        MsgBox("Aucun texte sélectionné.")
    }
}
