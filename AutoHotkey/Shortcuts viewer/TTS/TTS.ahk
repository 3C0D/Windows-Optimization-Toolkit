#Requires AutoHotkey v2.0

InitializeVoices() {
    ; First check if voices are missing without admin rights
    sourcePath := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"
    destinationPaths := [
        "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens",
        "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\SPEECH\Voices\Tokens"
    ]

    ; Check for missing voices in registry
    missingVoices := false
    try {
        loop reg, sourcePath, "K" {
            sourceKey := A_LoopRegKey "\" A_LoopRegName
            for destPath in destinationPaths {
                destKey := destPath "\" A_LoopRegName
                if !RegRead(destKey) {
                    missingVoices := true
                    break 2
                }
            }
        }
    }

    ; Exit if no voices need to be installed
    if (!missingVoices)
        return

    ; Request admin rights if needed
    if !A_IsAdmin {
        MsgBox "Additional voices available. The script will restart with administrator rights to install them."
        try {
            if A_IsCompiled
                Run '*RunAs "' A_ScriptFullPath '" /restart'
            else
                Run '*RunAs "' A_AhkPath '" /restart "' A_ScriptFullPath '"'
            ExitApp
        }
        catch {
            MsgBox "Could not obtain administrator rights. Some voices may not be available."
            return
        }
    }

    ; Copy registry keys and update voices
    try {
        for destPath in destinationPaths {
            loop reg, sourcePath, "K" {
                sourceKey := A_LoopRegKey "\" A_LoopRegName
                destKey := destPath "\" A_LoopRegName
                if !RegRead(destKey)
                    RegCreateKey(destKey)
                loop reg, sourceKey, "V" {
                    RegWrite(RegRead(sourceKey, A_LoopRegName), "REG_SZ", destKey, A_LoopRegName)
                }
            }
        }

        ; Restart audio service to apply changes
        RunWait "net stop Audiosrv", , "Hide"
        RunWait "net start Audiosrv", , "Hide"

        ; Just reload without message
        Reload
    }
    catch as err {
        MsgBox "Error updating voices: " err.Message
    }
}

; Uncomment if voices are not found.
; InitializeVoices()

; Global variables
global APP_VERSION := "1.0.0"
global state := {
    isReading: false,
    isPaused: false,
    speed: 2.0,  ; Speed for display
    internalRate: 2, ; Integer speed for SAPI
    currentText: "",   ; Current text being read
    originalText: "",  ; Original complete text
    volume: 100      ; Volume level (0-100)
}

global voice := ComObject("SAPI.SpVoice")

; Create tray icon - only needed if not compiled with an icon
if (!A_IsCompiled)
    TraySetIcon(A_ScriptDir "\TTS.ico", , true)

A_TrayMenu.Delete()  ; Remove default options
A_TrayMenu.Add("TTS Reader v" . APP_VERSION, (*) => ShowHelp())
A_TrayMenu.Add()  ; Separator
A_TrayMenu.Add("Shortcuts...", (*) => ShowHelp())
A_TrayMenu.Add()  ; Separator
A_TrayMenu.Add("Run at startup", ToggleStartup)
A_TrayMenu.Add()  ; Separator
A_TrayMenu.Add("Exit", (*) => ExitApp())
A_TrayMenu.Default := "Shortcuts..."

; Check if already set to run at startup and update menu
startupPath := A_Startup "\TTS Reader.lnk"
if FileExist(startupPath)
    A_TrayMenu.Check("Run at startup")

