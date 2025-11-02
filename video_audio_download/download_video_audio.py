import sys
import subprocess
import os
import re
import time
import json
import importlib.metadata

# Import pour accéder au registre Windows (pour obtenir le dossier Téléchargements)
if sys.platform == "win32":
    import winreg


def read_requirements():
    """Lire les packages requis dans le fichier de requirements"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, "requirements.txt")

    required_packages = set()
    with open(requirements_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                package_name = line.split("==")[0].split("<")[0].split(">")[0].strip()
                required_packages.add(package_name.lower())
    return required_packages


def install_modules(missing_modules):
    """Installer les modules requis dans l'environnement virtuel"""
    if missing_modules:
        print(f"\nInstallation des modules manquants: {', '.join(missing_modules)}")
        print("Cette opération peut prendre de 1 à 2 minutes, veuillez patienter...")
    else:
        print("\nMise à jour des modules...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(script_dir, "venv")
    requirements_path = os.path.join(script_dir, "requirements.txt")

    pip_path = (
        os.path.join(venv_path, "Scripts", "pip")
        if sys.platform == "win32"
        else os.path.join(venv_path, "bin", "pip")
    )
    # Utiliser -q pour réduire la verbosité
    subprocess.check_call([pip_path, "install", "-q", "-r", requirements_path])


def open_file_explorer(path):
    """
    Ouvre l'explorateur de fichiers Windows à l'emplacement spécifié.

    Args:
        path (str): Chemin du fichier ou du dossier à ouvrir
    """
    # Normaliser le chemin pour éviter les problèmes avec les barres obliques
    normalized_path = os.path.normpath(path)

    # Essayer d'ouvrir l'explorateur de fichiers directement
    try:
        # Vérifier si c'est un fichier ou un dossier
        if os.path.isfile(normalized_path):
            # Ouvrir le dossier contenant le fichier et sélectionner le fichier
            subprocess.Popen(f'explorer /select,"{normalized_path}"', shell=True)
        else:
            # Ouvrir directement le dossier
            subprocess.Popen(f'explorer "{normalized_path}"', shell=True)
    except Exception as e:
        print(
            f"Note: Impossible d'ouvrir automatiquement l'explorateur de fichiers: {e}"
        )
        print(f"Chemin du fichier: {normalized_path}")


def get_windows_downloads_folder():
    """
    Obtient le chemin exact du dossier Téléchargements sur Windows en utilisant le registre.
    Cette méthode fonctionne quelle que soit la langue du système.

    Returns:
        str: Chemin du dossier Téléchargements
    """
    try:
        # GUID du dossier Téléchargements dans Windows
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        ) as key:
            downloads = winreg.QueryValueEx(key, downloads_guid)
            return downloads[0]
    except Exception:
        # Fallback 1: Essayer avec le nom connu
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            ) as key:
                downloads = winreg.QueryValueEx(key, "Downloads")
                return downloads[0]
        except Exception:
            # Fallback 2: Utiliser la méthode standard
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                # Essayer les noms courants
                for name in ["Téléchargements", "Downloads"]:
                    path = os.path.join(user_profile, name)
                    if os.path.exists(path):
                        return path
                # Dernier recours
                return os.path.join(user_profile, "Downloads")
            else:
                return os.path.join(os.path.expanduser("~"), "Downloads")


def get_download_path(source_type):
    """
    Obtient le chemin de téléchargement pour un type de source donné.
    Crée les dossiers nécessaires s'ils n'existent pas.

    Args:
        source_type (str): Type de source ('youtube', 'youtube_audio', 'odysee', 'odysee_audio', 'generic', 'generic_audio')

    Returns:
        str: Chemin complet vers le dossier de téléchargement
    """
    # Obtenir le dossier Téléchargements/Downloads de l'utilisateur
    # Comme ce script est conçu pour Windows, on utilise directement la fonction spécifique
    downloads_folder = get_windows_downloads_folder()

    # Déterminer si c'est un téléchargement audio ou vidéo
    is_audio = "_audio" in source_type.lower()
    base_type = source_type.lower().replace("_audio", "")

    # Déterminer le dossier principal (Audio ou Video)
    main_folder = "Audio" if is_audio else "Video"

    # Créer le chemin complet selon le type de source
    if base_type == "youtube":
        path = os.path.join(downloads_folder, main_folder, "Youtube")
    elif base_type == "odysee":
        path = os.path.join(downloads_folder, main_folder, "Odysee")
    else:  # generic
        path = os.path.join(downloads_folder, main_folder, "Generic")

    # Créer les dossiers s'ils n'existent pas
    os.makedirs(path, exist_ok=True)

    return path


def update_yt_dlp():
    """Mettre à jour yt-dlp vers la version stable"""
    try:
        print("\nVérification des mises à jour pour yt-dlp...")
        print(
            "Les mises à jour régulières sont nécessaires pour contourner les changements d'API de YouTube."
        )
        # Use pip to update yt-dlp since it was installed via pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            if "already up-to-date" in result.stdout.lower() or "already satisfied" in result.stdout.lower():
                print("yt-dlp est déjà à jour.")
            else:
                print("yt-dlp a été mis à jour avec succès.")
        else:
            print(f"Erreur lors de la mise à jour de yt-dlp: {result.stderr}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de yt-dlp: {e}")


