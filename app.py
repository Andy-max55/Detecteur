import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import requests
import cv2
import os

# Configuration de l'apparence
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
        
        self.btn_scan = ctk.CTkButton(self.sidebar, text="SCAN WEBCAM", command=self.open_webcam, 
                                     corner_radius=10, fg_color="#2ecc71", hover_color="#27ae60")
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
        self.res_frame = ctk.CTkFrame(self, width=280, corner_radius=15)
        self.res_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        
        self.res_title = ctk.CTkLabel(self.res_frame, text="RÉSULTATS D'ANALYSE", font=("Helvetica", 16, "bold"))
        self.res_title.pack(pady=15)
        
        self.result_label = ctk.CTkLabel(self.res_frame, text="En attente...", font=("Helvetica", 14), wraplength=230)
        self.result_label.pack(pady=20)
        
        self.confiance_progress = ctk.CTkProgressBar(self.res_frame)
        self.confiance_progress.set(0)
        self.confiance_progress.pack(padx=20, pady=10)

    def process_and_send(self, file_path):
        """Envoie l'image au serveur et affiche les résultats détaillés"""
        try:
            # 1. Aperçu de l'image
            img = Image.open(file_path)
            img = img.resize((350, 250))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 250))
            self.image_label.configure(image=ctk_img, text="")
            
            self.result_label.configure(text="Analyse sécurisée en cours...", text_color="orange")
            self.update()
            
            # 2. Requête serveur
            with open(file_path, "rb") as f:
                response = requests.post("http://127.0.0.1:8000/scanner", files={"file": f})
            
            data = response.json()
            res_text = data["analyse"]["resultat"]
            conf_str = data["analyse"]["confiance"] # Contient déjà le "%" (ex: "98.5%")

            # 3. Affichage intelligent
            # Si le verdict contient "AUTHENTIQUE", on affiche en vert avec le %
            if "AUTHENTIQUE" in res_text:
                final_msg = f"✅ {res_text}\nFiabilité : {conf_str}"
                couleur = "#2ecc71" # Vert
            else:
                # Si l'IA rejette (score < 85%), on affiche en rouge
                final_msg = f"⚠️ {res_text}\nScore de certitude : {conf_str}"
                couleur = "#e74c3c" # Rouge
            
            self.result_label.configure(text=final_msg, text_color=couleur)
            
            # Mise à jour de la barre de progression (on enlève le % pour le calcul)
            valeur_progress = float(conf_str.replace("%", "")) / 100
            self.confiance_progress.set(valeur_progress)

        except Exception as e:
            self.result_label.configure(text=f"ERREUR : Connexion impossible\n({str(e)})", text_color="red")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            self.process_and_send(file_path)

    def open_webcam(self):
        """Capture via webcam avec correction pour Windows (CAP_DSHOW)"""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.result_label.configure(text="Caméra occupée ou introuvable", text_color="red")
            return

        while True:
            ret, frame = cap.read()
            if not ret: break

            cv2.putText(frame, "ESPACE : Capturer | Q : Quitter", (12, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("SCANNER DE SECURITE - IA", frame)

            key = cv2.waitKey(1)
            if key == ord(' '): # ESPACE
                temp_path = "webcam_capture.jpg"
                cv2.imwrite(temp_path, frame)
                cap.release()
                cv2.destroyAllWindows()
                self.process_and_send(temp_path)
                break
            elif key == ord('q'): # Q
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = ScannerApp()
    app.mainloop()