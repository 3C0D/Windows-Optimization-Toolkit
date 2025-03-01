#Requires AutoHotkey v2.0

; Helper function for clipboard operations
getSelectedOrClipboardText() {
    OldClipboard := A_Clipboard
    A_Clipboard := ""

    Send "^c" ; Copy the selected text
    if !ClipWait(0.5) {
        ; If no selection, restore the clipboard and use it
        if (OldClipboard != "") {
            text := OldClipboard
            A_Clipboard := OldClipboard
            return text
        } else {
            MsgBox "No text selected or in the clipboard"
            return ""
        }
    } else {
        ; Use the selected text
        text := A_Clipboard
        A_Clipboard := OldClipboard
        return text
    }
}

; openInAI remains unchanged as it doesn't use clipboard
openInAI() {
    aiMenu := Menu()
    aiMenu.Add("DeepSeek", (*) => Run("https://chat.deepseek.com/a/chat"))
    aiMenu.Add("Claude", (*) => Run("https://claude.ai"))
    aiMenu.Add("ChatGPT", (*) => Run("https://chatgpt.com/"))
    aiMenu.Add("Grok", (*) => Run("https://x.com/i/grok"))
    aiMenu.Add("Perplexity", (*) => Run("https://www.perplexity.ai/"))
    aiMenu.Add("Qwen", (*) => Run("https://chat.qwenlm.ai/"))
    aiMenu.Add("Nexus Mind", (*) => Run("https://www.nexusmind.tech/home"))
    aiMenu.Add("Google AI", (*) => Run("https://aistudio.google.com/prompts/new_chat"))
    
    aiMenu.Show()
}

; Universal URL/Search handler
openUrlOrSearch() {
    SelectedText := getSelectedOrClipboardText()
    if (SelectedText != "") {
        ; If it looks like a URL, open directly, otherwise search
        if RegExMatch(SelectedText, "^(https?://|www\.)")
            Run(SelectedText)
        else
            Run("https://www.google.com/search?q=" SelectedText)
    }
}

; Hotkey definitions
#+i:: openInAI()
#+u:: openUrlOrSearch()