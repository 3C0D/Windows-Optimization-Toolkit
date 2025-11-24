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

; Open AI services menu with categories
openInAI() {
    aiMenu := Menu()
    
    ; === ASSISTANTS GÉNÉRALISTES ===
    aiMenu.Add("Claude", (*) => Run("https://claude.ai"))
    aiMenu.Add("ChatGPT", (*) => Run("https://chatgpt.com/"))
    aiMenu.Add("Ernie", (*) => Run("https://ernie.baidu.com/"))
    aiMenu.Add("Gemini", (*) => Run("https://gemini.google.com/app"))
    aiMenu.Add("Copilot", (*) => Run("https://copilot.microsoft.com"))
    aiMenu.Add("Perplexity", (*) => Run("https://www.perplexity.ai/"))
    aiMenu.Add("Grok", (*) => Run("https://x.com/i/grok"))
    ; aiMenu.Add("Poe", (*) => Run("https://poe.com"))
    
    aiMenu.Add() ; Separator
    
    ; === ASSISTANTS SPÉCIALISÉS ===
    aiMenu.Add("Mistral", (*) => Run("https://chat.mistral.ai/chat"))
    aiMenu.Add("DeepSeek", (*) => Run("https://chat.deepseek.com/a/chat"))
    aiMenu.Add("Qwen", (*) => Run("https://chat.qwenlm.ai/"))
    aiMenu.Add("Kimi", (*) => Run("https://www.kimi.com/"))
    aiMenu.Add("GLM", (*) => Run("https://chat.z.ai/"))
    aiMenu.Add("Cici", (*) => Run("https://www.cici.com/chat/?from_logout=1"))
    
    aiMenu.Add() ; Separator
    
    ; === RECHERCHE & SYNTHÈSE ===
    aiMenu.Add("Genspark", (*) => Run("https://www.genspark.ai/"))
    aiMenu.Add("Consensus", (*) => Run("https://consensus.app/search/"))
    aiMenu.Add("You.com", (*) => Run("https://you.com"))
    
    aiMenu.Add() ; Separator
    
    ; === GÉNÉRATION D'IMAGES ===
    aiMenu.Add("DALL-E 3", (*) => Run("https://chatgpt.com/"))
    aiMenu.Add("Midjourney", (*) => Run("https://www.midjourney.com"))
    aiMenu.Add("Leonardo.ai", (*) => Run("https://leonardo.ai"))
    aiMenu.Add("Ideogram", (*) => Run("https://ideogram.ai"))
    aiMenu.Add("Firefly", (*) => Run("https://firefly.adobe.com"))
    
    aiMenu.Add() ; Separator
    
    ; === GÉNÉRATION VIDÉO ===
    aiMenu.Add("Runway", (*) => Run("https://runwayml.com"))
    aiMenu.Add("Pika", (*) => Run("https://pika.art"))
    aiMenu.Add("HeyGen", (*) => Run("https://www.heygen.com"))
    aiMenu.Add("Luma AI", (*) => Run("https://lumalabs.ai"))
    
    aiMenu.Add() ; Separator
    
    ; === VOIX & AUDIO ===
    aiMenu.Add("ElevenLabs", (*) => Run("https://elevenlabs.io"))
    aiMenu.Add("Unmute", (*) => Run("https://unmute.sh/"))
    aiMenu.Add("Maya", (*) => Run("https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice#demo"))
    
    aiMenu.Add() ; Separator
    
    ; === OUTILS SPÉCIALISÉS ===
    aiMenu.Add("Google AI Studio", (*) => Run("https://aistudio.google.com/prompts/new_chat"))
    aiMenu.Add("Cursor", (*) => Run("https://cursor.sh"))
    aiMenu.Add("Manus", (*) => Run("https://manus.im/app"))
    aiMenu.Add("Fragments", (*) => Run("https://fragments.e2b.dev/"))
    
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
            Run("https://www.google.com/search?q=" . UrlEncode(SelectedText))
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

; Function to encode the URL
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
#+t:: translateText()