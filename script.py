import subprocess

# Lancement du premier script en arrière-plan
process1 = subprocess.Popen(["python", "app/app.py"])

# Lancement du deuxième script en arrière-plan
process2 = subprocess.Popen(["python", "api.py"])

# Attendre que les deux processus s'exécutent indéfiniment
try:
    # Optionnel : attendre que les processus se terminent
    process1.wait()
    process2.wait()
except KeyboardInterrupt:
    # Si l'utilisateur interrompt (Ctrl+C), on tue les processus
    print("Interruption reçue, fermeture des scripts...")
    process1.terminate()
    process2.terminate()
