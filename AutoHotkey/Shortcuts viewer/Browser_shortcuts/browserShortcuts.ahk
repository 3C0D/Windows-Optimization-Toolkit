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
    aiMenu.Add("Claude", (*) => Run("https://claude.ai"))
    aiMenu.Add("Google AI", (*) => Run("https://aistudio.google.com/prompts/new_chat"))
    aiMenu.Add("ChatGPT", (*) => Run("https://chatgpt.com/"))
    aiMenu.Add("Grok", (*) => Run("https://x.com/i/grok"))
    aiMenu.Add("Perplexity", (*) => Run("https://www.perplexity.ai/"))
    aiMenu.Add("Genspark", (*) => Run("https://www.genspark.ai/"))
    aiMenu.Add("Mistral", (*) => Run("https://chat.mistral.ai/chat"))
    aiMenu.Add("DeepSeek", (*) => Run("https://chat.deepseek.com/a/chat"))
    aiMenu.Add("Qwen", (*) => Run("https://chat.qwenlm.ai/"))
    aiMenu.Add("Gemini", (*) => Run("https://gemini.google.com/app"))
    aiMenu.Add("Cici", (*) => Run("https://www.cici.com/chat/?from_logout=1"))
    ; aiMenu.Add("Liner", (*) => Run("https://getliner.com/"))
    aiMenu.Add("Manus", (*) => Run("https://manus.im/app"))
    aiMenu.Add("Nexus Mind", (*) => Run("https://www.nexusmind.tech/home"))
    aiMenu.Add("Maya", (*) => Run("https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice#demo"))
    aiMenu.Add("Unmute", (*) => Run("https://unmute.sh/"))
    aiMenu.Add("Consensus", (*) => Run("https://consensus.app/search/"))
    ; aiMenu.Add("Storm", (*) => Run("https://storm.genie.stanford.edu/"))

    
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
            Run("https://www.google.com/search?q=" . UrlEncode(SelectedText)) ; Use UrlEncode here too
    }
}

; Function to translate selected text using Google Search + "trad"
translateText() {
    SelectedText := getSelectedOrClipboardText()
    if (SelectedText != "") {
        ; Encode the text for the URL
        EncodedText := UrlEncode(SelectedText)
        
        ; Construct the Google Search URL with " trad" appended
        TranslateUrl := "https://www.google.com/search?q=" . EncodedText . "+trad"

        ; Open the URL in the default browser
        Run TranslateUrl
    }
}

; Function to encode the URL (moved from translateInBrowser.ahk)
UrlEncode(str) {
    static chars := "0123456789ABCDEF"
    encodedStr := ""
    for i, char in StrSplit(str) {
        if char ~= "[a-zA-Z0-9-_.~]"
            encodedStr .= char
        else {
            code := Ord(char)
            encodedStr .= "%" . SubStr(chars, (code >> 4) + 1, 1) . SubStr(chars, (code & 15) + 1, 1)
        }
    }
    return encodedStr
}

; Hotkey definitions
#+i:: openInAI()
#+u:: openUrlOrSearch()
#+t:: translateText() ; Added hotkey for translation