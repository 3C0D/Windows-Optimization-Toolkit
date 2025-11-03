# Guide de Migration UV - Video/Audio Downloader

## 1. Qu'est-ce qu'UV et pourquoi migrer ?

UV est un gestionnaire de projets Python rapide et moderne développé par Astral. Il offre une alternative plus efficace aux outils traditionnels comme pip, venv et Poetry.

### Pourquoi migrer vers UV ?

- **Performance** : Jusqu'à 10-100x plus rapide que pip/venv
- **Simplicité** : Un seul outil pour gérer les dépendances et l'environnement
- **Compatibilité** : Fonctionne avec les fichiers `requirements.txt` existants
- **Fiabilité** : Résolution de dépendances plus robuste
- **Modernité** : Designed pour les workflows de développement actuels

## 2. Avantages d'utiliser UV

### Performance
```bash
# Ancien: pip install (lent)
pip install -r requirements.txt

# Nouveau: uv sync (rapide)
uv sync
```

### Gestion simplifiée
```bash
# Ancien: plusieurs étapes
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Nouveau: une seule commande
uv sync
```

### Exécution des scripts
```bash
# Ancien: activation manuelle
venv\Scripts\activate
python script.py

# Nouveau: exécution directe
uv run python script.py
```

## 3. Ce qui a changé dans ce projet

### Avant (Méthode traditionnelle)
Le fichier `video_audio_download.bat` utilisait :
- Création manuelle d'un environnement virtuel avec `python -m venv`
- Activation de l'environnement avec `call venv\Scripts\activate`
- Installation des dépendances avec `pip install -r requirements.txt`

### Après (Méthode UV)
Le nouveau `video_audio_download.bat` utilise :
- Vérification de l'installation UV
- Synchronisation automatique des dépendances avec `uv sync`
- Exécution directe du script avec `uv run python`

### Fichiers modifiés
- **`video_audio_download.bat`** : Entièrement rewritten pour utiliser UV
- **Aucun changement** pour les autres fichiers du projet

## 4. Comment utiliser le projet maintenant

### Prérequis
1. Installer UV sur votre système :
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

### Utilisation
1. **Lancement simple** :
   Double-cliquez sur `video_audio_download.bat`

2. **Lancement manuel** (optionnel) :
   ```bash
   # Installer/mettre à jour les dépendances
   uv sync

   # Exécuter le script
   uv run python download_video_audio.py
   ```

### Structure des fichiers
```
video_audio_download/
├── video_audio_download.bat     # Script principal (mis à jour)
├── download_video_audio.py      # Script Python (inchangé)
├── requirements.txt             # Dépendances (inchangé)
├── uv.lock                      # Nouveau: lock file UV
├── .venv/                       # Nouveau: environnement virtuel géré par UV
└── pyproject.toml              # Nouveau: configuration UV (créé automatiquement)
```

## 5. Dépannage

### UV n'est pas installé
**Erreur** : `[ERROR] UV is not installed!`

**Solution** :
```powershell
# Installer UV avec PowerShell (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Redémarrer le terminal après installation
```

### Problèmes de dépendances
**Erreur** : Conflits de versions ou dépendances manquantes

**Solutions** :
```bash
# Re-synchroniser l'environnement
uv sync --refresh

# Nettoyer et recréer l'environnement
uv sync --no-cache
```

### Permissions (Windows)
**Erreur** : Problèmes d'exécution du script batch

**Solution** :
1. Clic droit sur `video_audio_download.bat`
2. Sélectionner "Exécuter en tant qu'administrateur"

### Vérification de l'installation
```bash
# Vérifier qu'UV fonctionne
uv --version

# Vérifier l'environnement
uv run python --version
```

## 6. Comparaison : Avant vs Après

| Aspect | Avant (venv traditionnel) | Après (UV) |
|--------|---------------------------|------------|
| **Installation** | `pip install` | `uv sync` |
| **Création venv** | `python -m venv venv` | Automatique |
| **Activation** | `venv\Scripts\activate` | Pas besoin |
| **Exécution** | `python script.py` | `uv run python script.py` |
| **Vitesse** | Lente | Très rapide |
| **Cache** | pip cache | UV cache optimisé |
| **Gestion venv** | Manuel | Automatique |
| **Compatibilité** | requirements.txt | requirements.txt + pyproject.toml |

### Exemple concret d'utilisation

**Avant** :
```batch
@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python download_video_audio.py
deactivate
pause
```

**Après** :
```batch
@echo off
uv sync
uv run python download_video_audio.py
pause
```

## 7. Commandes UV utiles

```bash
# Installer/mettre à jour toutes les dépendances
uv sync

# Installer une nouvelle dépendance
uv add nom-du-package

# Supprimer une dépendance
uv remove nom-du-package

# Exécuter un script
uv run python script.py

# Ouvir un shell dans l'environnement UV
uv run --nom run

# Mettre à jour les dépendances
uv sync --upgrade

# Vérifier les dépendances obsolètes
uv pip list --outdated
```

## 8. Migration depuis d'autres outils

### Depuis pip + venv
La migration est transparente. UV lit automatiquement `requirements.txt`.

### Depuis Poetry
```bash
# Convertir un projet Poetry vers UV
uv init --python 3.11
uv add $(poetry export -f requirements.txt --without-hashes)
```

### Depuis pipenv
```bash
# Les Pipfile.lock peuvent être convertis
uv add $(cat requirements.txt)
```

## 9. Performance et optimisations

### Cache UV
UV utilise un cache intelligent qui accélère considérablement les installations répétées.

### Résolution de dépendances
UV résout les dépendances plus rapidement et avec plus de précision que pip.

### Environnement virtuel
Les environnements UV sont plus compacts et optimisés.

## 10. Support et ressources

- **Documentation officielle** : https://docs.astral.sh/uv/
- **Guide d'installation** : https://docs.astral.sh/uv/getting-started/installation/
- **Exemples et tutoriels** : https://github.com/astral-sh/uv/tree/main/docs

---

## Résumé

Cette migration vers UV simplifie considérablement l'utilisation du projet tout en améliorant les performances. Les utilisateurs n'ont plus besoin de gérer manuellement les environnements virtuels, et les dépendances sont installées et synchronisées beaucoup plus rapidement.

**Prochaines étapes** :
1. Installer UV si ce n'est pas déjà fait
2. Tester le nouveau script `video_audio_download.bat`
3. Profiter de la rapidité et simplicité d'UV !