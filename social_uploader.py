from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from instabot import Bot
from tiktok_uploader.upload import upload_video
import os

class SocialUploader:
    def __init__(self):
        self.youtube = self._setup_youtube()
        self.instagram = self._setup_instagram()
        
    def _setup_youtube(self):
        """Configure l'API YouTube"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        creds = None
        
        if os.path.exists('youtube_token.json'):
            creds = Credentials.from_authorized_user_file('youtube_token.json', SCOPES)
            
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('youtube_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('youtube_token.json', 'w') as token:
                token.write(creds.to_json())
                
        return build('youtube', 'v3', credentials=creds)
    
    def _setup_instagram(self):
        """Configure l'API Instagram"""
        try:
            bot = Bot(base_path="./config/")  # Pour éviter les conflits de session
            bot.login(
                username=os.getenv('INSTAGRAM_USERNAME'),
                password=os.getenv('INSTAGRAM_PASSWORD'),
                use_cookie=False  # Important pour GitHub Actions
            )
            return bot
        except Exception as e:
            print(f"❌ Erreur connexion Instagram: {str(e)}")
            return None
        
    def upload_video(self, video_path, title, description, category):
        """Upload la vidéo sur les différentes plateformes"""
        try:
            # Upload YouTube
            request = self.youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": ["AI", category, "trending"],
                        "categoryId": "28"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                },
                media_body=MediaFileUpload(video_path)
            )
            response = request.execute()
            print(f"✅ Vidéo uploadée sur YouTube: https://youtu.be/{response['id']}")
            
            # Upload Instagram
            if self.instagram:
                self.instagram.upload_video(video_path, caption=f"{title}\n\n{description}")
                print("✅ Vidéo uploadée sur Instagram")
            
            # Upload TikTok
            upload_video(
                filename=video_path,
                description=title,
                auth_file="tiktok_session.json"
            )
            print("✅ Vidéo uploadée sur TikTok")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'upload: {str(e)}")