#Requires AutoHotkey v2.0

; Open text in AI chat (Win+Shift+I)
#+i:: openInAI()

; Open any link in browser (Win+Shift+O)
#+o:: openInBrowser()

openInAI() {
    ; Create AI menu
    aiMenu := Menu()
    aiMenu.Add("DeepSeek", (*) => Run("https://chat.deepseek.com/a/chat"))
    aiMenu.Add("Claude", (*) => Run("https://claude.ai"))
    aiMenu.Add("ChatGPT", (*) => Run("https://chatgpt.com/"))
    aiMenu.Add("Grok", (*) => Run("https://x.com/i/grok"))
    
    ; Show menu at cursor position
    aiMenu.Show()
}

openInBrowser() {
    OldClipboard := A_Clipboard
    A_Clipboard := ""

    Send "^c" ; Copy the selected text
    if !ClipWait(0.5) {
        ; If no selection, restore the clipboard and use it
        if (OldClipboard != "") {
            SelectedText := OldClipboard
            A_Clipboard := OldClipboard
        } else {
            MsgBox "No text selected or in the clipboard"
            return
        }
    } else {
        ; Use the selected text
        SelectedText := A_Clipboard
    }

    if (SelectedText != "") {
        ; Add https:// if not present
        if !RegExMatch(SelectedText, "^(https?://|www\.)")
            SelectedText := "https://" . SelectedText
            
        Run(SelectedText)
    }
    A_Clipboard := OldClipboard
}