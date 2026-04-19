from fastapi import FastAPI, UploadFile, File
import uvicorn
import sqlite3
import os
import shutil
# On importe la fonction d'analyse que tu as créée dans ia_logic.py
from ia_logic import analyser_billet

app = FastAPI()

# --- CONFIGURATION DES CHEMINS ---
# On récupère le dossier où se trouve ce fichier (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin vers la base de données
DB_PATH = os.path.join(BASE_DIR, "billets.db")

# Chemin vers le dossier où on va stocker les images reçues
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Création automatique du dossier uploads s'il n'existe pas
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print(f"✅ Dossier créé : {UPLOAD_DIR}")

@app.post("/scanner")
async def scanner(file: UploadFile = File(...)):
    # 1. SAUVEGARDE DE L'IMAGE
    # On définit le chemin complet du fichier (ex: backend/uploads/mon_billet.jpg)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # On écrit le contenu du fichier reçu sur le disque dur
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. ANALYSE PAR L'IA
    # On envoie le chemin de l'image à notre fonction dans ia_logic.py
    resultat, confiance = analyser_billet(file_path)

    # 3. ENREGISTREMENT DANS LA BASE DE DONNÉES
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # On insère les résultats réels de l'IA
        cursor.execute('''
            INSERT INTO historique (denomination, resultat, confiance) 
            VALUES (?, ?, ?)
        ''', (file.filename, resultat, confiance))
        
        conn.commit()
        conn.close()
        
        # 4. RÉPONSE À POSTMAN
        return {
            "statut": "Analyse terminée",
            "message": "Fichier sauvegardé et historisé",
            "analyse": {
                "resultat": resultat,
                "confiance": f"{confiance}%",
                "nom_fichier": file.filename
            }
        }
        
    except Exception as e:
        # En cas d'erreur (ex: base de données verrouillée)
        return {"erreur": f"Erreur lors de l'enregistrement : {str(e)}"}

if __name__ == "__main__":
    # On lance le serveur sur le port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)