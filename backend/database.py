import sqlite3
import os

def init_db():
    # On s'assure de créer la base dans le bon dossier
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "billets.db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # On crée la table avec TOUTES les colonnes nécessaires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            denomination TEXT, 
            resultat TEXT,
            confiance REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de données remise à neuf avec la colonne denomination !")

if __name__ == "__main__":
    init_db()