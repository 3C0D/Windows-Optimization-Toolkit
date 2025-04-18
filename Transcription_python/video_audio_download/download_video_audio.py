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
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--update-to", "stable"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            if "yt-dlp is up to date" in result.stdout:
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
            except:
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
            except:
                pass  # En cas d'erreur, on procède à la mise à jour

        if update_needed:
            print("\nVérification périodique des modules...")
            install_modules(missing)  # missing est vide ici
            # Enregistrer la date de la mise à jour
            try:
                with open(last_update_file, "w") as f:
                    f.write(str(current_time))
            except:
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
except Exception as e:
    print(f"\nAttention: Impossible de mettre à jour yt-dlp: {e}")
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
                            video_title.replace('"', "")
                            .replace("“", "")
                            .replace("”", "")
                            .replace("＂", "")
                        )

                        for file in os.listdir(local_path):
                            # Obtenir le nom du fichier sans extension et le normaliser
                            file_name_without_ext = os.path.splitext(file)[0]
                            normalized_file_name = (
                                file_name_without_ext.replace('"', "")
                                .replace("“", "")
                                .replace("”", "")
                                .replace("＂", "")
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
                "ffmpeg_location": r"C:\ffmpeg\bin\ffmpeg.exe",
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "no_color": True,
                "geo_bypass": True,
                "geo_bypass_country": "US",
                "extractor_retries": 10,
                "socket_timeout": 60,
            }

            # Options spécifiques selon le type de téléchargement
            if download_type == "video":
                # Pour la vidéo, forcer la sortie en MP4
                ydl_opts["merge_output_format"] = "mp4"
            else:  # Audio uniquement
                # Pour l'audio, extraire l'audio et convertir en MP3
                ydl_opts["extractaudio"] = True
                ydl_opts["audioformat"] = "mp3"
                ydl_opts["audioquality"] = (
                    audio_bitrate  # Utiliser la qualité choisie par l'utilisateur
                )
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

            print(f"\nTéléchargement avec la qualité sélectionnée...")
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
    print("\nTéléchargement de la vidéo Odysee...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    local_path = get_download_path("odysee")
    video_name = soup.find("title").text + ".mp4"
    video_path = os.path.join(local_path, video_name)

    # Étape 1 : Vérifier si le fichier existe déjà
    if os.path.exists(video_path):
        print(
            f"\nAttention: Le fichier '{video_name}' existe déjà dans '{local_path}'."
        )
        while True:
            choice = input("Voulez-vous remplacer ce fichier ? (o/n): ").lower()
            if choice in ["o", "oui", "y", "yes"]:
                print("Le fichier existant sera remplacé.")
                break
            elif choice in ["n", "non", "no"]:
                print("Téléchargement annulé.")
                return
            else:
                print("Veuillez répondre par 'o' (oui) ou 'n' (non).")

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

        print("Téléchargement terminé avec succès.")
        print(f"Fichier enregistré dans: {video_path}")
        open_file_explorer(video_path)

    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")


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
                print(f"Taille : {total_size / (1024*1024):.2f} MB")
                print(f"Temps total : {time.time() - start_time:.2f} secondes")
                open_file_explorer(video_path)

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
