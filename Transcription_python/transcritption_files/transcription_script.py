# https://github.com/MahmoudAshraf97/whisper-diarization

import sys
import subprocess
import importlib.metadata
import os

def read_requirements(file_path):
    """Lire les packages requis dans le fichier de requirements"""
    required_packages = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                package_name = line.split('==')[0].split('<')[0].split('>')[0].strip()
                required_packages.add(package_name.lower())
    return required_packages

def install_modules(venv_path, requirements_file):
    """Installer les modules requis dans l'environnement virtuel"""
    pip_path = os.path.join(venv_path, 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join(venv_path, 'bin', 'pip')
    subprocess.check_call([pip_path, 'install', '-r', requirements_file])

def check_and_install_modules(required):
    """Vérifier si les modules requis sont installés et les installer si nécessaire"""
    installed = {pkg.metadata['Name'].lower() for pkg in importlib.metadata.distributions()}    
    missing = required - installed
    if not missing:
        return

    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')    
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    install_modules(venv_path, requirements_path)
    
    print("Modules installés avec succès dans l'environnement virtuel.")

script_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(script_dir, 'requirements.txt')
required_modules = read_requirements(requirements_path)

try:
    check_and_install_modules(required_modules)
except Exception as e:
    print(f"Erreur lors de l'installation des modules : {e}")

try:
    import warnings
    import whisper
    import pyperclip
    import yt_dlp
    import json
    from bs4 import BeautifulSoup
    import requests
    from pydub import AudioSegment
    import numpy as np
    from googletrans import Translator
    import re
except ImportError as e:
    print(f"Erreur lors de l'importation des modules : {e}")
    print("Assurez-vous que tous les modules sont installés et essayez à nouveau.")

# Filtrer les avertissements spécifiques
warnings.filterwarnings("ignore", category=UserWarning, module='whisper')
warnings.filterwarnings("ignore", message=r"You are using `torch\.load` with `weights_only=False`")

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?' \
                    r'(youtube|youtu|youtube-nocookie)\.(com|be)/' \
                    r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return bool(re.match(youtube_regex, url))

def is_valid_odysee_url(url):
    odysee_regex = r'https?://odysee\.com/([a-zA-Z0-9\-_@:]+)'
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
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        return video_id.group(1) if video_id else None
    if is_valid_odysee_url(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.find('title').text
    print("Impossible d'extraire l'ID de la vidéo.")
    return None

def download_youtube_audio(url):
    print("\nTéléchargement de l'audio YouTube...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'temp_audio.%(ext)s',
        'ffmpeg_location': r"C:\ffmpeg\bin\ffmpeg.exe",
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print("Téléchargement terminé.")
            return 'temp_audio.mp3', info['title']
    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")
        return None, None

def download_odysee_video(url):
    print("\nTéléchargement de la vidéo Odysee...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', type='application/ld+json')
    json_content = json.loads(script_tag.string)
    video_url = json_content.get('contentUrl')
    
    response = requests.get(video_url, stream=True)
    video_path = 'temp_video.mp4'
    
    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192): 
            if chunk:
                f.write(chunk)
    
    print("Téléchargement terminé.")
    return video_path

def convert_video_to_audio(video_path):
    print("\nConversion de la vidéo en audio...")
    audio_path = 'temp_audio.mp3'
    audio = AudioSegment.from_file(video_path)
    audio.export(audio_path, format='mp3')
    print("Conversion terminée.")
    return audio_path

def download_odysee_audio(url):
    video_path = download_odysee_video(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_title = soup.find('title').text
    audio_path = convert_video_to_audio(video_path)
    
    # os.remove(video_path)
    
    return audio_path, video_title

def transcribe_audio(audio_path):
    """Transcrire l'audio en texte"""
    if not audio_path:
        return None

    try:
        print("\nChargement du modèle de transcription...")
        model = whisper.load_model("small")
        # model = whisper.load_model("tiny")
        print("\nTranscription de l'audio en cours...")
        result = model.transcribe(audio_path, task="transcribe")
        print("Transcription terminée.")
    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        return None

    os.remove(audio_path)

    return result['text']

def detect_language(text, verbose=True):
    if verbose:
        print("\nDétection de la langue...")
    translator = Translator()
    try:
        detected = translator.detect(text[:1000])
        if verbose:
            print(f"Langue détectée : {detected.lang}")
        return detected.lang
    except Exception as e:
        if verbose:
            print(f"Erreur lors de la détection de la langue : {e}")
        return None


def translate_text(text, target_lang="fr"):
    if not text:
        return None
    
    source_lang = detect_language(text, True)
    if source_lang == target_lang:
        print(f"Le texte est déjà en {target_lang}. Aucune traduction nécessaire.")
        return text

    print("\nTraduction du texte en cours...")
    translator = Translator()
    max_chunk_size = 5000
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    translated_chunks = []
    for chunk in chunks:
        try:
            translated = translator.translate(chunk, src=source_lang, dest=target_lang)
            translated_chunks.append(translated.text)
        except Exception as e:
            print(f"Erreur lors de la traduction : {e}")
            return None
    
    print("Traduction terminée.")
    return " ".join(translated_chunks)

def save_transcription(text, filename):
    """Sauvegarder la transcription dans un fichier"""
    if not text:
        print("Aucun texte à sauvegarder.")
        return
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename_safe = re.sub(r'[^\w\s.-]', '', filename)
    full_path = os.path.join(parent_dir, filename_safe)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Transcription sauvegardée dans {full_path}")

#fonction pour générer le fichier traduit
def generate_translated_file(transcription ,detected_lang, video_id, video_title):
    """Générer le fichier traduit"""
    target_lang = {"fr": "en", "en": "fr"}
    translated_text = translate_text(transcription, target_lang[detected_lang])
    if translated_text:
        translated_text = re.sub(r'([.!?...])(\S)', r'\1 \2', translated_text)
        filename_translated = f"{video_id}_{video_title[:30]}_{target_lang[detected_lang].upper()}.txt"
        filename_translated = re.sub(r'[^\w\-_\. ]', '_', filename_translated)
        print("filename_translated", filename_translated)
        save_transcription(translated_text, filename_translated)

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
            audio_file, video_title = download_youtube_audio(url)
        except Exception as e:
            print(f"Erreur lors du téléchargement de l'audio YouTube : {e}")
            return
    elif "odysee.com" in url:
        try:
            audio_file, video_title = download_odysee_audio(url)
        except Exception as e:
            print(f"Erreur lors du téléchargement de l'audio Odysee : {e}")
            return

    if not audio_file:
        print("Impossible de télécharger l'audio. Le programme s'arrête.")
        return

    transcription = transcribe_audio(audio_file)
    if not transcription:
        print("La transcription n'a pas pu être effectuée. Le programme s'arrête.")
        return

    detected_lang = detect_language(transcription)

    filename_original = f"{video_id}_{video_title[:30]}_{detected_lang.upper()}.txt"
    transcription = transcription.strip()
    save_transcription(transcription, filename_original)
    print(f"\nTranscription originale sauvegardée sous : {filename_original}")

    generate_translated_file(transcription, detected_lang, video_id, video_title)

    print("\n===== Processus terminé =====")

if __name__ == "__main__":
    main()
