; Mute_micro.ahk - Module pour couper/activer le microphone
; À inclure dans le script principal avec #Include Mute_micro.ahk

; Variables pour la fenêtre de notification
notificationGui := ""
notificationTimer := ""

; Raccourci Win+Shift+M pour couper/activer le microphone
#+m::
{
    ToggleMicrophone()
}

ToggleMicrophone()
{
    try {
        ; Méthode 1: Toggle avec -1 (recommandée pour v2)
        SoundSetMute(-1, , "Microphone Array")
        newMute := SoundGetMute("Microphone Array")
        ShowNotification(newMute)
        
    } catch Error as err {
        ; Méthode 2: Si erreur, essayer avec le périphérique par défaut
        try {
            SoundSetMute(-1)  ; Toggle du périphérique par défaut
            newMute := SoundGetMute()
            ShowNotification(newMute)
        } catch Error as err2 {
            ShowNotification("Erreur: Impossible de contrôler le microphone")
        }
    }
}

ShowNotification(isMuted)
{
    global notificationGui, notificationTimer
    
    ; Fermer la notification précédente si elle existe
    if (notificationGui) {
        notificationGui.Destroy()
        notificationGui := ""
    }
    
    ; Créer la fenêtre de notification
    notificationGui := Gui("+AlwaysOnTop -MaximizeBox -MinimizeBox +LastFound", "Micro Status")
    notificationGui.BackColor := "0x1a1a1a"  ; Fond noir/gris foncé
    notificationGui.MarginX := 20
    notificationGui.MarginY := 15
    
    ; Déterminer le texte et la couleur
    if (Type(isMuted) = "String") {
        ; Si c'est un message d'erreur
        statusText := isMuted
        textColor := "0xFF6B6B"  ; Rouge clair pour les erreurs
    } else if (isMuted) {
        statusText := "🎤 MICRO OFF"
        textColor := "0xFF6B6B"  ; Rouge clair
    } else {
        statusText := "🎤 MICRO ON"
        textColor := "0x90EE90"  ; Vert clair
    }
    
    ; Ajouter le texte
    textControl := notificationGui.AddText("c" . textColor . " Center", statusText)
    textControl.SetFont("s14 Bold", "Segoe UI")
    
    ; Positionner la fenêtre (coin supérieur droit)
    notificationGui.Show("w200 h60 x" . (A_ScreenWidth - 220) . " y20 NoActivate")
    
    ; Programmer la fermeture automatique après 2 secondes
    if (notificationTimer) {
        SetTimer(notificationTimer, 0)  ; Annuler l'ancien timer
    }
    notificationTimer := ObjBindMethod(CloseNotification)
    SetTimer(notificationTimer, -2000)  ; -2000 = une seule fois après 2 secondes
}

CloseNotification()
{
    global notificationGui, notificationTimer
    
    if (notificationGui) {
        notificationGui.Destroy()
        notificationGui := ""
    }
    notificationTimer := ""
}

