from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from instabot import Bot
from tiktok_uploader.upload import upload_video
import os
import json
import logging

class SocialUploader:
    def __init__(self):
        try:
            self.youtube = self._setup_youtube()
        except Exception as e:
            logging.error(f"❌ Impossible d'initialiser YouTube: {str(e)}")
            self.youtube = None
            
        try:
            self.instagram = self._setup_instagram()
        except Exception as e:
            logging.error(f"❌ Impossible d'initialiser Instagram: {str(e)}")
            self.instagram = None
        
    def _setup_youtube(self):
        """Configure YouTube API - désactivé pour GitHub Actions"""
        logging.info("🌐 YouTube upload désactivé dans l'environnement GitHub Actions")
        return None
    
    def _setup_instagram(self):
        """Configure l'API Instagram"""
        try:
            logging.info("📸 Tentative de connexion à Instagram...")
            bot = Bot(base_path="./config/")
            bot.login(
                username=os.getenv('INSTAGRAM_USERNAME'),
                password=os.getenv('INSTAGRAM_PASSWORD'),
                use_cookie=False
            )
            return bot
        except Exception as e:
            logging.error(f"❌ Erreur connexion Instagram: {str(e)}")
            return None
        
    def upload_video(self, video_path, title, description, category):
        """Upload la vidéo sur les différentes plateformes"""
        # Sauvegarde la vidéo générée
        save_path = f"videos/{category}_video.mp4"
        try:
            import shutil
            shutil.copy(video_path, save_path)
            logging.info(f"✅ Vidéo sauvegardée dans {save_path}")
        except Exception as e:
            logging.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
            
        # YouTube (désactivé pour GitHub Actions)
        logging.info(f"ℹ️ Upload YouTube désactivé (environnement GitHub Actions)")
        
        # Instagram (tentative)
        if self.instagram:
            try:
                self.instagram.upload_video(video_path, caption=f"{title}\n\n{description}")
                logging.info("✅ Vidéo uploadée sur Instagram")
            except Exception as e:
                logging.error(f"❌ Erreur upload Instagram: {str(e)}")
        
        # TikTok (tentative)
        try:
            if os.path.exists("tiktok_session.json"):
                upload_video(
                    filename=video_path,
                    description=title,
                    auth_file="tiktok_session.json"
                )
                logging.info("✅ Vidéo uploadée sur TikTok")
            else:
                logging.warning("⚠️ Fichier de session TikTok non trouvé")
        except Exception as e:
            logging.error(f"❌ Erreur upload TikTok: {str(e)}")
            
        logging.info(f"🎬 Processus terminé pour {category} - vidéo disponible dans {save_path}")