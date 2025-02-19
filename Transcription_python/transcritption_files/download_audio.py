import sys
import subprocess
import importlib.metadata
import os
import re
import time
import json
import requests

def read_requirements(file_path):
    """Lire les packages requis dans le fichier de requirements"""
    required_packages = set()
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                package_name = line.split("==")[0].split("<")[0].split(">")[0].strip()
                required_packages.add(package_name.lower())
    return required_packages

def install_modules(venv_path, requirements_file):
    """Installer les modules requis dans l'environnement virtuel"""
    pip_path = (
        os.path.join(venv_path, "Scripts", "pip")
        if sys.platform == "win32"
        else os.path.join(venv_path, "bin", "pip")
    )
    subprocess.check_call([pip_path, "install", "-r", requirements_file])

def check_and_install_modules(required):
    """Vérifier si les modules requis sont installés et les installer si nécessaire"""
    installed = {
        pkg.metadata["Name"].lower() for pkg in importlib.metadata.distributions()
    }
    missing = required - installed
    if not missing:
        return

    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    requirements_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
    )
    install_modules(venv_path, requirements_path)

    print("Modules installés avec succès dans l'environnement virtuel.")

script_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(script_dir, "requirements.txt")
required_modules = read_requirements(requirements_path)

try:
    check_and_install_modules(required_modules)
except Exception as e:
    print(f"Erreur lors de l'installation des modules : {e}")
    sys.exit(1)

# Importer les modules nécessaires
try:
    import pyperclip # type: ignore
    import yt_dlp # type: ignore
    from bs4 import BeautifulSoup # type: ignore
    from tqdm import tqdm # type: ignore
except ImportError as e:
    print(f"Erreur lors de l'importation des modules : {e}")
    print("Assurez-vous que tous les modules sont installés et essayez à nouveau.")
    sys.exit(1)

def select_video_quality(available_formats):
    """
    Sélectionne le format vidéo selon les préférences pour l'extraction audio:
    1. 480p (854x480)
    2. 720p (1280x720)
    3. 1080p (1920x1080)
    """
    preferred_heights = [480, 720, 1080]
    
    # Filtrer les formats qui contiennent de la vidéo
    video_formats = [f for f in available_formats if f.get('vcodec') != 'none']
    
    # Grouper les formats par hauteur
    formats_by_height = {}
    for fmt in video_formats:
        height = fmt.get('height', 0)
        if height not in formats_by_height:
            formats_by_height[height] = []
        formats_by_height[height].append(fmt)
    
    # Chercher la première qualité disponible parmi les préférées
    for preferred_height in preferred_heights:
        if preferred_height in formats_by_height:
            formats = formats_by_height[preferred_height]
            best_format = max(formats, key=lambda x: x.get('abr', 0) or 0)
            return best_format['format_id'], preferred_height
    
    # Si aucune qualité préférée n'est disponible, prendre la plus basse disponible
    available_heights = sorted(formats_by_height.keys())
    if available_heights:
        height = available_heights[0]
        formats = formats_by_height[height]
        best_format = max(formats, key=lambda x: x.get('abr', 0) or 0)
        return best_format['format_id'], height
    
    return None, None

def modify_youtube_options(ydl_opts):
    """
    Modifie les options yt-dlp pour sélectionner la qualité appropriée
    """
    def format_selector(ctx):
        formats = ctx.get('formats', [])
        format_id, height = select_video_quality(formats)
        
        if format_id:
            print(f"Qualité vidéo sélectionnée pour extraction audio : {height}p")
            return f"{format_id}+bestaudio"
        return 'bestaudio'  # Fallback to best audio
    
    ydl_opts['format'] = format_selector
    return ydl_opts

def is_valid_youtube_url(url):
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    return bool(re.match(youtube_regex, url))

def is_valid_odysee_url(url):
    odysee_regex = r"https?://odysee\.com/([a-zA-Z0-9\-_@:]+)"
    return bool(re.match(odysee_regex, url))

