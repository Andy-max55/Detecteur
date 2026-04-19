import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import os

# 1. CONFIGURATION
DATA_PATH = "data/vrai_billets" # Chemin vers tes dossiers 500F, 1000F, etc.
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# 2. PRÉPARATION DES IMAGES (Data Augmentation)
# On va créer des variantes de tes photos (rotation, zoom) pour que l'IA soit plus robuste
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2, # 20% des photos servent pour l'examen final
    rotation_range=20,
    horizontal_flip=True
)

train_generator = datagen.flow_from_directory(
    DATA_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = datagen.flow_from_directory(
    DATA_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# 3. CRÉATION DU MODÈLE (Transfer Learning)
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False # On garde les connaissances de base figées

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    # On crée autant de sorties qu'il y a de dossiers (500, 1000, 2000...)
    layers.Dense(train_generator.num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 4. ENTRAÎNEMENT
print("Début de l'entraînement...")
model.fit(train_generator, validation_data=val_generator, epochs=10)

# 5. SAUVEGARDE
if not os.path.exists("ai_model"):
    os.makedirs("ai_model")

model.save("ai_model/mon_modele_cfa.h5")
print("✅ Entraînement terminé ! Modèle sauvegardé dans ai_model/mon_modele_cfa.h5")