def check_and_export_cookies():
    """Vérifier si le fichier cookies.txt existe, sinon l'exporter depuis Chrome"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_file = os.path.join(script_dir, "cookies.txt")

    if os.path.exists(cookies_file):
        # Le fichier de cookies existe déjà, vérifier s'il est valide
        try:
            import http.cookiejar

            cookie_jar = http.cookiejar.MozillaCookieJar(cookies_file)
            cookie_jar.load()
            # Si on arrive ici, le fichier est valide
            print("\nFichier de cookies déjà présent et valide.")
            return
        except Exception:
            # Le fichier existe mais n'est pas valide, on va le recréer
            try:
                os.remove(cookies_file)
                print(
                    "\nFichier de cookies corrompu détecté et supprimé. Tentative de recréation..."
                )
            except Exception:
                pass

    # Si on arrive ici, soit le fichier n'existe pas, soit il était corrompu et a été supprimé
    print("\nVérification des cookies YouTube...")
    print(
        "Les cookies permettent d'accéder aux vidéos avec restriction d'âge et aux contenus privés."
    )

    # Si on arrive ici, il faut exporter les cookies
    try:
        print("\nExportation des cookies depuis Chrome...")
        # Import des modules nécessaires pour l'exportation des cookies
        import browser_cookie3
        import http.cookiejar

        # Créer un fichier de cookies vide mais valide
        cookie_jar = http.cookiejar.MozillaCookieJar(cookies_file)

        try:
            # Essayer d'abord avec Chrome
            cookies = browser_cookie3.chrome(domain_name=".youtube.com")
            for cookie in cookies:
                cookie_jar.set_cookie(cookie)
            cookie_jar.save()
            print("Cookies exportés avec succès depuis Chrome.")
        except Exception as chrome_error:
            # Si ça échoue avec Chrome, créer un fichier de cookies vide mais valide
            print(
                f"Erreur lors de l'exportation des cookies depuis Chrome: {chrome_error}"
            )
            print("Création d'un fichier de cookies vide mais valide...")

            # Créer l'en-tête du fichier cookies.txt au format Netscape
            with open(cookies_file, "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/docs/http-cookies.html\n")
                f.write(
                    "# This file was generated by yt-dlp! Edit at your own risk.\n\n"
                )

            print("Fichier de cookies vide créé avec succès.")
            print(
                "\nAttention: Sans cookies valides, les vidéos avec restriction d'âge ne seront pas accessibles."
            )
            print(
                "Vous pouvez continuer à utiliser le script pour les vidéos sans restriction."
            )
    except Exception as e:
        print(f"Erreur lors de la gestion des cookies: {e}")
        print("\nPour utiliser les cookies YouTube, vous devez:")
        print("1. Vous connecter à votre compte YouTube via le navigateur Chrome")
        print("2. Garder votre session active dans Chrome")
        print("3. Relancer ce script")
        print("\nNote: Seuls les cookies de Chrome sont supportés pour le moment.")


def check_and_install_modules():
    """Vérifier si les modules requis sont installés et les installer si nécessaire"""
    required = read_requirements()

    # Supprimer importlib-metadata de la liste des modules requis car il est intégré à Python 3.8+
    if "importlib-metadata" in required:
        required.remove("importlib-metadata")

    # Obtenir la liste des packages installés
    installed = {
        pkg.metadata["Name"].lower() for pkg in importlib.metadata.distributions()
    }
    missing = required - installed

    if missing:
        install_modules(missing)
        print("Modules manquants installés avec succès.")
    else:
        # Vérifier si une mise à jour est nécessaire (tous les 30 jours)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        last_update_file = os.path.join(script_dir, ".last_update")
        current_time = time.time()
        update_needed = True

        if os.path.exists(last_update_file):
            try:
                with open(last_update_file, "r") as f:
                    last_update = float(f.read().strip())
                    # Si la dernière mise à jour date de moins de 30 jours, pas besoin de mettre à jour
                    if (
                        current_time - last_update < 30 * 24 * 60 * 60
                    ):  # 30 jours en secondes
                        update_needed = False
            except Exception:
                pass  # En cas d'erreur, on procède à la mise à jour

        if update_needed:
            print("\nVérification périodique des modules...")
            install_modules(missing)  # missing est vide ici
            # Enregistrer la date de la mise à jour
            try:
                with open(last_update_file, "w") as f:
                    f.write(str(current_time))
            except Exception:
                pass  # Ignorer les erreurs d'écriture
        else:
            print("\nTous les modules sont à jour.")


# Vérifier et installer les modules nécessaires
try:
    check_and_install_modules()
    print("\nVérification des modules terminée avec succès.")
except Exception as e:
    print(
        f"\nAttention: Problème lors de la vérification/installation des modules: {e}"
    )
    print(
        "Le script va continuer, mais certaines fonctionnalités pourraient ne pas fonctionner correctement."
    )
    print(
        "Si vous rencontrez des erreurs, essayez d'installer manuellement les modules requis:"
    )
    print("pip install -r requirements.txt")

# Importer les modules nécessaires
try:
    import pyperclip  # type: ignore
    import yt_dlp  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
    from tqdm import tqdm  # type: ignore
    import requests  # type: ignore
except ImportError as e:
    print(f"\nErreur critique lors de l'importation des modules: {e}")
    print("Certains modules nécessaires ne sont pas disponibles.")
    print("Veuillez installer manuellement les modules requis et réessayer:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Mettre à jour yt-dlp et exporter les cookies après l'installation des modules
try:
    update_yt_dlp()
except Exception:
    print("\nAttention: Impossible de mettre à jour yt-dlp.")
    print("Le téléchargement pourrait échouer si yt-dlp n'est pas à jour.")

# Essayer d'exporter les cookies, mais continuer même en cas d'échec
try:
    check_and_export_cookies()
except Exception as e:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_file = os.path.join(script_dir, "cookies.txt")

    # Vérifier si le fichier de cookies existe malgré l'erreur
    if os.path.exists(cookies_file):
        print(
            "\nAttention: Problème lors de la vérification des cookies, mais un fichier de cookies existe."
        )
        print(
            "Le script va continuer, mais certaines vidéos avec restriction d'âge pourraient être inaccessibles."
        )
    else:
        # Créer un fichier de cookies vide mais valide
        try:
            print("\nCréation d'un fichier de cookies vide mais valide...")
            with open(cookies_file, "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/docs/http-cookies.html\n")
                f.write(
                    "# This file was generated by yt-dlp! Edit at your own risk.\n\n"
                )
            print("Fichier de cookies vide créé avec succès.")
            print(
                "\nAttention: Sans cookies valides, les vidéos avec restriction d'âge ne seront pas accessibles."
            )
            print(
                "Vous pouvez continuer à utiliser le script pour les vidéos sans restriction."
            )
        except Exception as cookie_error:
            print(f"\nErreur lors de la création du fichier de cookies: {cookie_error}")
            print(
                "Sans cookies, les vidéos avec restriction d'âge ne seront pas accessibles."
            )
            print(
                "Le script va continuer, mais certaines fonctionnalités pourraient être limitées."
            )


def detect_protected_sites(url):
    """
    Detect if the URL belongs to a protected site that requires yt-dlp specialized handling
    Returns the site type or 'generic' if not protected
    """
    protected_sites = {
        'm6.fr': 'm6',
        'www.m6.fr': 'm6',
        'm6plus.fr': 'm6',
        'www.m6plus.fr': 'm6',
        'tf1.fr': 'tf1', 
        'www.tf1.fr': 'tf1',
        'lci.tf1.fr': 'tf1',
        'france.tv': 'francetv',
        'www.france.tv': 'francetv',
        'francetvinfo.fr': 'francetv',
        'www.francetvinfo.fr': 'francetv',
        '6play.fr': 'm6',
        'www.6play.fr': 'm6',
        'tf1play.fr': 'tf1',
        'www.tf1play.fr': 'tf1',
        'pluzz.francetv.fr': 'francetv'
    }
    
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    
    for site_domain, site_type in protected_sites.items():
        if domain == site_domain or domain.endswith('.' + site_domain):
            print(f"Protected site detected: {site_type} ({domain})")
            return site_type
    
    return 'generic'


def validate_downloaded_file(filepath, expected_min_size_mb=10):
    """
    Validate that the downloaded file is complete and not just a chunk
    """
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    if file_size_mb < expected_min_size_mb:
        return False, f"File too small: {file_size_mb:.2f} MB (minimum: {expected_min_size_mb} MB)"
    
    # Try to detect if file is corrupted by checking first few bytes
    try:
        with open(filepath, 'rb') as f:
            header = f.read(100)
            if b'<html' in header.lower() or b'<!doctype' in header.lower():
                return False, "File appears to be HTML (likely error page)"
            
            # Check if file starts with typical video file headers
            video_headers = [
                b'\x00\x00\x00\x20ftyp',  # MP4
                b'\x00\x00\x00\x18ftyp',  # MP4
                b'RIFF',                  # AVI/WAV
                b'\x1a\x45\xdf\xa3',      # MKV
                b'FWS',                   # Flash Video
                b'FLV',                   # FLV
                b'\x00\x00\x00\x20ftypmp4', # MP4 variant
                b'\x00\x00\x00\x20ftypM4A', # M4A audio
                b'\x00\x00\x00\x20ftypf4v', # FLV variant
            ]
            
            is_valid_video = any(header.startswith(h) for h in video_headers)
            if not is_valid_video:
                return False, "File does not appear to be a valid video/audio format"
    
    except Exception as e:
        return False, f"Error validating file: {e}"
    
    return True, f"File validation successful: {file_size_mb:.2f} MB"


def get_available_video_qualities(available_formats):
    """
    Récupère les formats vidéo disponibles, limités à 1080p maximum.
    Retourne une liste de formats triés par qualité.
    """
    # Définir les résolutions standard à proposer
    standard_resolutions = [1080, 720, 480]

    # Préparer les options de qualité à présenter à l'utilisateur
    quality_options = []

    # Filtrer les formats qui contiennent de la vidéo (pas seulement audio)
    video_formats = [f for f in available_formats if f.get("vcodec") != "none"]

    # Extraire les hauteurs disponibles
    available_heights = set()
    for fmt in video_formats:
        height = fmt.get("height", 0)
        if (
            height > 0 and height <= 1080
        ):  # Ignorer les résolutions > 1080p et les formats sans hauteur
            available_heights.add(height)

    # Trier les hauteurs par ordre décroissant
    sorted_heights = sorted(available_heights, reverse=True)

    # Pour chaque résolution standard, vérifier si elle est disponible ou trouver la plus proche
    for res in standard_resolutions:
        # Trouver la résolution disponible la plus proche inférieure ou égale
        closest_height = None
        for height in sorted_heights:
            if height <= res:
                closest_height = height
                break

        if closest_height is None:
            continue  # Pas de résolution disponible inférieure ou égale à celle demandée

        # Créer une chaîne de format qui combine vidéo+audio pour cette résolution
        format_string = f"bestvideo[height<={res}]+bestaudio/best[height<={res}]"

        quality_options.append(
            {
                "format_string": format_string,
                "height": res,
                "display_name": f"{res}p",
                "ext": "mp4",  # On force mp4 comme format de sortie
            }
        )

        # Limiter à 3 options maximum
        if len(quality_options) >= 3:
            break

    # Si aucune option n'a été ajoutée (cas rare), ajouter une option par défaut
    if not quality_options and sorted_heights:
        height = sorted_heights[0]
        quality_options.append(
            {
                "format_string": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
                "height": height,
                "display_name": f"{height}p",
                "ext": "mp4",
            }
        )

    return quality_options


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
    """Récupère et valide l'URL ou le chemin local depuis le presse-papier"""
    print("\nRécupération de l'URL depuis le presse-papier...")
    content = pyperclip.paste()

    if not content:
        print("Le presse-papier est vide.")
        return None

    content = content.strip()
    # Supprimer les guillemets si présents
    if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
        content = content[1:-1]
    print(f"Contenu du presse-papier : '{content}'")

    if is_valid_url(content):
        if is_valid_youtube_url(content):
            print("URL YouTube valide trouvée.")
            return ("youtube", content)
        elif is_valid_odysee_url(content):
            print("URL Odysee valide trouvée.")
            return ("odysee", content)
        else:
            print("URL générique trouvée.")
            return ("generic", content)
    else:
        # Vérifier si c'est un chemin local
        if os.path.exists(content):
            print("Chemin local détecté.")
            return ("local", content)
        else:
            print("Le contenu du presse-papier n'est pas une URL valide ni un chemin local existant.")
            return None


