#Requires AutoHotkey v2.0

InitializeVoices() {
    ; Skip voice copying if we don't have admin rights
    if !A_IsAdmin {
        ; MsgBox "Running without admin rights - skipping voice copying"
        return
    }

    ; Registry source path for voices
    sourcePath := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"

    ; Registry destination paths
    destinationPaths := [
        "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens",
        "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\SPEECH\Voices\Tokens"
    ]

    ; Copy voices from source path to destination paths
    try {
        for destPath in destinationPaths {
            loop reg, sourcePath, "K" {
                sourceKey := A_LoopRegKey "\" A_LoopRegName
                destKey := destPath "\" A_LoopRegName
                ; Create destination key if it doesn't exist
                if !RegRead(destKey)
                    RegCreateKey(destKey)

                ; Copy values
                loop reg, sourceKey, "V" {
                    RegWrite(RegRead(sourceKey, A_LoopRegName), "REG_SZ", destKey, A_LoopRegName)
                }
            }
        }
        MsgBox "Voice copying completed successfully."
    } catch as err {
        MsgBox "Error while copying voices: " . err.Message
    }
}

; ; Check if script is running as admin and if not, try to elevate
; if !A_IsAdmin {
;     try {
;         if A_IsCompiled
;             Run '*RunAs "' A_ScriptFullPath '" /restart'
;         else
;             Run '*RunAs "' A_AhkPath '" /restart "' A_ScriptFullPath '"'
;     }
; }

; Activez si les voix ne sont pas trouvées.
; InitializeVoices()

; Global variables
global state := {
    isReading: false,
    isPaused: false,
    speed: 2.0,  ; Vitesse pour l'affichage
    internalRate: 2  ; Vitesse entière pour SAPI
}
global voice := ComObject("SAPI.SpVoice")

; Gestion des hotkeys
UpdateHotkeys(enable := true) {
    if (enable) {
        Hotkey "NumpadAdd", "On"
        Hotkey "NumpadSub", "On"
    } else {
        Hotkey "NumpadAdd", "Off"
        Hotkey "NumpadSub", "Off"
    }
}

; Initialisation des hotkeys
Hotkey "NumpadAdd", AdjustSpeedUp
Hotkey "NumpadSub", AdjustSpeedDown
; Désactiver les hotkeys au démarrage
UpdateHotkeys(false)

; play/stop
#y:: ReadText("AUTO")

; pause/resume
#!y:: TogglePause()

AdjustSpeedUp(*) {
    AdjustSpeed(0.5)
}

AdjustSpeedDown(*) {
    AdjustSpeed(-0.5)
}

ReadText(language) {
    if (voice.Status.RunningState == 2 || state.isPaused) {
        StopReading()
        return
    }

    ResetState()

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
        voice.Rate := state.internalRate  ; Utilise la vitesse entière

        state.isReading := true
        ; Activer les hotkeys quand la lecture commence
        UpdateHotkeys(true)
        voice.Speak(SelectedText, 1) ; Asynchronous reading

        ; Surveiller l'état de la lecture
        SetTimer(CheckReadingStatus, 100)
    } catch as err {
        MsgBox "Error while using text-to-speech: " . err.Message
        ResetState()
    } finally {
        A_Clipboard := OldClipboard
    }
}

CheckReadingStatus() {
    if (voice.Status.RunningState == 1) { ; Si la lecture est terminée
        StopReading()
        SetTimer(CheckReadingStatus, 0) ; Arrêter le timer
    }
}

AdjustSpeed(delta) {
    if (!state.isReading)
        return

    ; Met à jour la vitesse pour l'affichage
    state.speed := Max(Min(state.speed + delta, 10), -10)
    state.speed := Round(state.speed, 1)

    ; Convertit en entier pour SAPI
    state.internalRate := Round(state.speed)
    voice.Rate := state.internalRate 

    ; Affiche la fenêtre de vitesse
    ShowSpeedWindow()
}

ShowSpeedWindow() {
    static speedGui := false

    ; Si une fenêtre existe déjà, la détruire
    if (speedGui) {
        speedGui.Destroy()
    }

    ; Créer une nouvelle fenêtre
    speedGui := Gui("+AlwaysOnTop -Caption +ToolWindow")
    speedGui.SetFont("s12", "Arial")
    speedGui.Add("Text", , "Vitesse: " . Format("{:.1f}", state.speed))
    ; Positionner la fenêtre
    screenWidth := A_ScreenWidth
    screenHeight := A_ScreenHeight
    guiWidth := 150
    guiHeight := 40
    xPos := (screenWidth - guiWidth) / 2
    yPos := screenHeight - 100

    speedGui.Show("x" . xPos . " y" . yPos . " w" . guiWidth . " h" . guiHeight)

    ; Fermer la fenêtre après 2 secondes
    SetTimer () => speedGui.Destroy(), -2000
}

TogglePause() {
    if (!state.isReading) {
        return
    }

    if (!state.isPaused) {
        voice.Pause()
        state.isPaused := true
    } else {
        voice.Resume()
        state.isPaused := false
    }
}

ResetState() {
    state.isReading := false
    state.isPaused := false
    ; Désactiver les hotkeys quand on réinitialise l'état
    UpdateHotkeys(false)
}

StopReading() {
    if (state.isPaused) {
        voice.Resume()  ; Resume before stopping to ensure proper state
        state.isPaused := false
    }
    voice.Speak("", 3)  ; Stop current reading
    ResetState()
}

SetVoiceLanguage(language, text := "") {
    if (language == "AUTO") {
        language := DetectLanguage(text)
    }

    if (language == "EN") {
        voiceName := "Microsoft Mark"
    } else if (language == "FR") {
        voiceName := "Microsoft Paul"
    } else {
        MsgBox "Unsupported language: " . language
        return
    }

    for v in voice.GetVoices() {
        if (v.GetAttribute("Name") == voiceName) {
            voice.Voice := v
            return
        }
    }

    MsgBox "Voice for language " . language . " not found. Using default voice."
}

DetectLanguage(text) {
    ; Language detection based on common words
    frenchWords := ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "donc", "or", "ni", "car", "que", "qui",
        "quoi", "dont", "où", "à", "au", "avec", "pour", "sur", "dans", "par", "ce", "cette", "ces"
    ]
    englishWords := ["the", "and", "or", "but", "so", "yet", "for", "nor", "that", "which", "who", "whom", "whose",
        "when", "where", "why", "how", "a", "an", "in", "on", "at", "with", "by", "this", "these", "those", "is"
    ]

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
        return "FR" ; By default, consider French
    }
}

HasVal(haystack, needle) {
    for index, value in haystack
        if (value = needle)
            return true
    return false
}

IgnoreCharacters(text) {
    charactersToIgnore := ["*", "#", "@", "//"
    ]
    for char in charactersToIgnore {
        text := StrReplace(text, char, "")
    }
    return text
}