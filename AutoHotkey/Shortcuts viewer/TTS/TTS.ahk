#Requires AutoHotkey v2.0

InitializeVoices() {
    ; Chemin de registre source pour les voix
    sourcePath := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"

    ; Chemins de registre de destination
    destinationPaths := [
    "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens",
    "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\SPEECH\Voices\Tokens"
    ]

    ; Copie des voix du chemin source vers les chemins de destination
    try {
        for destPath in destinationPaths {
            Loop Reg, sourcePath, "K"
            {
                sourceKey := A_LoopRegKey . "" . A_LoopRegName
                destKey := destPath . "" . A_LoopRegName
                ; Crée la clé de destination si elle n'existe pas
                if !RegRead(destKey)
                    RegCreateKey(destKey)

                ; Copie les valeurs
                Loop Reg, sourceKey, "V"
                {
                    RegWrite(RegRead(sourceKey, A_LoopRegName), "REG_SZ", destKey, A_LoopRegName)
                }
            }
        } 
        MsgBox "Copie des voix terminée avec succès." 
    } catch as err {
        ; MsgBox "Erreur lors de la copie des voix : " . err.Message
    } 
}

InitializeVoices()

; Variables globales
global isReading := false
global voice := ComObject("SAPI.SpVoice")

; Définit le raccourci Windows+Y pour l'autodétection
#y:: ReadText("AUTO")

ReadText(language) {
    global isReading, voice

    if (voice.Status.RunningState == 2) {
        voice.Speak("", 3) ; Arrête la lecture en cours
        isReading := false
        return
    }

    if (isReading) {
        isReading := false
    }

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

    SelectedText := IgnoreCharacters(SelectedText)

    try {
        SetVoiceLanguage(language, SelectedText)
        voice.Rate := 2

        isReading := true
        voice.Speak(SelectedText, 1) ; Lecture asynchrone
    } catch as err {
        MsgBox "Erreur lors de l'utilisation de la synthèse vocale: " . err.Message
        isReading := false
    }

    A_Clipboard := OldClipboard
}

SetVoiceLanguage(language, text := "") {
    if (language == "AUTO") {
        language := DetectLanguage(text)
    }

    ; Utiliser les noms exacts des voix disponibles
    if (language == "EN") {
        voiceName := "Microsoft Mark"
    } else if (language == "FR") {
        voiceName := "Microsoft Paul" ; Modifiez ceci pour utiliser une autre voix, si disponible
    } else {
        MsgBox "Langue non supportée : " . language
        return
    }

    for v in ComObject("SAPI.SpVoice").GetVoices() {
        if (v.GetAttribute("Name") == voiceName) {
            voice.Voice := v
            return
        }
    }

    MsgBox "Voix pour la langue " . language . " non trouvée. Utilisation de la voix par défaut."
}

DetectLanguage(text) {
    ; Détection de la langue basée sur des mots courants
    frenchWords := ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "donc", "or", "ni", "car", "que", "qui", "quoi", "dont", "où", "à", "au", "avec", "pour", "sur", "dans", "par", "ce", "cette", "ces"]
    englishWords := ["the", "and", "or", "but", "so", "yet", "for", "nor", "that", "which", "who", "whom", "whose", "when", "where", "why", "how", "a", "an", "in", "on", "at", "with", "by", "this", "these", "those", "is"]

    frenchScore := 0
    englishScore := 0

    words := StrSplit(text, " ")
    for word in words {
        if (HasVal(frenchWords, word))
            frenchScore++
        if (HasVal(englishWords, word))
            englishScore++
    }

    if (englishScore > frenchScore) {
        return "EN"
    } else if (frenchScore > englishScore) {
        return "FR"
    } else {
        return "FR" ; Par défaut, considère le français
    }
}

HasVal(haystack, needle) {
    for index, value in haystack
        if (value = needle)
        return true
    return false
}

IgnoreCharacters(text) {
    charactersToIgnore := ["*", "#", "@"]
    for char in charactersToIgnore {
        text := StrReplace(text, char, "")
    }
    return text
}