def download_youtube_video(url):
    print("\nAnalyse de la vidéo YouTube...")

    # Demander à l'utilisateur s'il souhaite télécharger la vidéo ou seulement l'audio
    print("\nQue souhaitez-vous télécharger ?")
    print("1. Vidéo (avec audio)")
    print("2. Audio uniquement (MP3)")

    download_type = None
    while download_type is None:
        try:
            choice = input(
                "\nEntrez votre choix (1-2) ou appuyez sur Entrée pour la vidéo: "
            )
            if not choice.strip():
                download_type = "video"
            else:
                choice = int(choice)
                if choice == 1:
                    download_type = "video"
                elif choice == 2:
                    download_type = "audio"
                else:
                    print("Veuillez entrer 1 ou 2")
        except ValueError:
            print("Veuillez entrer un nombre valide")

    # Déterminer le chemin de destination en fonction du type de téléchargement
    if download_type == "video":
        local_path = get_download_path("youtube")
    else:  # audio
        local_path = get_download_path("youtube_audio")

    # Add cookies file if available
    cookies_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "cookies.txt"
    )
    use_cookies = os.path.exists(cookies_file)

    # Options pour l'extraction des informations
    info_opts = {
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "no_color": True,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "extractor_retries": 10,
        "socket_timeout": 60,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["js", "configs"],
            }
        },
    }

    # Use cookies if available
    if use_cookies:
        info_opts["cookiefile"] = cookies_file
        print(f"Utilisation du fichier de cookies: {cookies_file}")

    try:
        # Extraire les informations de la vidéo sans télécharger
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            print("Extraction des informations de la vidéo...")
            info = ydl.extract_info(url, download=False)
            video_title = info.get("title", "video")

            # Déterminer l'extension en fonction du type de téléchargement
            file_ext = ".mp3" if download_type == "audio" else ".mp4"
            filename = f"{video_title}{file_ext}"
            filepath = os.path.join(local_path, filename)

            # Vérifier si le fichier existe déjà AVANT de choisir la qualité
            file_exists = False

            try:
                # Vérifier directement si le fichier existe (méthode standard)
                if os.path.exists(filepath):
                    file_exists = True
                else:
                    # Méthode avancée: vérifier tous les fichiers du dossier en normalisant les guillemets
                    if os.path.exists(local_path):
                        # Normaliser le titre de la vidéo pour la comparaison
                        normalized_title = (
                            (video_title or "").replace('"', "")
                            .replace(
                                """, "")
                            .replace(""", 
                                "",
                            )
                            .replace("＇", "")
                        )

                        for file in os.listdir(local_path):
                            # Obtenir le nom du fichier sans extension et le normaliser
                            file_name_without_ext = os.path.splitext(file)[0]
                            normalized_file_name = (
                                file_name_without_ext.replace('"', "")
                                .replace(
                                    """, "")
                                .replace(""", 
                                    "",
                                )
                                .replace("＇", "")
                            )

                            # Comparer les noms normalisés
                            if normalized_file_name == normalized_title:
                                file_exists = True
                                # Utiliser le chemin réel du fichier trouvé
                                filepath = os.path.join(local_path, file)
                                break
            except Exception as e:
                print(f"Erreur lors de la vérification du fichier: {e}")

            if file_exists:
                print("\n" + "=" * 60)
                print(f"ATTENTION: Le fichier '{video_title}' existe déjà !")
                print(f"Chemin: {filepath}")
                print("=" * 60)

                # Demander à l'utilisateur s'il souhaite remplacer le fichier
                while True:
                    choice = input("Voulez-vous remplacer ce fichier ? (o/n): ").lower()
                    if choice in ["o", "oui", "y", "yes"]:
                        print("Le fichier existant sera remplacé.")
                        try:
                            # Supprimer le fichier existant
                            os.remove(filepath)
                            print("Fichier existant supprimé.")
                            break  # Sortir de la boucle et continuer le téléchargement
                        except Exception as e:
                            print(f"Impossible de supprimer le fichier existant: {e}")
                            return
                    elif choice in ["n", "non", "no"]:
                        print("Téléchargement annulé.")
                        return
                    else:
                        print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

            # Gérer différemment selon le type de téléchargement (vidéo ou audio)
            if download_type == "video":
                # Récupérer les formats disponibles pour la vidéo
                quality_options = get_available_video_qualities(info.get("formats", []))

                if not quality_options:
                    print(
                        "Aucun format vidéo disponible. Utilisation du format par défaut."
                    )
                    format_option = "best"
                else:
                    # Afficher les options de qualité disponibles
                    print("\nFormats vidéo disponibles:")
                    for i, option in enumerate(quality_options, 1):
                        print(f"  {i}. {option['display_name']}")

                    # Demander à l'utilisateur de choisir
                    choice = None
                    while choice is None:
                        try:
                            user_input = input(
                                "\nChoisissez la qualité (numéro) ou appuyez sur Entrée pour la meilleure qualité: "
                            )
                            if not user_input.strip():
                                choice = 1  # Meilleure qualité par défaut
                            else:
                                choice = int(user_input)
                                if choice < 1 or choice > len(quality_options):
                                    print(
                                        f"Veuillez entrer un nombre entre 1 et {len(quality_options)}"
                                    )
                                    choice = None
                        except ValueError:
                            print("Veuillez entrer un nombre valide")

                    # Récupérer le format choisi
                    selected_option = quality_options[choice - 1]
                    format_option = selected_option["format_string"]
                    print(f"\nTéléchargement en {selected_option['display_name']}...")

                # Format vidéo sélectionné

            else:  # Audio uniquement
                # Options de qualité audio
                audio_quality_options = [
                    {"bitrate": "192", "display_name": "Haute qualité (192 kbps)"},
                    {"bitrate": "128", "display_name": "Qualité standard (128 kbps)"},
                    {"bitrate": "96", "display_name": "Basse qualité (96 kbps)"},
                ]

                # Afficher les options de qualité audio
                print("\nFormats audio disponibles:")
                for i, option in enumerate(audio_quality_options, 1):
                    print(f"  {i}. {option['display_name']}")

                # Demander à l'utilisateur de choisir
                choice = None
                while choice is None:
                    try:
                        user_input = input(
                            "\nChoisissez la qualité audio (numéro) ou appuyez sur Entrée pour la meilleure qualité: "
                        )
                        if not user_input.strip():
                            choice = 1  # Meilleure qualité par défaut
                        else:
                            choice = int(user_input)
                            if choice < 1 or choice > len(audio_quality_options):
                                print(
                                    f"Veuillez entrer un nombre entre 1 et {len(audio_quality_options)}"
                                )
                                choice = None
                    except ValueError:
                        print("Veuillez entrer un nombre valide")

                # Récupérer la qualité audio choisie
                selected_audio_option = audio_quality_options[choice - 1]
                audio_bitrate = selected_audio_option["bitrate"]
                print(
                    f"\nTéléchargement audio en {selected_audio_option['display_name']}..."
                )

                # Pour l'audio, on utilise le meilleur format audio disponible
                format_option = "bestaudio/best"

                # Format audio sélectionné

            # Options pour le téléchargement
            ydl_opts = {
                "format": format_option,
                "outtmpl": os.path.join(local_path, "%(title)s.%(ext)s"),
                "ffmpeg_location": r"C:\ffmpeg\bin",
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "no_color": True,
                "geo_bypass": True,
                "geo_bypass_country": "US",
                "extractor_retries": 10,
                "socket_timeout": 60,
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"],
                        "player_skip": ["js", "configs"],
                    }
                },
            }

            # Options spécifiques selon le type de téléchargement
            if download_type == "video":
                # Pour la vidéo, forcer la sortie en MP4
                ydl_opts["merge_output_format"] = "mp4"
            else:  # Audio uniquement
                # Pour l'audio, extraire l'audio et convertir en MP3
                ydl_opts["extractaudio"] = True
                ydl_opts["audioformat"] = "mp3"
                ydl_opts["audioquality"] = audio_bitrate  # Utiliser la qualité choisie par l'utilisateur
                # Options supplémentaires pour la conversion audio
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": audio_bitrate,
                    }
                ]

            # Pas besoin de forcer le remplacement car on a déjà supprimé le fichier existant si nécessaire

            if use_cookies:
                ydl_opts["cookiefile"] = cookies_file

            # Télécharger la vidéo avec le format choisi
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                # Vérifier le fichier réel (au cas où le nom aurait été modifié par yt-dlp)
                file_ext = ".mp3" if download_type == "audio" else ".mp4"
                final_path = os.path.join(local_path, filename)

                # Si le fichier n'existe pas avec le nom prévu, chercher le fichier réel
                if not os.path.exists(final_path):
                    files = os.listdir(local_path)
                    matching_files = [
                        os.path.join(local_path, f)
                        for f in files
                        if f.endswith(file_ext)
                    ]

                    if matching_files:
                        newest_file = max(
                            matching_files, key=os.path.getctime, default=None
                        )
                        if newest_file:
                            final_path = newest_file
                    else:
                        # Si aucun fichier correspondant n'est trouvé, utiliser le dossier
                        print(
                            f"Aucun fichier {file_ext} récent trouvé, ouverture du dossier."
                        )
                        final_path = local_path

                print("Téléchargement terminé avec succès.")
                print(f"Fichier enregistré dans: {final_path}")

                # Ouvrir l'explorateur au bon endroit
                open_file_explorer(final_path)

    except Exception as e:
        print(f"Erreur avec yt-dlp : {str(e)}")
        print("Tentative avec méthode alternative...")

        # Méthode alternative avec subprocess
        try:
            # Options différentes selon le type de téléchargement
            if download_type == "video":
                # Demander à l'utilisateur de choisir la qualité vidéo pour la méthode alternative
                print("\nOptions de qualité vidéo pour la méthode alternative:")
                print("  1. Meilleure qualité (jusqu'à 1080p)")
                print("  2. Qualité moyenne (720p)")
                print("  3. Qualité basse (480p ou moins)")

                choice = None
                while choice is None:
                    try:
                        user_input = input(
                            "\nChoisissez la qualité (1-3) ou appuyez sur Entrée pour la meilleure qualité: "
                        )
                        if not user_input.strip():
                            choice = 1
                        else:
                            choice = int(user_input)
                            if choice < 1 or choice > 3:
                                print("Veuillez entrer un nombre entre 1 et 3")
                                choice = None
                    except ValueError:
                        print("Veuillez entrer un nombre valide")

                # Définir le format en fonction du choix
                format_option = (
                    "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
                    if choice == 1
                    else (
                        "bestvideo[height<=720]+bestaudio/best[height<=720]"
                        if choice == 2
                        else "bestvideo[height<=480]+bestaudio/best[height<=480]"
                    )
                )

                cmd = [
                    sys.executable,
                    "-m",
                    "yt_dlp",
                    "--format",
                    format_option,
                    "--output",
                    os.path.join(local_path, "%(title)s.%(ext)s"),
                    "--ffmpeg-location",
                    r"C:\ffmpeg\bin",
                    "--no-playlist",
                    "--no-check-certificate",
                    "--geo-bypass",
                    "--merge-output-format",
                    "mp4",
                ]

            else:  # Audio uniquement
                # Demander à l'utilisateur de choisir la qualité audio pour la méthode alternative
                print("\nOptions de qualité audio pour la méthode alternative:")
                print("  1. Haute qualité (192 kbps)")
                print("  2. Qualité standard (128 kbps)")
                print("  3. Basse qualité (96 kbps)")

                choice = None
                while choice is None:
                    try:
                        user_input = input(
                            "\nChoisissez la qualité audio (1-3) ou appuyez sur Entrée pour la meilleure qualité: "
                        )
                        if not user_input.strip():
                            choice = 1
                        else:
                            choice = int(user_input)
                            if choice < 1 or choice > 3:
                                print("Veuillez entrer un nombre entre 1 et 3")
                                choice = None
                    except ValueError:
                        print("Veuillez entrer un nombre valide")

                # Définir la qualité audio en fonction du choix
                audio_quality = (
                    "192" if choice == 1 else ("128" if choice == 2 else "96")
                )

                cmd = [
                    sys.executable,
                    "-m",
                    "yt_dlp",
                    "--format",
                    "bestaudio/best",
                    "--output",
                    os.path.join(local_path, "%(title)s.%(ext)s"),
                    "--ffmpeg-location",
                    r"C:\ffmpeg\bin",
                    "--no-playlist",
                    "--no-check-certificate",
                    "--geo-bypass",
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    audio_quality,
                ]

            # Pas besoin de forcer le remplacement car on a déjà supprimé le fichier existant si nécessaire

            if use_cookies:
                cmd.extend(["--cookies", cookies_file])

            cmd.append(url)

            print("\nTéléchargement avec la qualité sélectionnée...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Erreur subprocess: {result.stderr}")
                raise Exception(result.stderr)

            # Essayer de trouver le fichier le plus récent avec la bonne extension
            try:
                file_ext = ".mp3" if download_type == "audio" else ".mp4"
                files = os.listdir(local_path)
                matching_files = [
                    os.path.join(local_path, f) for f in files if f.endswith(file_ext)
                ]

                if matching_files:
                    newest_file = max(matching_files, key=os.path.getctime)
                    print("Téléchargement terminé avec succès.")
                    print(f"Fichier enregistré dans: {newest_file}")
                    open_file_explorer(newest_file)
                else:
                    # Si aucun fichier correspondant n'est trouvé, ouvrir le dossier
                    print("Téléchargement terminé avec succès.")
                    print(f"Fichier enregistré dans le dossier: {local_path}")
                    open_file_explorer(local_path)
            except Exception as e:
                print(f"Erreur lors de la recherche du fichier: {e}")
                print("Téléchargement terminé avec succès.")
                print(f"Fichier enregistré dans le dossier: {local_path}")
                # En cas d'erreur, ouvrir simplement le dossier
                open_file_explorer(local_path)

        except Exception as e2:
            print(f"Toutes les tentatives ont échoué. Erreur finale : {str(e2)}")
            return