def get_url_from_clipboard():
    print("\nRécupération de l'URL depuis le presse-papier...")
    url = pyperclip.paste()
    if not url:
        print("Le presse-papier est vide.")
        return None
    if is_valid_youtube_url(url) or is_valid_odysee_url(url):
        print("URL valide trouvée.")
        return url
    print("L'URL dans le presse-papier n'est pas une URL YouTube ou Odysee valide.")
    return None

def get_video_id(url):
    """Extraire l'ID de la vidéo depuis l'URL"""
    print("\nExtraction de l'ID de la vidéo...")
    if is_valid_youtube_url(url):
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        return video_id.group(1) if video_id else None
    if is_valid_odysee_url(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find("title").text
    print("Impossible d'extraire l'ID de la vidéo.")
    return None

def download_youtube_audio(url):
    print("\nExtraction de l'audio YouTube...")
    local_path = r"C:\Users\dd200\Downloads\Video\Youtube"
    os.makedirs(local_path, exist_ok=True)

    try:
        # Configuration des options de téléchargement avec les nouveaux paramètres anti-bot
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(local_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
            'noplaylist': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'http_headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Dest': 'empty',
                'Connection': 'keep-alive',
            },
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'quiet': False,
            'no_warnings': False,
            'extractor_retries': 3,
            'socket_timeout': 30
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Vérification du fichier existant
            info = ydl.extract_info(url, download=False)
            audio_title = info.get('title', 'audio')
            expected_filename = f"{audio_title}.mp3"
            expected_filepath = os.path.join(local_path, expected_filename)

            if os.path.exists(expected_filepath):
                print(f"Le fichier audio '{expected_filename}' existe déjà dans '{local_path}'. Extraction ignorée.")
                return

            # Téléchargement avec les options configurées
            ydl.download([url])
            print("Extraction audio terminée.")

    except Exception as e:
        print(f"Erreur lors de l'extraction audio : {str(e)}")
        return

def download_odysee_audio(url):
    print("\nExtraction de l'audio Odysee...")
    local_path = r"C:\Users\dd200\Downloads\Video\Odysee"
    os.makedirs(local_path, exist_ok=True)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        audio_name = soup.find("title").text + ".mp3"
        audio_path = os.path.join(local_path, audio_name)

        if os.path.exists(audio_path):
            print(
                f"Le fichier audio '{audio_name}' existe déjà dans '{local_path}'. Extraction ignorée."
            )
            return

        script_tag = soup.find("script", type="application/ld+json")
        json_content = json.loads(script_tag.string)
        video_url = json_content.get("contentUrl")

        if not video_url:
            print("URL du contenu non trouvée dans les métadonnées.")
            return

        # Configuration des options de téléchargement
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_path,
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraire les informations pour la sélection de format
            info = ydl.extract_info(video_url, download=False)
            format_id, height = select_video_quality(info['formats'])
            
            if format_id:
                print(f"Qualité vidéo sélectionnée pour extraction audio : {height}p")
                ydl_opts['format'] = f"{format_id}+bestaudio/bestaudio/best"
            
            # Télécharger avec les options mises à jour
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([video_url])

        print("Extraction audio terminée.")

    except Exception as e:
        print(f"Erreur lors de l'extraction audio : {str(e)}")

def main():
    print("\n===== Début du processus d'extraction audio =====\n")

    url = get_url_from_clipboard()
    if not url:
        return

    video_id = get_video_id(url)
    if not video_id:
        print("Impossible d'extraire l'ID de la vidéo.")
        return

    print(f"\nTraitement de l'audio depuis l'URL : {url}")

    try:
        if is_valid_youtube_url(url):
            download_youtube_audio(url)
        elif is_valid_odysee_url(url):
            download_odysee_audio(url)
    except Exception as e:
        print(f"Erreur lors de l'extraction audio : {e}")

    print("\n===== Processus d'extraction audio terminé =====")

if __name__ == "__main__":
    main()