; Function to toggle startup status
ToggleStartup(*) {
    startupPath := A_Startup "\TTS Reader.lnk"
    
    if FileExist(startupPath) {
        ; Remove from startup
        try {
            FileDelete(startupPath)
            A_TrayMenu.Uncheck("Run at startup")
        } catch as err {
            MsgBox("Error removing startup shortcut: " . err.Message)
        }
    } else {
        ; Add to startup
        try {
            if A_IsCompiled {
                FileCreateShortcut(A_ScriptFullPath, startupPath, A_WorkingDir)
            } else {
                FileCreateShortcut(A_AhkPath, startupPath, A_WorkingDir, '"' . A_ScriptFullPath . '"')
            }
            A_TrayMenu.Check("Run at startup")
        } catch as err {
            MsgBox("Error creating startup shortcut: " . err.Message)
        }
    }
}
; A_TrayMenu.Add("Play/Stop (Win+Y)", (*) => ReadText("AUTO"))
A_TrayMenu.Add()  ; Separator
A_TrayMenu.Add("Exit", (*) => ExitApp())
A_TrayMenu.Default := "Shortcuts..."

; Function to display shortcuts help
ShowHelp(*) {
    helpText := "
    (    
    MAIN SHORTCUTS:
    Win+Y : Play/Stop selected text
    Win+Alt+Y : Pause/Resume reading
    
    NAVIGATION:
    Win+Ctrl+Y : Skip to next paragraph
    Win+Shift+Y : Go to previous paragraph
    
    SPEED:
    Numpad+ : Increase speed
    Numpad- : Decrease speed
    
    VOLUME:
    Numpad* : Increase volume
    Numpad/ : Decrease volume
    
    === How to use ===
    1. Select or copy text in any application
    2. Press Win+Y to start reading
    3. Use the shortcuts above to control playback
    
    Language is automatically detected (English or French).
    )"
    
    helpGui := Gui("+AlwaysOnTop")
    helpGui.Title := "Shortcuts"
    helpGui.SetFont("s10", "Segoe UI")
    helpGui.Add("Text", "w500", helpText)
    helpGui.Add("Button", "Default w100", "OK").OnEvent("Click", (*) => helpGui.Destroy())
    helpGui.Show()
}

; Manage hotkeys
UpdateHotkeys(enable := true) {
    if (enable) {
        ; Speed and volume controls
        Hotkey "NumpadAdd", "On"
        Hotkey "NumpadSub", "On"
        Hotkey "NumpadMult", "On"      ; Volume Up
        Hotkey "NumpadDiv", "On"       ; Volume Down
        
        ; Navigation and control hotkeys
        Hotkey "#^y", "On"              ; Next line
        Hotkey "#+y", "On"              ; Previous paragraph
        Hotkey "#!y", "On"              ; Pause/Resume
    } else {
        ; Speed and volume controls
        Hotkey "NumpadAdd", "Off"
        Hotkey "NumpadSub", "Off"
        Hotkey "NumpadMult", "Off"     ; Volume Up
        Hotkey "NumpadDiv", "Off"      ; Volume Down
        
        ; Navigation and control hotkeys
        Hotkey "#^y", "Off"             ; Next line
        Hotkey "#+y", "Off"             ; Previous paragraph
        Hotkey "#!y", "Off"             ; Pause/Resume
    }
}

; Initialize hotkeys
Hotkey "NumpadAdd", AdjustSpeedUp
Hotkey "NumpadSub", AdjustSpeedDown
Hotkey "NumpadMult", VolumeUp
Hotkey "NumpadDiv", VolumeDown
Hotkey "#^y", JumpToNextLine
Hotkey "#+y", JumpToPreviousParagraph
Hotkey "#!y", TogglePause
; Disable hotkeys at start
UpdateHotkeys(false)

; play/stop
#y:: ReadText("AUTO")

