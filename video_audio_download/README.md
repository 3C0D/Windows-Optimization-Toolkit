# Outil de Téléchargement de Vidéos et d'Audio

## Installation avec UV (Recommandé)

### Installation de UV

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Utilisation

1. **Premier lancement** : Double-cliquez sur `video_audio_download.bat`
   - UV créera automatiquement l'environnement virtuel
   - Installera toutes les dépendances nécessaires
   - Lancera le script

2. **Lancements suivants** : Même commande, UV vérifie et met à jour si nécessaire

3. **Mise à jour manuelle** (optionnel) :

   ```bash
   uv sync --upgrade
   ```

### Avantages de UV

- ⚡ Installation 10-100x plus rapide que pip
- 🔄 Gestion automatique de l'environnement virtuel
- 🔒 Résolution déterministe des dépendances
- 🎯 Utilise pyproject.toml comme source unique des dépendances

---

Cet outil permet de télécharger facilement des vidéos ou de l'audio (MP3) depuis YouTube, Odysee et d'autres sites web en utilisant l'URL dans le presse-papier.

## Fonctionnalités

- Téléchargement de vidéos YouTube avec choix de la qualité (jusqu'à 1080p)
- Extraction audio uniquement en MP3 avec différentes qualités (192, 128, 96 kbps)
- Téléchargement de vidéos Odysee
- Téléchargement depuis d'autres sites web (mode générique)
- **Extraction audio depuis des fichiers vidéo locaux** (MP4, etc.)
- Installation automatique des dépendances
- Mise à jour automatique de yt-dlp
- Exportation automatique des cookies YouTube depuis Chrome

## Prérequis

- Python 3.6 ou supérieur
- Navigateur Chrome (pour l'exportation des cookies YouTube)
- FFmpeg (pour l'extraction audio des fichiers locaux)
- Connexion à Internet

## Installation

Aucune installation manuelle n'est nécessaire. Le script gère automatiquement :

1. La création d'un environnement virtuel Python
2. L'installation des modules requis
3. La mise à jour de yt-dlp
4. L'exportation des cookies depuis Chrome

## Création d'un raccourci sur le Bureau

Pour faciliter l'accès à l'outil, vous pouvez créer un raccourci sur votre Bureau :

1. Faites un clic droit sur le fichier `video_audio_download.bat`
2. Sélectionnez "Créer un raccourci"
3. Déplacez le raccourci créé sur votre Bureau
4. Vous pouvez renommer le raccourci (par exemple "Téléchargeur Vidéo/Audio")
5. Optionnel : Pour changer l'icône, faites un clic droit sur le raccourci, sélectionnez "Propriétés", puis cliquez sur "Changer d'icône"

## Utilisation

1. **Copiez l'URL** de la vidéo que vous souhaitez télécharger **ou le chemin d'un fichier vidéo local** dans le presse-papier
2. **Exécutez le fichier `video_audio_download.bat`** ou utilisez le raccourci créé sur le Bureau
3. **Pour les URLs** : Choisissez le type de téléchargement : vidéo complète ou audio uniquement (MP3)
4. **Pour les fichiers locaux** : L'extraction audio se lance automatiquement (MP3 192 kbps)
5. Si le fichier existe déjà, le script vous demandera si vous souhaitez le remplacer
6. **Sélectionnez la qualité** souhaitée (vidéo ou audio selon votre choix, sauf pour les fichiers locaux)
7. Le fichier sera téléchargé/extrait dans le dossier approprié :
    - Vidéos YouTube : `C:\Users\dd200\Downloads\Video\Youtube`
    - Audio YouTube : `C:\Users\dd200\Downloads\Audio\Youtube`
    - Vidéos Odysee : `C:\Users\dd200\Downloads\Video\Odysee`
    - Audio Odysee : `C:\Users\dd200\Downloads\Audio\Odysee`
    - Autres sites : `C:\Users\dd200\Downloads\Video\Generic` ou `C:\Users\dd200\Downloads\Audio\Generic`
    - **Audio extrait de fichiers locaux** : Dans le dossier Audio correspondant si le fichier source est dans Video, sinon dans le même dossier
8. Une fois le téléchargement terminé, l'explorateur de fichiers Windows s'ouvrira automatiquement pour afficher le fichier téléchargé

## Important pour les vidéos YouTube avec restriction d'âge

Pour accéder aux vidéos avec restriction d'âge ou aux contenus privés sur YouTube :

1. Vous devez être connecté à votre compte YouTube dans le navigateur Chrome
2. Gardez votre session active dans Chrome
3. Le script exportera automatiquement vos cookies lors de la première exécution

**Note** : Seuls les cookies de Chrome sont supportés pour le moment.

## Dépannage

Si vous rencontrez des problèmes :

1. **Erreur d'exportation des cookies** : Assurez-vous d'être connecté à YouTube dans Chrome
2. **Erreur de téléchargement YouTube** : Le script essaiera automatiquement une méthode alternative
3. **Modules manquants** : Le script tentera de les installer automatiquement

Si les problèmes persistent, essayez de supprimer le dossier `venv` et relancez le script pour une installation fraîche.

## Fichiers du projet

- `video_audio_download.bat` : Script batch pour lancer l'outil
- `download_video_audio.py` : Script Python principal
- `pyproject.toml` : Configuration des dépendances Python
- `cookies.txt` : Fichier de cookies exporté (créé automatiquement)

## Dépendances

Les dépendances suivantes sont automatiquement installées :

- yt-dlp : Pour le téléchargement de vidéos YouTube
- pyperclip : Pour accéder au presse-papier
- beautifulsoup4 : Pour l'analyse HTML
- requests : Pour les requêtes HTTP
- tqdm : Pour les barres de progression
- browser-cookie3 : Pour l'exportation des cookies du navigateur
