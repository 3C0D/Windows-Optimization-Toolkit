## Création de la tâche planifiée

1. Ouvre le **Planificateur de tâches** (tape dans le menu démarrer).
2. Clique sur **Créer une tâche**.
3. Onglet **Général** :
   - Donne un nom à la tâche (ex. : `Désactivation Wi-Fi si Ethernet`).
   - Coche **Exécuter avec les autorisations maximales**.
   - Configure pour **Windows 10 ou 11**.

4. Onglet **Déclencheurs** :
   - Clique sur **Nouveau**.
   - Choisis **Sur un événement**.
   - Type : **De base**.
   - Journal : `Microsoft-Windows-NetworkProfile/Operational`.
   - Source : `NetworkProfile`.
   - ID de l’événement : `10000`.
   - Clique sur OK.

5. Onglet **Actions** :
   - Clique sur **Nouveau**.
   - Action : **Démarrer un programme**.
   - Programme/script : `powershell.exe`.
   - Arguments :  
     ```
     -NoProfile -ExecutionPolicy Bypass -File "C:\chemin\vers\ton_script.ps1"
     ```
     (remplace le chemin par celui de ton script)

6. Onglet **Conditions** :
   - Décoche tout sauf **"Démarrer uniquement si une connexion réseau existe"** si tu veux.

7. Onglet **Paramètres** :
   - Coche **"Exécuter dès que possible après un déclenchement manqué"**.
   - Coche **"Redémarrer la tâche si elle échoue"**.

8. Clique sur OK pour enregistrer la tâche.
