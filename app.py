import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import requests
import cv2 # Nouveau : pour la webcam
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PRO-SCAN BILLETS V1.0 - CyberSecurity Suite")
        self.geometry("1100x600")

        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SCAN-SHIELD", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=30)
        
        # Le bouton "Nouveau Scan" ouvre maintenant la webcam
        self.btn_scan = ctk.CTkButton(self.sidebar, text="SCAN WEBCAM", command=self.open_webcam, corner_radius=10, fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_scan.pack(padx=20, pady=10)

        # --- ZONE CENTRALE ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.title_label = ctk.CTkLabel(self.main_frame, text="Analyseur de Devises par IA", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        self.image_preview = ctk.CTkFrame(self.main_frame, width=400, height=300, border_width=2, border_color="#3B8ED0")
        self.image_preview.pack(pady=10)
        self.image_label = ctk.CTkLabel(self.image_preview, text="Aucune image sélectionnée")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        self.upload_btn = ctk.CTkButton(self.main_frame, text="IMPORTER UN FICHIER", command=self.upload_image, height=40)
        self.upload_btn.pack(pady=10)

        # --- RÉSULTATS ---
        self.res_frame = ctk.CTkFrame(self, width=250, corner_radius=15)
        self.res_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        
        self.res_title = ctk.CTkLabel(self.res_frame, text="RÉSULTATS D'ANALYSE", font=("Helvetica", 16, "bold"))
        self.res_title.pack(pady=15)
        
        self.result_label = ctk.CTkLabel(self.res_frame, text="En attente...", font=("Helvetica", 14), wraplength=200)
        self.result_label.pack(pady=20)
        
        self.confiance_progress = ctk.CTkProgressBar(self.res_frame)
        self.confiance_progress.set(0)
        self.confiance_progress.pack(padx=20, pady=10)

    def process_and_send(self, file_path):
        """Fonction commune pour envoyer l'image au serveur"""
        # Afficher l'aperçu
        img = Image.open(file_path)
        img = img.resize((350, 250))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 250))
        self.image_label.configure(image=ctk_img, text="")
        
        self.result_label.configure(text="Analyse en cours...", text_color="orange")
        self.update()
        
        try:
            with open(file_path, "rb") as f:
                response = requests.post("http://127.0.0.1:8000/scanner", files={"file": f})
            
            data = response.json()
            res_text = data["analyse"]["resultat"]
            conf = data["analyse"]["confiance"].replace("%", "")
            
            self.result_label.configure(text=f"VERDICT : {res_text}", text_color="green" if "Authentique" in res_text else "red")
            self.confiance_progress.set(float(conf) / 100)
        except Exception as e:
            self.result_label.configure(text="Erreur connexion serveur", text_color="red")

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.process_and_send(file_path)

    def open_webcam(self):
        """Ouvre une fenêtre de capture vidéo"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.result_label.configure(text="Caméra introuvable", text_color="red")
            return

        while True:
            ret, frame = cap.read()
            if not ret: break

            # Afficher des instructions sur le flux vidéo
            cv2.putText(frame, "Placez le billet et appuyez sur ESPACE", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Appuyez sur Q pour quitter", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow("SCANNER WEBCAM - IA", frame)

            key = cv2.waitKey(1)
            if key == ord(' '): # ESPACE pour capturer
                temp_path = "webcam_capture.jpg"
                cv2.imwrite(temp_path, frame)
                cap.release()
                cv2.destroyAllWindows()
                self.process_and_send(temp_path)
                break
            elif key == ord('q'): # Q pour quitter
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = ScannerApp()
    app.mainloop()