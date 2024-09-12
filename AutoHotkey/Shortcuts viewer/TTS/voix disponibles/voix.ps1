# Fonction pour afficher les voix
function Show-Voices {
    $voices = New-Object -ComObject SAPI.SpVoice
    $availableVoices = $voices.GetVoices()
    $voiceList = @()
    foreach ($voice in $availableVoices) {
        $voiceName = $voice.GetAttribute("Name")
        Write-Host $voiceName
        $voiceList += $voiceName
    }
    return $voiceList
}

# Chemins des registres
$sourcePath = 'HKLM:\software\Microsoft\Speech_OneCore\Voices\Tokens'
$destinationPaths = @(
    'HKLM:\SOFTWARE\Microsoft\Speech\Voices\Tokens',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\SPEECH\Voices\Tokens'
)

# Afficher les voix avant la copie
Write-Host "Voix disponibles avant la copie :"
$voicesBefore = Show-Voices

# Copie des voix
Write-Host "`nCopie des voix en cours..."
$listVoices = Get-ChildItem $sourcePath -ErrorAction SilentlyContinue
if ($listVoices) {
    foreach($voice in $listVoices) {
        $source = $voice.PSPath
        foreach($destPath in $destinationPaths) {
            Copy-Item -Path $source -Destination $destPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "Copié $($voice.Name) vers $destPath"
        }
    }
    Write-Host "Copie des voix terminée."
} else {
    Write-Host "Aucune voix trouvée dans le chemin source. Vérifiez les permissions ou le chemin."
}

Write-Host "`nRedémarrage du service Windows Audio..."
Restart-Service -Name Audiosrv -Force

# Afficher les voix après la copie
Write-Host "`nVoix disponibles après la copie et le redémarrage du service audio :"
$voicesAfter = Show-Voices

# Comparer les listes de voix
$newVoices = Compare-Object -ReferenceObject $voicesBefore -DifferenceObject $voicesAfter | Where-Object { $_.SideIndicator -eq '=>' } | Select-Object -ExpandProperty InputObject
if ($newVoices) {
    Write-Host "`nNouvelles voix ajoutées :"
    $newVoices | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "`nAucune nouvelle voix n'a été ajoutée."
}

# Enregistrer la liste des voix dans un fichier
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$outputFile = Join-Path $scriptPath "VoixDisponibles.txt"
$voicesAfter | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "`nLa liste des voix a été enregistrée dans le fichier : $outputFile"

Write-Host "`nAppuyez sur une touche pour quitter..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")