import sys
import subprocess
import importlib.metadata
import os
import re
import time
import json


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
    import requests # type: ignore

except ImportError as e:
    print(f"Erreur lors de l'importation des modules : {e}")
    print("Assurez-vous que tous les modules sont installés et essayez à nouveau.")
    sys.exit(1)
    
def select_video_quality(available_formats):
    """
    Sélectionne le meilleur format vidéo disponible selon les préférences:
    1. 1080p (1920x1080)
    2. 720p (1280x720)
    3. 480p (854x480)
    4. Meilleure qualité disponible si aucune des préférées n'est trouvée
    """
    preferred_heights = [1080, 720, 480]
    
    # Filtrer les formats qui contiennent de la vidéo (pas seulement audio)
    video_formats = [f for f in available_formats if f.get('vcodec') != 'none']
    
    # Grouper les formats par hauteur
    formats_by_height = {}
    for fmt in video_formats:
        height = fmt.get('height', 0)
        if height not in formats_by_height:
            formats_by_height[height] = []
        formats_by_height[height].append(fmt)
    
    # Chercher la meilleure qualité disponible parmi les préférées
    for preferred_height in preferred_heights:
        if preferred_height in formats_by_height:
            formats = formats_by_height[preferred_height]
            # Prendre le format avec le meilleur bitrate pour cette résolution
            best_format = max(formats, key=lambda x: x.get('vbr', 0) or 0)
            return best_format['format_id'], preferred_height
    
    # Si aucune qualité préférée n'est disponible, prendre la meilleure disponible
    available_heights = sorted(formats_by_height.keys(), reverse=True)
    if available_heights:
        height = available_heights[0]
        formats = formats_by_height[height]
        best_format = max(formats, key=lambda x: x.get('vbr', 0) or 0)
        return best_format['format_id'], height
    
    return None, None

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

def is_valid_url(url):
    """Vérifie si la chaîne est une URL valide"""
    url_regex = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"
    return bool(re.match(url_regex, url))

def get_url_from_clipboard():
    """Récupère et valide l'URL depuis le presse-papier"""
    print("\nRécupération de l'URL depuis le presse-papier...")
    url = pyperclip.paste()
    
    if not url:
        print("Le presse-papier est vide.")
        return None
        
    if not is_valid_url(url):
        print("Le contenu du presse-papier n'est pas une URL valide.")
        return None
        
    if is_valid_youtube_url(url):
        print("URL YouTube valide trouvée.")
        return ("youtube", url)
    elif is_valid_odysee_url(url):
        print("URL Odysee valide trouvée.")
        return ("odysee", url)
    else:
        print("URL générique trouvée.")
        return ("generic", url)
    
def download_youtube_video(url):
    print("\nTéléchargement de la vidéo YouTube...")
    local_path = r"C:\Users\dd200\Downloads\Video\Youtube"
    
    # Add cookies file if available
    cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
    use_cookies = os.path.exists(cookies_file)
    
    # Utiliser des options plus simples et robustes
    ydl_opts = {
        'format': 'best',  # Format simplifié
        'outtmpl': os.path.join(local_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,  # Ignorer certaines erreurs
        'no_color': True,      # Désactiver les couleurs qui peuvent causer des problèmes
        'geo_bypass': True,    # Contourner les restrictions géographiques
        'geo_bypass_country': 'US',
        'extractor_retries': 10, # Plus de tentatives
        'socket_timeout': 60    # Timeout plus long
    }
    
    # Use cookies if available
    if use_cookies:
        ydl_opts['cookiefile'] = cookies_file
        print(f"Utilisation du fichier de cookies: {cookies_file}")

    try:
        # Tentative avec yt-dlp directement
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            filename = f"{video_title}.mp4"
            filepath = os.path.join(local_path, filename)
            
            if os.path.exists(filepath):
                print(f"Le fichier '{filename}' existe déjà dans '{local_path}'. Téléchargement ignoré.")
                return
                
            # Télécharger la vidéo
            ydl.download([url])
            print("Téléchargement terminé avec succès.")
            
    except Exception as e:
        print(f"Erreur avec yt-dlp : {str(e)}")
        print("Tentative avec méthode alternative...")
        
        # Méthode alternative avec subprocess
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--format", "best",
                "--output", os.path.join(local_path, "%(title)s.%(ext)s"),
                "--no-playlist",
                "--no-check-certificate",
                "--geo-bypass",
            ]
            
            if use_cookies:
                cmd.extend(["--cookies", cookies_file])
                
            cmd.append(url)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Erreur subprocess: {result.stderr}")
                raise Exception(result.stderr)
                
            print("Téléchargement terminé avec succès via subprocess.")
            
        except Exception as e2:
            print(f"Toutes les tentatives ont échoué. Erreur finale : {str(e2)}")
            return
