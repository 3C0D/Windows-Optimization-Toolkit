import sys
import subprocess
import importlib.metadata
import os


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
    import pyperclip
    import json
    import yt_dlp
    import re
    from bs4 import BeautifulSoup
    import requests

except ImportError as e:
    print(f"Erreur lors de l'importation des modules : {e}")
    print("Assurez-vous que tous les modules sont installés et essayez à nouveau.")
    sys.exit(1)


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


def download_youtube_video(url):
    print("\nTéléchargement de la vidéo YouTube...")
    local_path = r"C:\Users\dd200\Downloads\Video\Youtube"
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(local_path, "%(title)s.%(ext)s"),
        "ffmpeg_location": r"C:\ffmpeg\bin\ffmpeg.exe",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print("Téléchargement terminé.")
            return os.path.join(local_path, f"{info['title']}.mp4"), info["title"]
    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")
        return None, None


def download_odysee_video(url):
    print("\nTéléchargement de la vidéo Odysee...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    local_path = r"C:\Users\dd200\Downloads\Video\Odysee"
    video_name = soup.find("title").text + ".mp4"
    video_path = os.path.join(local_path, video_name)
    script_tag = soup.find("script", type="application/ld+json")
    json_content = json.loads(script_tag.string)
    video_url = json_content.get("contentUrl")
    response = requests.get(video_url, stream=True)

    with open(video_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print("Téléchargement terminé.")


def main():
    print("\n===== Début du processus =====\n")

    url = get_url_from_clipboard()
    if not url:
        return

    video_id = get_video_id(url)
    if not video_id:
        print("Impossible d'extraire l'ID de la vidéo.")
        return

    print(f"\nTraitement de la vidéo depuis l'URL : {url}")

    if "youtube.com" in url:
        try:
            audio_file, video_title = download_youtube_video(url)
        except Exception as e:
            print(f"Erreur lors du téléchargement de la video YouTube : {e}")
            return
    elif "odysee.com" in url:
        try:
            download_odysee_video(url)
        except Exception as e:
            print(f"Erreur lors du téléchargement de la video Odysee : {e}")
            return

    print("\n===== Processus terminé =====")


if __name__ == "__main__":
    main()