def download_odysee_video(url):
    """Télécharge une vidéo depuis Odysee avec options audio/vidéo et choix de qualité"""
    print("\nAnalyse de la vidéo Odysee...")

    # Demander à l'utilisateur s'il souhaite télécharger la vidéo ou seulement l'audio
    print("\nQue souhaitez-vous télécharger ?")
    print("1. Vidéo (avec audio)")
    print("2. Audio uniquement (MP3)")

    download_type = None
    while download_type is None:
        try:
            choice = input(
                "\nEntrez votre choix (1-2) ou appuyez sur Entrée pour la vidéo: "
            )
            if not choice.strip():
                download_type = "video"
            else:
                choice = int(choice)
                if choice == 1:
                    download_type = "video"
                elif choice == 2:
                    download_type = "audio"
                else:
                    print("Veuillez entrer 1 ou 2")
        except ValueError:
            print("Veuillez entrer un nombre valide")

    # Déterminer le chemin de destination en fonction du type de téléchargement
    if download_type == "video":
        local_path = get_download_path("odysee")
    else:  # audio
        local_path = get_download_path("odysee_audio")

    # Essayer d'abord avec yt-dlp (méthode recommandée pour Odysee)
    try:
        print("Extraction des informations de la vidéo...")

        # Options pour l'extraction des informations
        info_opts = {
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "no_color": True,
            "extractor_retries": 5,
            "socket_timeout": 30,
        }

        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get("title", "video_odysee")

            # Nettoyer le titre pour le nom de fichier
            clean_title = re.sub(r'[<>:"/\\|?*]', "_", video_title or "video_odysee")

            # Déterminer l'extension en fonction du type de téléchargement
            file_ext = ".mp3" if download_type == "audio" else ".mp4"
            filename = f"{clean_title}{file_ext}"
            filepath = os.path.join(local_path, filename)

            # Vérifier si le fichier existe déjà
            if os.path.exists(filepath):
                print("\n" + "=" * 60)
                print(f"ATTENTION: Le fichier '{filename}' existe déjà !")
                print(f"Chemin: {filepath}")
                print("=" * 60)

                while True:
                    choice = input("Voulez-vous remplacer ce fichier ? (o/n): ").lower()
                    if choice in ["o", "oui", "y", "yes"]:
                        print("Le fichier existant sera remplacé.")
                        try:
                            os.remove(filepath)
                            print("Fichier existant supprimé.")
                            break
                        except Exception as e:
                            print(f"Impossible de supprimer le fichier existant: {e}")
                            return
                    elif choice in ["n", "non", "no"]:
                        print("Téléchargement annulé.")
                        return
                    else:
                        print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

            # Configuration en fonction du type de téléchargement
            if download_type == "video":
                # Récupérer les formats disponibles pour la vidéo
                available_formats = info.get("formats", [])
                quality_options = get_available_video_qualities(available_formats)

                if not quality_options:
                    print(
                        "Aucun format vidéo spécifique trouvé. Utilisation du format par défaut."
                    )
                    format_option = "best"
                else:
                    # Afficher les options de qualité disponibles
                    print("\nFormats vidéo disponibles:")
                    for i, option in enumerate(quality_options, 1):
                        print(f"  {i}. {option['display_name']}")

                    # Demander à l'utilisateur de choisir
                    choice = None
                    while choice is None:
                        try:
                            user_input = input(
                                "\nChoisissez la qualité (numéro) ou appuyez sur Entrée pour la meilleure qualité: "
                            )
                            if not user_input.strip():
                                choice = 1  # Meilleure qualité par défaut
                            else:
                                choice = int(user_input)
                                if choice < 1 or choice > len(quality_options):
                                    print(
                                        f"Veuillez entrer un nombre entre 1 et {len(quality_options)}"
                                    )
                                    choice = None
                        except ValueError:
                            print("Veuillez entrer un nombre valide")

                    # Récupérer le format choisi
                    selected_option = quality_options[choice - 1]
                    format_option = selected_option["format_string"]
                    print(f"\nTéléchargement en {selected_option['display_name']}...")

            else:  # Audio uniquement
                # Options de qualité audio
                audio_quality_options = [
                    {"bitrate": "192", "display_name": "Haute qualité (192 kbps)"},
                    {"bitrate": "128", "display_name": "Qualité standard (128 kbps)"},
                    {"bitrate": "96", "display_name": "Basse qualité (96 kbps)"},
                ]

                # Afficher les options de qualité audio
                print("\nFormats audio disponibles:")
                for i, option in enumerate(audio_quality_options, 1):
                    print(f"  {i}. {option['display_name']}")

                # Demander à l'utilisateur de choisir
                choice = None
                while choice is None:
                    try:
                        user_input = input(
                            "\nChoisissez la qualité audio (numéro) ou appuyez sur Entrée pour la meilleure qualité: "
                        )
                        if not user_input.strip():
                            choice = 1  # Meilleure qualité par défaut
                        else:
                            choice = int(user_input)
                            if choice < 1 or choice > len(audio_quality_options):
                                print(
                                    f"Veuillez entrer un nombre entre 1 et {len(audio_quality_options)}"
                                )
                                choice = None
                    except ValueError:
                        print("Veuillez entrer un nombre valide")

                # Récupérer la qualité audio choisie
                selected_audio_option = audio_quality_options[choice - 1]
                audio_bitrate = selected_audio_option["bitrate"]
                print(
                    f"\nTéléchargement audio en {selected_audio_option['display_name']}..."
                )

                # Pour l'audio, on utilise le meilleur format audio disponible
                format_option = "bestaudio/best"

            # Options pour le téléchargement
            ydl_opts = {
                "format": format_option,
                "outtmpl": os.path.join(local_path, "%(title)s.%(ext)s"),
                "ffmpeg_location": r"C:\ffmpeg\bin",
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "no_color": True,
                "extractor_retries": 5,
                "socket_timeout": 30,
            }

            # Options spécifiques selon le type de téléchargement
            if download_type == "video":
                # Pour la vidéo, forcer la sortie en MP4
                ydl_opts["merge_output_format"] = "mp4"
            else:  # Audio uniquement
                # Pour l'audio, extraire l'audio et convertir en MP3
                ydl_opts["extractaudio"] = True
                ydl_opts["audioformat"] = "mp3"
                ydl_opts["audioquality"] = audio_bitrate
                # Options supplémentaires pour la conversion audio
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": audio_bitrate,
                    }
                ]

            # Télécharger avec yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Vérifier le fichier téléchargé
            file_ext = ".mp3" if download_type == "audio" else ".mp4"
            final_path = filepath

            # Si le fichier n'existe pas avec le nom prévu, chercher le fichier réel
            if not os.path.exists(final_path):
                files = os.listdir(local_path)
                matching_files = [
                    os.path.join(local_path, f) for f in files if f.endswith(file_ext)
                ]

                if matching_files:
                    newest_file = max(
                        matching_files, key=os.path.getctime, default=None
                    )
                    if newest_file:
                        final_path = newest_file

            print("Téléchargement terminé avec succès.")
            print(f"Fichier enregistré dans: {final_path}")
            open_file_explorer(final_path)

    except Exception as e:
        print(f"Erreur avec yt-dlp pour Odysee: {str(e)}")
        print("Tentative avec la méthode alternative (parsing HTML)...")

        # Méthode alternative: parsing HTML direct (pour vidéo seulement)
        if download_type == "video":
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")

                # Extraire le titre depuis la balise title
                title_tag = soup.find("title")
                video_name = (title_tag.text if title_tag else "video_odysee") + ".mp4"
                video_name = re.sub(r'[<>:"/\\|?*]', "_", video_name)
                video_path = os.path.join(local_path, video_name)

                # Vérifier si le fichier existe déjà
                if os.path.exists(video_path):
                    print(
                        f"\nAttention: Le fichier '{video_name}' existe déjà dans '{local_path}'."
                    )
                    while True:
                        choice = input(
                            "Voulez-vous remplacer ce fichier ? (o/n): "
                        ).lower()
                        if choice in ["o", "oui", "y", "yes"]:
                            print("Le fichier existant sera remplacé.")
                            break
                        elif choice in ["n", "non", "no"]:
                            print("Téléchargement annulé.")
                            return
                        else:
                            print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

                # Chercher l'URL de la vidéo dans les métadonnées JSON-LD
                script_tag = soup.find("script", type="application/ld+json")
                if script_tag and script_tag.string:
                    json_content = json.loads(script_tag.string)
                    video_url = json_content.get("contentUrl")

                    if video_url:
                        print("Téléchargement de la vidéo...")
                        response = requests.get(video_url, stream=True)

                        with open(video_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)

                        print("Téléchargement terminé avec succès.")
                        print(f"Fichier enregistré dans: {video_path}")
                        open_file_explorer(video_path)
                    else:
                        print("URL de la vidéo non trouvée dans les métadonnées.")
                else:
                    print("Métadonnées JSON-LD non trouvées.")

            except Exception as e2:
                print(f"Erreur avec la méthode alternative: {str(e2)}")

        else:  # Audio demandé mais yt-dlp a échoué
            print("Désolé, l'extraction audio depuis Odysee nécessite yt-dlp.")
            print(
                "Veuillez réessayer ou vérifier que yt-dlp est correctement installé."
            )


