; Script AutoHotkey pour capture d'écran et traduction via un chat IA
#Requires AutoHotkey v2.0
#SingleInstance Force

; Configuration - Changer ces variables pour basculer entre les services
useGemini := false    ; true pour utiliser Gemini, false pour utiliser Mistral

; Raccourci clavier: Ctrl + Win + Q
^#q::
{
    ; Définir les paramètres selon le service choisi
    if (useGemini) {
        chatUrl := "https://gemini.google.com/app"
        chatWindowTitle := "Gemini"
        promptText := "Extrais le texte de cette image. Affiche d'abord le texte original, puis sa traduction en français."
    } else {
        chatUrl := "https://chat.mistral.ai/chat"
        chatWindowTitle := "Le Chat - Mistral AI"
        promptText := "Extrais le texte de cette image. Affiche d'abord le texte original, puis sa traduction en français."
    }
    
    ; Dossier de destination pour les captures
    screenshotDir := "C:\\Users\\dd200\\Pictures\\Screenshots\\"
    
    ; Créer le dossier s'il n'existe pas
    if !DirExist(screenshotDir)
        DirCreate(screenshotDir)
    
    ; Capturer une zone de l'écran
    Sleep 300
    try {
        ; Mémoriser l'heure actuelle pour trouver le nouveau fichier plus tard
        startTime := A_Now
        
        ; Utiliser la commande intégrée de capture d'écran
        Run "ms-screenclip:"
        
        ; Attendre que l'utilisateur fasse la capture
        Sleep 500  ; Petit délai pour que l'outil de capture s'ouvre
        
        ; Attendre que le curseur change, indiquant que l'outil est prêt
        KeyWait "LButton", "D"  ; Attendre que le bouton gauche soit enfoncé
        KeyWait "LButton"       ; Attendre que le bouton gauche soit relâché
        
        ; Attendre que le fichier soit enregistré
        Sleep 2000
        
        ; Trouver le fichier le plus récent créé après startTime
        latestFile := ""
        latestTime := 0
        
        ; Chercher le fichier de capture d'écran
        loop Files, screenshotDir "*.png"
        {
            fileTime := FileGetTime(A_LoopFileFullPath)
            if (fileTime > startTime && fileTime > latestTime)
            {
                latestTime := fileTime
                latestFile := A_LoopFileFullPath
            }
        }
        
        if (latestFile = "")
        {
            ; Attendre un peu plus si aucun fichier n'est trouvé
            Sleep 3000
            
            ; Essayer à nouveau de trouver le fichier
            loop Files, screenshotDir "*.png"
            {
                fileTime := FileGetTime(A_LoopFileFullPath)
                if (fileTime > startTime && fileTime > latestTime)
                {
                    latestTime := fileTime
                    latestFile := A_LoopFileFullPath
                }
            }
            
            if (latestFile = "")
                throw "Aucun fichier de capture trouvé. Veuillez réessayer."
        }
        
        ; Copier l'image dans le presse-papiers
        if !FileExist(latestFile)
            throw "Fichier de capture introuvable: " latestFile
            
        Clipboard := "" ; Vider le presse-papiers
        Clipboard := FileRead(latestFile)
        
        ; Ouvrir le chat IA dans le navigateur
        Run chatUrl
        if !WinWait(chatWindowTitle,, 30)
            throw "Timeout lors de l'ouverture de " chatWindowTitle
            
        ; Activer la fenêtre du chat
        WinActivate chatWindowTitle
        
        ; Attendre que la page se charge
        Sleep 1000
        
        ; Coller l'image et ajouter la requête
        Send "^v"
        Sleep 1000
        Send promptText
        Sleep 500
        Send "{Enter}"
    } catch Error as e {
        MsgBox "Erreur: " e.Message, "OCR Traduction", "IconX"
    }
}