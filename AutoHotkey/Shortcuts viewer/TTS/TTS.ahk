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

; Uncomment if voices are not found.
; InitializeVoices()

; Global variables
global state := {
    isReading: false,
    isPaused: false,
    speed: 2.0,  ; Speed for display
    internalRate: 2, ; Integer speed for SAPI
    currentText: ""   ; Current text being read
}

global voice := ComObject("SAPI.SpVoice")

; Manage hotkeys
UpdateHotkeys(enable := true) {
    if (enable) {
        Hotkey "NumpadAdd", "On"
        Hotkey "NumpadSub", "On"
    } else {
        Hotkey "NumpadAdd", "Off"
        Hotkey "NumpadSub", "Off"
    }
}

; Initialize hotkeys
Hotkey "NumpadAdd", AdjustSpeedUp
Hotkey "NumpadSub", AdjustSpeedDown
; Disable hotkeys at start
UpdateHotkeys(false)

; play/stop
#y:: ReadText("AUTO")

; Function to jump to the next line
#^y:: {
    ; Do nothing if reading is stopped or paused
    if (!state.isReading || state.isPaused)
        return

    ; Get the currently reading text
    text := state.currentText

    ; Get the current position in the text
    currentPos := voice.Status.InputWordPosition

    ; Search for the next line after the current position
    nextPos := -1
    nextPos := InStr(text, "`n", true, currentPos + 1)

    ; If a valid position is found
    if (nextPos > 0) {
        ; Stop the current reading
        voice.Speak("", 3)  ; 3 = SVSFPurgeBeforeSpeak (stops immediately)

        ; Extract remaining text starting just after the line break
        remainingText := SubStr(text, nextPos + 1)

        ; Remove any initial line breaks if present
        remainingText := RegExReplace(remainingText, "^[\r\n]+", "")

        ; Resume reading with the remaining text
        if (remainingText != "") {
            state.currentText := remainingText
            voice.Rate := state.internalRate
            voice.Speak(remainingText, 1)  ; 1 = SVSFlagsAsync (asynchronous reading)
        } else {
            StopReading()  ; If no more text, stop reading
        }
    }
}

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
            state.currentText := OldClipboard
            A_Clipboard := OldClipboard
        } else {
            MsgBox "No text selected or in the clipboard"
            return
        }
    } else {
        ; Use the selected text for translation
        state.currentText := A_Clipboard
    }

    state.currentText := IgnoreCharacters(state.currentText)

    try {
        SetVoiceLanguage(language, state.currentText)
        voice.Rate := state.internalRate

        state.isReading := true
        ; Enable hotkeys when reading starts
        UpdateHotkeys(true)
        voice.Speak(state.currentText, 1) ; Asynchronous reading

        ; Monitor reading status
        SetTimer(CheckReadingStatus, 100)
    } catch as err {
        MsgBox "Error while using text-to-speech: " . err.Message
        ResetState()
    } finally {
        A_Clipboard := OldClipboard
    }
}

CheckReadingStatus() {
    if (voice.Status.RunningState == 1) { ; If reading is complete
        StopReading()
        SetTimer(CheckReadingStatus, 0) ; Stop the timer
    }
}

AdjustSpeed(delta) {
    if (!state.isReading)
        return

    ; Update display speed
    state.speed := Max(Min(state.speed + delta, 10), -10)
    state.speed := Round(state.speed, 1)

    ; Convert to integer for SAPI
    state.internalRate := Round(state.speed)
    voice.Rate := state.internalRate

    ; Display the speed window
    ShowSpeedWindow()
}

ShowSpeedWindow() {
    static speedGui := false

    ; Destroy existing window if present
    if (speedGui) {
        speedGui.Destroy()
    }

    ; Create a new window
    speedGui := Gui("+AlwaysOnTop -Caption +ToolWindow")
    speedGui.SetFont("s12", "Arial")
    speedGui.Add("Text", , "Speed: " . Format("{:.1f}", state.speed))
    ; Position the window
    screenWidth := A_ScreenWidth
    screenHeight := A_ScreenHeight
    guiWidth := 150
    guiHeight := 40
    xPos := (screenWidth - guiWidth) / 2
    yPos := screenHeight - 100

    speedGui.Show("x" . xPos . " y" . yPos . " w" . guiWidth . " h" . guiHeight)

    ; Close the window after 2 seconds
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
    UpdateHotkeys(false)
}

StopReading() {
    if (state.isPaused) {
        voice.Resume()
        state.isPaused := false
    }
    voice.Speak("", 3)  ; Stop current reading
    state.currentText := "" ; Reset text
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

    ; Split text into words, normalize to lowercase for accurate counting
    words := StrSplit(StrLower(text), " ")
    for word in words {
        if (HasVal(frenchWords, word))
            frenchScore++
        if (HasVal(englishWords, word))
            englishScore++
    }

    ; Determine the language based on score
    if (englishScore > frenchScore) {
        return "EN"
    } else {
        return "FR" ; Defaults to French if scores are equal or French is higher
    }
}

HasVal(haystack, needle) {
    ; Checks if a list contains a specific word
    for index, value in haystack
        if (value = needle)
            return true
    return false
}

IgnoreCharacters(text) {
    ; Removes specific characters from text
    charactersToIgnore := ["*", "#", "@", "//"]
    for char in charactersToIgnore {
        text := StrReplace(text, char, "")
    }
    return text
}
