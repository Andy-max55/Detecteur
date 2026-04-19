import tensorflow as tf
import numpy as np
from PIL import Image
import os

# 1. Charger le modèle au démarrage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# On remonte d'un cran car ia_logic est dans /backend et le modèle est dans /ai_model
MODEL_PATH = os.path.join(BASE_DIR, "..", "ai_model", "mon_modele_cfa.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Liste des étiquettes (DOIT être dans le même ordre alphabétique que tes dossiers dans data/)
CLASSES = ["10000F", "1000F", "2000F", "5000F", "500F"] 

def analyser_billet(chemin_image):
    try:
        # 2. Préparation de l'image
        img = Image.open(chemin_image).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # 3. Prédiction réelle
        predictions = model.predict(img_array)
        index_max = np.argmax(predictions[0]) # On prend la classe avec le plus haut score
        verdict = CLASSES[index_max]
        confiance = float(predictions[0][index_max]) * 100

        return f"Billet détecté : {verdict}", round(confiance, 2)
            
    except Exception as e:
        return f"Erreur IA : {str(e)}", 0.0