; Function to jump to the next line
JumpToNextLine(*) {
    ; Do nothing if reading is paused
    if (state.isPaused)
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

; Function to jump to the previous paragraph
JumpToPreviousParagraph(*) {
    if (state.isPaused)
        return

    ; Static variables to track jumps and timing
    static lastJumpTime := 0
    static jumpCount := 0
    
    currentTime := A_TickCount
    
    ; Calculate the actual position in the original text
    currentPosInCurrent := voice.Status.InputWordPosition
    currentTextStart := InStr(state.originalText, state.currentText)
    currentPos := currentTextStart + currentPosInCurrent
    
    ; Check if we're within the time window for multiple jumps
    if (currentTime - lastJumpTime < 3000) {
        jumpCount++
    } else {
        jumpCount := 1
    }
    
    ; Record the time of this jump
    lastJumpTime := currentTime
    
    ; Stop the current reading completely (necessary to reset SAPI state)
    voice.Speak("", 3)  ; SVSFPurgeBeforeSpeak (stops immediately)
    
    ; Calculate the new position in the original text
    if (jumpCount == 1) {
        ; For first jump, find the previous paragraph or line break
        newPos := InStr(SubStr(state.originalText, 1, currentPos), "`n",, -1)
        if (!newPos)
            newPos := 1
    } else {
        ; For multiple jumps, look for double line breaks (paragraphs)
        searchPos := currentPos
        paragraphCount := 0
        
        while (searchPos > 1 && paragraphCount < jumpCount) {
            ; Look for paragraph break
            foundPos := InStr(SubStr(state.originalText, 1, searchPos), "`n`n",, -1)
            if (foundPos) {
                searchPos := foundPos - 1
                paragraphCount++
            } else {
                ; If no more paragraph breaks found, go to beginning
                searchPos := 1
                break
            }
        }
        
        newPos := searchPos
    }
    
    ; Create new text starting from the calculated position
    remainingText := SubStr(state.originalText, newPos)
    remainingText := RegExReplace(remainingText, "^[\r\n]+", "")
    
    if (remainingText != "") {
        ; Update current text and start new reading
        state.currentText := remainingText
        voice.Rate := state.internalRate
        voice.Speak(remainingText, 1)  ; Start new asynchronous reading
    } else {
        StopReading()
    }
}

; Helper function to find paragraph boundaries in text
FindParagraphBoundaries(text) {
    boundaries := []
    
    ; Always include the start of the text
    startPos := 1
    
    ; Scan through the text to find paragraph boundaries
    searchPos := 1
    textLength := StrLen(text)
    
    while (searchPos <= textLength) {
        ; Look for paragraph breaks (double newlines)
        paragraphBreak := InStr(text, "`n`n", false, searchPos)
        
        ; If no more paragraph breaks, the end of text is the last boundary
        if (!paragraphBreak) {
            ; Add the final paragraph
            boundaries.Push({ start: startPos, end: textLength + 1 })
            break
        }
        
        ; Add this paragraph boundary
        boundaries.Push({ start: startPos, end: paragraphBreak + 2 })
        
        ; Skip past any consecutive newlines
        newPos := paragraphBreak + 2
        while (SubStr(text, newPos, 1) == "`n" && newPos <= textLength) {
            newPos++
        }
        
        ; Start of next paragraph
        startPos := newPos
        searchPos := newPos
    }
    
    ; If no paragraphs were found (no double newlines), treat the entire text as one paragraph
    if (boundaries.Length == 0) {
        boundaries.Push({ start: 1, end: textLength + 1 })
    }
    
    return boundaries
}
AdjustSpeedUp(*) {
    AdjustSpeed(0.5)
}

AdjustSpeedDown(*) {
    AdjustSpeed(-0.5)
}

; Helper function for clipboard operations (we copy it there again needed for compilation .exe)
getSelOrCbText() {
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


ReadText(language) {
    if (voice.Status.RunningState == 2 || state.isPaused) {
        StopReading()
        return
    }

    ResetState()

    text := getSelOrCbText()  ; importée depuis browserShortcuts.ahk 
    if (text == "")
        return
        
    state.currentText := text
    state.originalText := text  ; Store the original text
    state.currentText := IgnoreCharacters(state.currentText)
    state.originalText := IgnoreCharacters(state.originalText)

    try {
        SetVoiceLanguage(language, state.currentText)
        voice.Rate := state.internalRate

        state.isReading := true
        ; Enable hotkeys when reading starts
        UpdateHotkeys(true)
        voice.Speak(state.currentText, 1)  ; Asynchronous reading

        ; Monitor reading status
        SetTimer(CheckReadingStatus, 100)
    } catch as err {
        MsgBox "Error using text-to-speech: " . err.Message
        ResetState()
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

TogglePause(*) {
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
    ; Language detection based on common words and patterns
    frenchWords := ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "donc", "or", "ni", "car", "que", "qui",
        "quoi", "dont", "où", "à", "au", "avec", "pour", "sur", "dans", "par", "ce", "cette", "ces", "je", "tu", "il", "elle",
        "nous", "vous", "ils", "elles", "mon", "ton", "son", "notre", "votre", "leur"
    ]
    englishWords := ["the", "and", "or", "but", "so", "yet", "for", "nor", "that", "which", "who", "whom", "whose",
        "when", "where", "why", "how", "a", "an", "in", "on", "at", "with", "by", "this", "these", "those", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should"
    ]

    ; Add weight to more distinctive words
    distinctiveFrench := ["est", "sont", "être", "avoir", "fait", "très", "beaucoup", "toujours", "jamais"]
    distinctiveEnglish := ["is", "are", "be", "have", "do", "very", "much", "always", "never"]

    frenchScore := 0
    englishScore := 0
    
    ; Count French-specific characters (adds to French score)
    frenchChars := "éèêëàâäôöùûüçÉÈÊËÀÂÄÔÖÙÛÜÇ"
    for char in StrSplit(text) {
        if InStr(frenchChars, char)
            frenchScore += 0.5  ; Give moderate weight to accented characters
    }

    ; Split text into words, normalize to lowercase for accurate counting
    words := StrSplit(StrLower(text), " ")
    for word in words {
        ; Check regular words
        if (HasVal(frenchWords, word))
            frenchScore++
        if (HasVal(englishWords, word))
            englishScore++
            
        ; Give extra weight to distinctive words
        if (HasVal(distinctiveFrench, word))
            frenchScore += 2
        if (HasVal(distinctiveEnglish, word))
            englishScore += 2
    }

    ; Check for language-specific patterns
    if (RegExMatch(text, "i)qu'[aeiouy]|c'est|n'[aeiouy]|l'[aeiouy]|d'[aeiouy]"))
        frenchScore += 3
    if (RegExMatch(text, "i)ing\s|ed\s|'s\s|'ve\s|'re\s|'ll\s"))
        englishScore += 3

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
    charactersToIgnore := ["*", " #", "##", "# ", "\n#", "@", "//", "/"]
    for char in charactersToIgnore {
        text := StrReplace(text, char, "")
    }
    return text
}

VolumeUp(*) {
    if (state.volume < 100) {
        state.volume += 10
        voice.Volume := state.volume
        ShowVolumeWindow()
    }
}

VolumeDown(*) {
    if (state.volume > 0) {
        state.volume -= 10
        voice.Volume := state.volume
        ShowVolumeWindow()
    }
}

ShowVolumeWindow() {
    static volumeGui := false

    ; Destroy existing window if present
    if (volumeGui) {
        volumeGui.Destroy()
    }

    ; Create a new window
    volumeGui := Gui("+AlwaysOnTop -Caption +ToolWindow")
    volumeGui.SetFont("s12", "Arial")
    volumeGui.Add("Text", , "Volume: " . state.volume . "%")
    
    ; Position the window
    screenWidth := A_ScreenWidth
    screenHeight := A_ScreenHeight
    guiWidth := 150
    guiHeight := 40
    xPos := (screenWidth - guiWidth) / 2
    yPos := screenHeight - 100

    volumeGui.Show("x" . xPos . " y" . yPos . " w" . guiWidth . " h" . guiHeight)

    ; Close the window after 2 seconds
    SetTimer () => volumeGui.Destroy(), -2000
}