def download_local_audio(file_path):
    """Extrait l'audio d'un fichier vidéo local"""
    print("\nExtraction de l'audio depuis le fichier local...")

    if not os.path.exists(file_path):
        print("Le fichier n'existe pas.")
        return

    # Déterminer le chemin de sortie
    input_dir = os.path.dirname(file_path)
    input_filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(input_filename)[0]
    output_filename = name_without_ext + ".mp3"

    # Obtenir les dossiers de base
    downloads_folder = get_windows_downloads_folder()
    video_folder = os.path.join(downloads_folder, "Video")
    audio_folder = os.path.join(downloads_folder, "Audio")

    output_path = None
    if input_dir.startswith(video_folder):
        # Obtenir le sous-dossier relatif
        relative_path = os.path.relpath(input_dir, video_folder)
        if relative_path and not relative_path.startswith('.'):
            audio_subfolder = os.path.join(audio_folder, relative_path)
            os.makedirs(audio_subfolder, exist_ok=True)
            output_path = os.path.join(audio_subfolder, output_filename)
        else:
            output_path = os.path.join(input_dir, output_filename)
    else:
        # Pas dans un dossier Video, mettre dans le même dossier
        output_path = os.path.join(input_dir, output_filename)

    # Vérifier si le fichier de sortie existe déjà
    if os.path.exists(output_path):
        print(f"\nLe fichier audio '{output_filename}' existe déjà.")
        while True:
            choice = input("Voulez-vous remplacer ce fichier ? (o/n): ").lower()
            if choice in ["o", "oui", "y", "yes"]:
                try:
                    os.remove(output_path)
                    print("Fichier existant supprimé.")
                    break
                except Exception as e:
                    print(f"Impossible de supprimer le fichier existant: {e}")
                    return
            elif choice in ["n", "non", "no"]:
                print("Extraction annulée.")
                return
            else:
                print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

    # Extraire l'audio avec ffmpeg
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
    cmd = [
        ffmpeg_path,
        "-i", file_path,
        "-vn",
        "-acodec", "mp3",
        "-ab", "192k",
        output_path
    ]

    try:
        print("Extraction en cours...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("Extraction d'audio terminée.")
            print(f"Fichier enregistré dans: {output_path}")
            open_file_explorer(output_path)
        else:
            print("Échec de l'extraction audio.")
            print(f"Erreur: {result.stderr}")
            print("Le fichier n'est peut-être pas un fichier vidéo dont on peut extraire l'audio.")
    except Exception as e:
        print(f"Erreur lors de l'extraction: {e}")


def download_protected_site_video(url, site_type):
    """
    Download video from protected sites using yt-dlp specialized handling
    Uses temporary directory to avoid yt-dlp cache issues
    """
    print(f"\nDownloading from protected site: {site_type}")
    
    # Determine final destination path
    local_path = get_download_path("generic")
    
    # Create TEMPORARY directory to avoid yt-dlp cache
    import tempfile
    import shutil
    import time
    
    temp_dir = None
    try:
        # Create unique temporary directory
        temp_dir = tempfile.mkdtemp(prefix=f"ytdl_{site_type}_")
        print(f"Using temporary directory: {temp_dir}")
        
        # Add cookies file if available
        cookies_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "cookies.txt"
        )
        use_cookies = os.path.exists(cookies_file)
        
        # Options for protected sites - FORCE fresh download in temp dir
        ydl_opts = {
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,  # Be strict for protected sites
            'no_color': True,
            'geo_bypass': True,
            'geo_bypass_country': 'FR',  # Use France for French sites
            'extractor_retries': 10,
            'socket_timeout': 60,
            'file_access_retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': False,
            'keep_fragments': False,
            'extract_flat': False,
            'write_info_json': False,
            'write_sub': False,
            'write_automatic_sub': False,
            'ignore_subtitles': True,
            'writethumbnail': False,
            'write_description': False,
            'write_duration': False,
            'write_chapters': False,
            'write_annotations': False,
            'ffmpeg_location': r"C:\ffmpeg\bin",  # Add FFmpeg path
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Output to temp dir
            'nooverwrites': True,  # Prevent yt-dlp from adding (1), (2), etc.
        }
        
        # Add site-specific options
        if site_type == 'm6':
            ydl_opts.update({
                'extractor_args': {
                    'm6': {
                        'player_client': ['android', 'web'],
                    }
                },
            })
            # Force video download with ffmpeg conversion to MP4
            ydl_opts.update({
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
        elif site_type == 'tf1':
            ydl_opts.update({
                'extractor_args': {
                    'tf1': {
                        'player_client': ['android', 'web'],
                    }
                },
            })
            ydl_opts.update({
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
        elif site_type == 'francetv':
            ydl_opts.update({
                'extractor_args': {
                    'francetv': {
                        'player_client': ['android', 'web'],
                    }
                },
            })
            ydl_opts.update({
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
        
        if use_cookies:
            ydl_opts['cookiefile'] = cookies_file
            print(f"Using cookies: {cookies_file}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info first
            print("Extracting video information...")
            info = ydl.extract_info(url, download=False)
            
            video_title = info.get("title", f"video_{site_type}")
            
            # Download the video to temporary directory
            print(f"Downloading: {video_title}")
            ydl.download([url])
            
            # Find the downloaded file in temp directory
            temp_files = [
                f for f in os.listdir(temp_dir)
                if f.endswith(('.mp4', '.m4a'))
            ]
            
            if temp_files:
                # Find the most recent video/audio file
                temp_file_path = os.path.join(temp_dir, max(temp_files, key=lambda x: os.path.getctime(os.path.join(temp_dir, x))))
                
                # FIX: Remove (1), (2), etc. from filename if yt-dlp added them
                downloaded_filename = os.path.basename(temp_file_path)
                clean_filename_from_temp = downloaded_filename
                
                # Remove numbered suffixes like (1), (2), etc. that yt-dlp may add
                import re
                pattern = r'\s*\(\d+\)\.mp4$'
                if re.search(pattern, clean_filename_from_temp):
                    clean_filename_from_temp = re.sub(pattern, '.mp4', clean_filename_from_temp)
                    print(f"Removed automatic numbering from yt-dlp filename: {downloaded_filename} -> {clean_filename_from_temp}")
                
                # Create final clean filename
                clean_final_filename = re.sub(r'[<>:"/\\|?*]', "_", clean_filename_from_temp)
                final_path = os.path.join(local_path, clean_final_filename)
                
                # Get file size for validation
                file_size_mb = os.path.getsize(temp_file_path) / (1024 * 1024)
                print(f"Downloaded file found: {downloaded_filename} ({file_size_mb:.2f} MB)")
                
                # Validate the download
                is_valid, message = validate_downloaded_file(temp_file_path)
                
                if is_valid:
                    # Check if file exists at final destination and remove if needed
                    if os.path.exists(final_path):
                        try:
                            os.remove(final_path)
                            print(f"Removed existing file at destination: {clean_final_filename}")
                        except Exception as e:
                            print(f"Warning: Cannot remove existing file at destination: {e}")
                    
                    # Move file from temp to final destination
                    shutil.move(temp_file_path, final_path)
                    
                    print("[SUCCESS] Download completed successfully!")
                    print(f"File saved in: {final_path}")
                    print(f"File size: {file_size_mb:.2f} MB")
                    open_file_explorer(final_path)
                else:
                    print(f"[WARNING] Downloaded file validation failed: {message}")
                    print("File found but appears corrupted or incomplete")
                    # Still copy to final location for manual inspection
                    if temp_file_path and os.path.exists(temp_file_path):
                        failed_filename = re.sub(r'[<>:"/\\|?*]', "_", f"{video_title}_FAILED.mp4")
                        final_path = os.path.join(local_path, failed_filename)
                        shutil.move(temp_file_path, final_path)
                        print(f"File saved in: {final_path} (for manual inspection)")
            else:
                print("[ERROR] No downloaded file found in temporary directory!")
                
    finally:
        # Always cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"Warning: Could not cleanup temp directory: {e}")


def download_generic_video_with_fallback(url):
    """
    Download video from generic URL with fallback to yt-dlp if generic method fails
    OPTIMIZED: Skip generic method for protected sites
    """
    # Check if it's a protected site FIRST - don't waste time with generic method
    site_type = detect_protected_sites(url)
    
    if site_type != 'generic':
        print(f"\nProtected site detected: {site_type} ({url})")
        print("Skipping generic method - using specialized yt-dlp...")
        
        # Use yt-dlp directly for protected sites (more efficient)
        try:
            download_protected_site_video(url, site_type)
        except Exception as e:
            print(f"Download failed for protected site: {str(e)}")
            print("Please check:")
            print("1. The URL is valid and accessible")
            print("2. Cookies are properly configured")
            print("3. Internet connection is stable")
        return
    
    # Only use generic method for truly generic/unprotected sites
    print("\nAttempting download with generic method...")
    local_path = get_download_path("generic")
    
    try:
        # Try the original generic download method
        download_generic_video(url)
        
        # Check if the downloaded file is valid
        files = [f for f in os.listdir(local_path) if f.endswith('.mp4')]
        if files:
            latest_file = os.path.join(local_path, max(files, key=lambda x: os.path.getctime(os.path.join(local_path, x))))
            is_valid, message = validate_downloaded_file(latest_file)
            
            if is_valid:
                print(f"Generic download successful: {message}")
                return
            else:
                print(f"Generic download failed validation: {message}")
                print("Falling back to yt-dlp...")
        else:
            print("No file found after generic download, falling back to yt-dlp...")
    
    except Exception as e:
        print(f"Generic download failed: {str(e)}")
        print("Falling back to yt-dlp...")
    
    # Fallback to yt-dlp for generic sites that failed
    try:
        print("\nAttempting download with yt-dlp...")
        site_type = detect_protected_sites(url)
        download_protected_site_video(url, site_type)
    except Exception as e:
        print(f"All download methods failed. Final error: {str(e)}")
        print("Please check:")
        print("1. The URL is valid and accessible")
        print("2. Cookies are properly configured")
        print("3. Internet connection is stable")


def download_generic_video(url):
    """Télécharge une vidéo depuis une URL générique"""
    print("\nTéléchargement de la vidéo depuis une URL générique...")
    local_path = get_download_path("generic")
    # Note: get_download_path crée déjà le dossier s'il n'existe pas

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("title")
        video_name = (title.text if title else "video") + ".mp4"
        video_name = re.sub(r'[<>:"/\\|?*]', "_", video_name)
        video_path = os.path.join(local_path, video_name)

        if os.path.exists(video_path):
            print(
                f"\nAttention: Le fichier '{video_name}' existe déjà dans '{local_path}'."
            )
            while True:
                choice = input("Voulez-vous remplacer ce fichier ? (o/n): ").lower()
                if choice in ["o", "oui", "y", "yes"]:
                    try:
                        os.remove(video_path)
                        print(f"Fichier existant supprimé: {video_name}")
                        break
                    except Exception as e:
                        print(f"Impossible de supprimer le fichier existant: {e}")
                        return
                elif choice in ["n", "non", "no"]:
                    print("Téléchargement annulé.")
                    return
                else:
                    print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

        # Chercher toutes les sources vidéo possibles
        video_sources = []

        # Chercher dans les balises JSON-LD
        script_tags = soup.find_all("script", type="application/ld+json")
        for script in script_tags:
            try:
                if script.string:
                    json_content = json.loads(script.string)
                    if isinstance(json_content, dict):
                        if "contentUrl" in json_content:
                            video_sources.append(
                                {"url": json_content["contentUrl"], "quality": "unknown"}
                            )
                        if "encodingFormat" in json_content:
                            for format_info in json_content.get("encodingFormat", []):
                                if isinstance(format_info, dict):
                                    url = format_info.get("contentUrl")
                                    quality = format_info.get("quality", "unknown")
                                    if url:
                                        video_sources.append(
                                            {"url": url, "quality": quality}
                                        )
            except Exception:
                continue

        # Chercher dans les balises vidéo et source
        video_tag = soup.find("video")
        if video_tag:
            if hasattr(video_tag, 'get'):
                src = video_tag.get("src")
                if src:
                    video_sources.append({"url": src, "quality": "unknown"})

                source_tags = video_tag.find_all("source")
                for source in source_tags:
                    if hasattr(source, 'get'):
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
        total_size = int(response.headers.get("content-length", 0))

        block_size = 1024 * 1024  # 1 MB

        with open(video_path, "wb") as f:
            try:
                with tqdm(
                    total=total_size, unit="B", unit_scale=True, desc=video_name
                ) as pbar:
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
                            speed = bytes_downloaded / (
                                1024 * 1024 * elapsed_time
                            )  # MB/s
                            pbar.set_postfix(speed=f"{speed:.2f} MB/s")

                print(f"\nTéléchargement terminé avec succès : {video_name}")
                print(f"Fichier enregistré dans: {video_path}")
                print(f"Taille : {total_size / (1024 * 1024):.2f} MB")
                print(f"Temps total : {time.time() - start_time:.2f} secondes")
                # NOTE: Not opening explorer here to avoid opening folders with temporary files
                # The fallback method will open explorer only if the final download succeeds

            except Exception as e:
                print(f"Erreur pendant le téléchargement : {e}")
                # Supprime le fichier partiellement téléchargé en cas d'erreur
                if os.path.exists(video_path):
                    os.remove(video_path)
                raise

    except Exception as e:
        print(f"Erreur lors du téléchargement générique : {str(e)}")
        # Nettoyer en cas d'erreur
        if 'video_path' in locals() and os.path.exists(video_path):
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
        elif type_url == "local":
            download_local_audio(url)
        else:
            # Use the new fallback method for generic URLs
            download_generic_video_with_fallback(url)
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

    print("\n===== Processus terminé =====")


if __name__ == "__main__":
    main()