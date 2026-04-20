import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import os

# 1. CONFIGURATION DES CHEMINS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "vrai_billets")

# 2. DATA AUGMENTATION AGRESSIVE
# On crée des milliers de variantes pour que l'IA devienne "intelligente"
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,       # 20% des photos pour le test final
    rotation_range=50,          # Rotation forte
    width_shift_range=0.3,      # Décalage latéral
    height_shift_range=0.3,     # Décalage vertical
    shear_range=0.2,            # Déformation
    zoom_range=0.4,             # Gros zoom (pour les détails)
    brightness_range=[0.6, 1.4], # Simulation ombre et lumière forte
    horizontal_flip=True,       # Retourne le billet
    fill_mode='nearest'
)

# Chargement des images
train_gen = datagen.flow_from_directory(
    DATA_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_gen = datagen.flow_from_directory(
    DATA_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Affiche l'ordre des classes (IMPORTANT pour ton ia_logic.py)
print("\n--- ORDRE DES CLASSES APPRIS ---")
labels = (train_gen.class_indices)
labels = dict((v,k) for k,v in labels.items())
print(labels)
print("--------------------------------\n")

# 3. CONSTRUCTION DU CERVEAU (TRANSFER LEARNING)
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False # On utilise l'intelligence de Google

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5), # Sécurité pour ne pas apprendre par coeur
    layers.Dense(256, activation='relu'),
    layers.Dense(len(train_gen.class_indices), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 4. ENTRAÎNEMENT (50 ÉPOQUES)
# On augmente le nombre d'étapes pour une précision maximale
print("Lancement de l'entraînement lourd...")
model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=50,
    verbose=1
)

# 5. SAUVEGARDE
os.makedirs("ai_model", exist_ok=True)
model.save("ai_model/mon_modele_cfa.h5")
print("\n✅ CERVEAU RÉGÉNÉRÉ AVEC SUCCÈS !")