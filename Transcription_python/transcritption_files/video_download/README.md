# Outil de Téléchargement de Vidéos

Cet outil permet de télécharger facilement des vidéos depuis YouTube, Odysee et d'autres sites web en utilisant l'URL dans le presse-papier.

## Fonctionnalités

- Téléchargement de vidéos YouTube avec choix de la qualité (jusqu'à 1080p)
- Téléchargement de vidéos Odysee
- Téléchargement depuis d'autres sites web (mode générique)
- Installation automatique des dépendances
- Mise à jour automatique de yt-dlp
- Exportation automatique des cookies YouTube depuis Chrome

## Prérequis

- Python 3.6 ou supérieur
- Navigateur Chrome (pour l'exportation des cookies YouTube)
- Connexion à Internet

## Installation

Aucune installation manuelle n'est nécessaire. Le script gère automatiquement :

1. La création d'un environnement virtuel Python
2. L'installation des modules requis
3. La mise à jour de yt-dlp
4. L'exportation des cookies depuis Chrome

## Utilisation

1. **Copiez l'URL** de la vidéo que vous souhaitez télécharger dans le presse-papier
2. **Exécutez le fichier `video_download.bat`**
3. Si la vidéo existe déjà, le script vous demandera si vous souhaitez la remplacer
4. **Sélectionnez la qualité** de la vidéo lorsque demandé
5. La vidéo sera téléchargée dans le dossier approprié :
   - YouTube : `C:\Users\dd200\Downloads\Video\Youtube`
   - Odysee : `C:\Users\dd200\Downloads\Video\Odysee`
   - Autres sites : `C:\Users\dd200\Downloads\Video\Generic`
6. Une fois le téléchargement terminé, l'explorateur de fichiers Windows s'ouvrira automatiquement pour afficher le fichier téléchargé

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

- `video_download.bat` : Script batch pour lancer l'outil
- `download_video.py` : Script Python principal
- `requirements.txt` : Liste des dépendances Python
- `cookies.txt` : Fichier de cookies exporté (créé automatiquement)

## Dépendances

Les dépendances suivantes sont automatiquement installées :

- yt-dlp : Pour le téléchargement de vidéos YouTube
- pyperclip : Pour accéder au presse-papier
- beautifulsoup4 : Pour l'analyse HTML
- requests : Pour les requêtes HTTP
- tqdm : Pour les barres de progression
- browser-cookie3 : Pour l'exportation des cookies du navigateur