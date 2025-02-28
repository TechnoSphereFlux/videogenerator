from video_generator import VideoGenerator
import schedule
import time
import logging
from datetime import datetime
import os
import sys
from social_uploader import SocialUploader

# Configuration du logging plus détaillée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()  # Affiche aussi dans la console
    ]
)

def generate_videos():
    """Génère les vidéos pour les 3 catégories"""
    try:
        logging.info("🚀 Démarrage de la génération des vidéos")
        
        # Vérification des variables d'environnement
        logging.info("Vérification des clés API...")
        required_env_vars = ['OPENAI_API_KEY', 'DEEPL_API_KEY', 'YOUTUBE_CLIENT_SECRETS']
        for var in required_env_vars:
            if not os.getenv(var):
                raise Exception(f"❌ Variable d'environnement manquante : {var}")
            logging.info(f"✅ {var} trouvé")

        # Création du dossier pour la date du jour
        logging.info("Création des dossiers...")
        base_output_dir = "videos"
        os.makedirs(base_output_dir, exist_ok=True)
        
        generator = VideoGenerator()
        
        # Récupération des sujets tendances
        logging.info("Récupération des tendances...")
        trends = generator.get_trending_topics()
        if not trends:
            raise Exception("Impossible de récupérer les tendances")
            
        logging.info(f"Tendances trouvées : {trends}")
        
        uploader = SocialUploader()
        
        # 2. Génération des vidéos pour chaque catégorie
        for category in ["science", "crypto", "ai"]:
            try:
                category_dir = f"{base_output_dir}/{category}"
                os.makedirs(category_dir, exist_ok=True)
                
                logging.info(f"🎥 Génération de la vidéo {category}...")
                
                # Génération du script
                script = generator.generate_script(category)
                if not script:
                    raise Exception(f"Échec de la génération du script pour {category}")
                
                # Sauvegarde du script
                with open(f"{category_dir}/script.txt", "w", encoding="utf-8") as f:
                    f.write(script)
                
                # Génération de l'audio
                audio_path = f"{category_dir}/audio.mp3"
                generator.text_to_speech(script, audio_path)
                
                # Génération des images
                images_dir = f"{category_dir}/images"
                os.makedirs(images_dir, exist_ok=True)
                
                # Création de la vidéo finale
                generator.create_video(
                    images_dir=images_dir,
                    audio_path=audio_path,
                    output_path=f"{category_dir}/video_finale.mp4"
                )
                
                # Upload sur les réseaux sociaux
                video_path = f"{category_dir}/video_finale.mp4"
                title = generator.topics[category]
                description = f"Découvrez les dernières actualités sur {category}!"
                
                uploader.upload_video(video_path, title, description, category)
                
                logging.info(f"✅ Vidéo {category} générée avec succès!")
                
            except Exception as e:
                logging.error(f"❌ Erreur: {str(e)}")
                continue
        
        logging.info("✨ Génération des vidéos terminée!")
        
    except Exception as e:
        logging.error(f"❌ Erreur générale : {str(e)}")
        raise e

if __name__ == "__main__":
    generate_videos() 