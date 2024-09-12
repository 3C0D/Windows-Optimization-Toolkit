#+g:: searchGoogle()

searchGoogle() {
    OldClipboard := A_Clipboard
    A_Clipboard := ""

    Send "^c" ; Copy the selected text
    if !ClipWait(0.5) {
        ; If no selection, restore the clipboard and use it for translation
        if (OldClipboard != "") {
            SelectedText := OldClipboard
            A_Clipboard := OldClipboard
        } else {
            MsgBox "No text selected or in the clipboard"
            return
        }
    } else {
        ; Use the selected text for translation
        SelectedText := A_Clipboard
    }

    if (SelectedText != "")
        Run("https://www.google.com/search?q=" SelectedText)
    else
        MsgBox("Aucune sélection active trouvée pour la recherche.")
    A_Clipboard := OldClipboard 
}

