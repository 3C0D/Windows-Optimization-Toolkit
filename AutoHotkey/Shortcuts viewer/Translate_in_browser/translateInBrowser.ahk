#Requires AutoHotkey v2.0

#+t:: translate()

translate() {
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

    ; Encode the text for the URL
    EncodedText := UrlEncode(SelectedText)
    
    ; Construct the Google Translate URL (from English to French)
    TranslateUrl := "https://translate.google.com/?sl=en&tl=fr&text=" . EncodedText

    ; Open the URL in the default browser
    Run TranslateUrl

    A_Clipboard := OldClipboard
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