def download_odysee_video(url):
    print("\nTéléchargement de la vidéo Odysee...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    local_path = r"C:\Users\dd200\Downloads\Video\Odysee"
    video_name = soup.find("title").text + ".mp4"
    video_path = os.path.join(local_path, video_name)

    # Étape 1 : Vérifier si le fichier existe déjà
    if os.path.exists(video_path):
        print(
            f"Le fichier '{video_name}' existe déjà dans '{local_path}'. Téléchargement ignoré."
        )
        return

    try:
        script_tag = soup.find("script", type="application/ld+json")
        json_content = json.loads(script_tag.string)
        video_url = json_content.get("contentUrl")

        if not video_url:
            print("URL du contenu non trouvée dans les métadonnées.")
            return

        response = requests.get(video_url, stream=True)

        with open(video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print("Téléchargement terminé.")

    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")

def download_generic_video(url):
    """Télécharge une vidéo depuis une URL générique"""
    print("\nTéléchargement de la vidéo depuis une URL générique...")
    local_path = r"C:\Users\dd200\Downloads\Video\Generic"
    os.makedirs(local_path, exist_ok=True)  # Crée le dossier s'il n'existe pas
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.find("title")
        video_name = (title.text if title else "video") + ".mp4"
        video_name = re.sub(r'[<>:"/\\|?*]', '_', video_name)
        video_path = os.path.join(local_path, video_name)
        
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Fichier existant supprimé: {video_name}")
            except Exception as e:
                print(f"Impossible de supprimer le fichier existant: {e}")
                return

        # Chercher toutes les sources vidéo possibles
        video_sources = []
        
        # Chercher dans les balises JSON-LD
        script_tags = soup.find_all("script", type="application/ld+json")
        for script in script_tags:
            try:
                json_content = json.loads(script.string)
                if isinstance(json_content, dict):
                    if "contentUrl" in json_content:
                        video_sources.append({"url": json_content["contentUrl"], "quality": "unknown"})
                    if "encodingFormat" in json_content:
                        for format_info in json_content.get("encodingFormat", []):
                            if isinstance(format_info, dict):
                                url = format_info.get("contentUrl")
                                quality = format_info.get("quality", "unknown")
                                if url:
                                    video_sources.append({"url": url, "quality": quality})
            except:
                continue

        # Chercher dans les balises vidéo et source
        video_tag = soup.find("video")
        if video_tag:
            src = video_tag.get("src")
            if src:
                video_sources.append({"url": src, "quality": "unknown"})
            
            source_tags = video_tag.find_all("source")
            for source in source_tags:
                src = source.get("src")
                if src:
                    quality = source.get("size", "unknown")
                    video_sources.append({"url": src, "quality": quality})

        if not video_sources:
            print("Aucune source vidéo trouvée dans la page.")
            return

        # Sélectionner la meilleure qualité disponible
        preferred_qualities = ["1080", "720", "480"]
        selected_url = None
        selected_quality = None

        for preferred_quality in preferred_qualities:
            for source in video_sources:
                if str(preferred_quality) in str(source["quality"]):
                    selected_url = source["url"]
                    selected_quality = preferred_quality
                    break
            if selected_url:
                break

        if not selected_url:
            selected_url = video_sources[0]["url"]
            selected_quality = "meilleure disponible"

        print(f"Téléchargement en qualité {selected_quality}...")
        
        response = requests.get(selected_url, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        block_size = 1024 * 1024  # 1 MB
        
        with open(video_path, 'wb') as f:
            try:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=video_name) as pbar:
                    start_time = time.time()
                    bytes_downloaded = 0
                    
                    for data in response.iter_content(block_size):
                        if not data:
                            break
                        f.write(data)
                        bytes_downloaded += len(data)
                        pbar.update(len(data))
                        
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = bytes_downloaded / (1024 * 1024 * elapsed_time)  # MB/s
                            pbar.set_postfix(speed=f"{speed:.2f} MB/s")

                print(f"\nTéléchargement terminé : {video_name}")
                print(f"Taille : {total_size / (1024*1024):.2f} MB")
                print(f"Temps total : {time.time() - start_time:.2f} secondes")
                
            except Exception as e:
                print(f"Erreur pendant le téléchargement : {e}")
                # Supprime le fichier partiellement téléchargé en cas d'erreur
                if os.path.exists(video_path):
                    os.remove(video_path)
                raise

    except Exception as e:
        print(f"Erreur lors du téléchargement générique : {str(e)}")
        # Nettoyer en cas d'erreur
        if os.path.exists(video_path):
            os.remove(video_path)

def main():
    print("\n===== Début du processus =====\n")

    result = get_url_from_clipboard()
    if not result:
        return

    type_url, url = result
    print(f"\nTraitement de la vidéo depuis l'URL : {url}")

    try:
        if type_url == "youtube":
            download_youtube_video(url)
        elif type_url == "odysee":
            download_odysee_video(url)
        else:
            download_generic_video(url)
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")

    print("\n===== Processus terminé =====")

if __name__ == "__main__":
    main()
