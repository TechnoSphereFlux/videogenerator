import openai
import requests
import deepl
from moviepy.editor import *
import os
from dotenv import load_dotenv
import math
from PIL import Image
import io
from moviepy.config import change_settings
from gtts import gTTS
from pytrends.request import TrendReq
import datetime
import logging

# Configuration de MoviePy
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

# Chargement des variables d'environnement
load_dotenv()

# Configuration des clés API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = "0Nd2ZIJSJHGRp1x4cBwauCPuCIH08CexznNpsuAw1sIbTaLH4wHRMN3d"
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

class VideoGenerator:
    def __init__(self):
        # Configuration la plus simple possible du client OpenAI
        self.client = openai.OpenAI(
            api_key=OPENAI_API_KEY
        )
        
        self.topics = {
            "science": "Les exoplanètes habitables découvertes en 2024",
            "crypto": "L'impact des ETF Bitcoin sur le marché crypto",
            "ai": "Les dernières avancées de l'IA générative multimodale"
        }

    def generate_script(self, topic_type):
        """Génère un script pour la vidéo"""
        try:
            prompt = f"""Écris un script captivant pour TikTok sur : 
            {self.topics[topic_type]}. 

            Règles importantes:
            - Écris UNIQUEMENT le texte à dire, sans indications scéniques
            - Pas de "Texte à l'écran", "Intervenant :", "(excité)", etc.
            - Pas de formatage ou de mise en page spéciale
            
            Structure:
            - Une introduction accrocheuse (2-3 phrases)
            - 3-4 points principaux avec des détails intéressants
            - Une conclusion avec call-to-action

            Le script doit être en anglais, avoir un ton dynamique et durer environ 45-60 secondes.
            Utilise un langage simple et direct, avec des phrases courtes pour faciliter la lecture des sous-titres."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert en création de contenu viral pour TikTok. Génère uniquement le texte à dire, sans indications de mise en scène ou formatage."},
                    {"role": "user", "content": prompt}
                ]
            )
            script = response.choices[0].message.content
            print(f"\n--- Script généré pour {topic_type} ---\n{script}\n")
            return script
            
        except openai.AuthenticationError:
            print("❌ Erreur d'authentification OpenAI - Vérifiez votre clé API")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la génération du script: {str(e)}")
            return None

    def text_to_speech(self, text, output_path):
        """Convertit le texte en voix avec Google TTS"""
        try:
            # Création de l'objet gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Sauvegarde du fichier audio
            tts.save(output_path)
            print(f"✅ Audio généré avec succès: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la génération audio: {str(e)}")
            return False

    def get_image(self, keyword, output_path):
        """Récupère une image depuis Unsplash"""
        url = f"https://api.unsplash.com/photos/random?query={keyword}&client_id={UNSPLASH_ACCESS_KEY}"
        response = requests.get(url).json()
        img_url = response["urls"]["regular"]

        img_data = requests.get(img_url).content
        with open(output_path, "wb") as f:
            f.write(img_data)

    def get_multiple_images(self, keyword, count, output_dir):
        """Récupère plusieurs images depuis Pexels et les formate pour TikTok"""
        images = []
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={keyword}&orientation=portrait&per_page={count}"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Erreur API Pexels: {response.status_code}")
                return []
                
            data = response.json()
            for i, photo in enumerate(data["photos"][:count]):
                img_url = photo["src"]["large2x"]  # Haute qualité
                output_path = f"{output_dir}/image_{keyword}_{i+1}.jpg"
                
                # Téléchargement et redimensionnement
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img = Image.open(io.BytesIO(img_response.content))
                    
                    # Format TikTok
                    target_width = 1080
                    target_height = 1920
                    
                    # Redimensionnement avec ratio
                    img_ratio = img.width / img.height
                    target_ratio = target_width / target_height
                    
                    if img_ratio > target_ratio:
                        new_width = int(target_height * img_ratio)
                        new_height = target_height
                        img = img.resize((new_width, new_height))
                        left = (new_width - target_width) // 2
                        img = img.crop((left, 0, left + target_width, target_height))
                    else:
                        new_width = target_width
                        new_height = int(target_width / img_ratio)
                        img = img.resize((new_width, new_height))
                        top = (new_height - target_height) // 2
                        img = img.crop((0, top, target_width, top + target_height))
                    
                    img.save(output_path, quality=95)
                    images.append(output_path)
                    print(f"✅ Image {i+1} pour '{keyword}' téléchargée et formatée (1080x1920)")
            
            return images
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement des images: {str(e)}")
            return []

    def split_into_subtitles(self, text, max_chars=50):
        """Découpe le texte en sous-titres courts basés sur le nombre de caractères"""
        sentences = text.split('.')
        subtitles = []
        
        current_subtitle = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Si la phrase est très courte, on l'ajoute directement
            if len(sentence) <= max_chars:
                subtitles.append(sentence)
                continue
            
            # Sinon, on découpe en morceaux logiques
            words = sentence.split()
            current_part = []
            
            for word in words:
                current_part.append(word)
                current_text = ' '.join(current_part)
                
                # Si on dépasse la limite ou si on a une ponctuation naturelle
                if len(current_text) >= max_chars or any(p in word for p in [',', '!', '?', ';']):
                    subtitles.append(current_text)
                    current_part = []
                
            # Ajouter les mots restants
            if current_part:
                subtitles.append(' '.join(current_part))
        
        return subtitles

    def create_video(self, images_dir, audio_path, output_path):
        """Crée la vidéo finale avec sous-titres"""
        try:
            # Chargement de l'audio
            audio = AudioFileClip(audio_path)
            
            # Récupération des images
            image_files = sorted([f for f in os.listdir(images_dir) if f.endswith('.jpg')])
            if not image_files:
                raise Exception("Aucune image trouvée dans le dossier")
            
            # Création des clips d'images
            image_clips = []
            duration_per_image = 4.0
            current_time = 0
            
            for img_file in image_files:
                img_path = os.path.join(images_dir, img_file)
                img_clip = (ImageClip(img_path)
                           .set_duration(duration_per_image)
                           .set_start(current_time))
                image_clips.append(img_clip)
                current_time += duration_per_image
            
            # Création de la vidéo de base
            video = concatenate_videoclips(image_clips).set_audio(audio)
            
            # Chargement et découpage des sous-titres
            with open('test/traductions/science_fr.txt', 'r', encoding='utf-8') as f:
                text = f.read()
            subtitles = self.split_into_subtitles(text)
            
            # Calcul intelligent du timing des sous-titres
            total_duration = audio.duration
            avg_reading_time = 0.4  # Augmenté à 400ms par mot
            min_duration = 2.0      # Durée minimum augmentée à 2 secondes
            
            subtitle_clips = []
            current_time = 0
            
            for subtitle in subtitles:
                # Calcul de la durée basée sur le nombre de mots et caractères
                words_count = len(subtitle.split())
                chars_count = len(subtitle)
                
                # Durée calculée en fonction des mots ET des caractères
                word_duration = words_count * avg_reading_time
                char_duration = chars_count * 0.05  # 50ms par caractère
                
                # On prend la plus grande des deux durées
                duration = max(word_duration, char_duration, min_duration)
                
                # Ajout d'une pause entre les phrases
                if subtitle.strip().endswith(('.', '!', '?')):
                    duration += 0.5  # Pause de 0.5 seconde après chaque phrase
                
                # Ajustement pour ne pas dépasser la durée totale
                if current_time + duration > total_duration:
                    duration = total_duration - current_time
                
                if duration <= 0:  # Skip si plus de temps disponible
                    break
                
                txt_clip = (TextClip(subtitle,
                                   fontsize=90,
                                   color='white',
                                   bg_color='rgba(0,0,0,0.8)',
                                   font='Arial-Bold',
                                   size=(video.w * 0.95, None),
                                   method='caption',
                                   stroke_color='black',
                                   stroke_width=3)
                           .set_start(current_time)
                           .set_duration(duration)
                           .set_pos(('center', 'bottom')))
                
                subtitle_clips.append(txt_clip)
                current_time += duration
            
            # Assemblage final
            final = CompositeVideoClip([video] + subtitle_clips)
            final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
            print(f"✅ Vidéo générée avec succès: {output_path}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la vidéo: {str(e)}")

    def get_subtitles(self, audio_path):
        """Génère et traduit les sous-titres"""
        # Temporairement, on retourne un texte fixe pour tester
        text = "This is a placeholder for the transcribed text"
        
        translator = deepl.Translator(DEEPL_API_KEY)
        return translator.translate_text(text, target_lang="FR").text

    def generate_all_videos(self):
        """Génère les 3 vidéos"""
        for topic in self.topics:
            print(f"Génération de la vidéo sur {topic}...")
            
            # Création des chemins de fichiers
            base_path = f"output/{topic}"
            os.makedirs(base_path, exist_ok=True)
            
            # Génération du contenu
            script = self.generate_script(topic)
            self.text_to_speech(script, f"{base_path}/audio.mp3")
            self.get_image(topic, f"{base_path}/image.jpg")
            self.create_video(
                f"{base_path}/image.jpg",
                f"{base_path}/audio.mp3",
                f"{base_path}/final.mp4"
            )
            print(f"Vidéo {topic} générée avec succès!")

    def test_script_generation(self):
        """Teste la génération de scripts pour tous les topics"""
        print("🚀 Test de génération des scripts...")
        
        for topic in self.topics:
            print(f"\n📝 Génération pour le topic: {topic}")
            script = self.generate_script(topic)
            if script:
                print("✅ Génération réussie!")
            else:
                print("❌ Échec de la génération")

    def test_translation(self):
        """Teste la traduction avec DeepL"""
        print("\n🌍 Test de traduction DeepL...")
        
        test_text = "Discover the fascinating world of exoplanets! Scientists have recently found three Earth-like planets that could potentially harbor life."
        
        try:
            translator = deepl.Translator(DEEPL_API_KEY)
            translated = translator.translate_text(test_text, target_lang="FR")
            print("\n✨ Texte original:")
            print(test_text)
            print("\n✨ Traduction:")
            print(translated.text)
            print("\n✅ Test de traduction réussi!")
            return True
            
        except deepl.exceptions.AuthenticationException:
            print("❌ Erreur d'authentification DeepL - Vérifiez votre clé API")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la traduction: {str(e)}")
            return False

    def test_subtitles_split(self):
        """Teste le découpage des sous-titres"""
        print("\n📝 Test de découpage des sous-titres...")
        
        test_text = "Découvrez le monde fascinant des exoplanètes ! Les scientifiques ont récemment découvert trois planètes semblables à la Terre qui pourraient potentiellement abriter la vie."
        
        subtitles = self.split_into_subtitles(test_text)
        print("\n✨ Sous-titres découpés:")
        for idx, subtitle in enumerate(subtitles, 1):
            print(f"{idx}. {subtitle}")
        
        return True

    def test_science_content(self):
        """Teste la génération complète pour le topic science"""
        test_dirs = ['test/textes', 'test/traductions', 'test/sous-titres', 'test/images', 'test/audio']
        for dir_path in test_dirs:
            os.makedirs(dir_path, exist_ok=True)

        try:
            # 1. Génération du texte en anglais
            print("\n📝 Génération du script en anglais...")
            script = self.generate_script("science")
            
            # Sauvegarde du texte anglais
            with open('test/textes/science_en.txt', 'w', encoding='utf-8') as f:
                f.write(script)
            print("✅ Texte anglais sauvegardé")

            # 2. Traduction en français
            print("\n🌍 Traduction en français...")
            translator = deepl.Translator(DEEPL_API_KEY)
            translated = translator.translate_text(script, target_lang="FR")
            
            with open('test/traductions/science_fr.txt', 'w', encoding='utf-8') as f:
                f.write(translated.text)
            print("✅ Traduction sauvegardée")

            # 3. Génération de l'audio
            print("\n🎤 Génération de l'audio...")
            audio_path = 'test/audio/test_josh.mp3'
            self.text_to_speech(script, audio_path)
            
            # Calcul du nombre d'images nécessaires basé sur la durée de l'audio
            audio = AudioFileClip(audio_path)
            images_needed = math.ceil(audio.duration / 4)  # Une image toutes les 4 secondes
            
            # 4. Récupération des images
            print(f"\n📸 Téléchargement de {images_needed} images...")
            search_terms = ["exoplanet", "space telescope", "habitable planet", "star system"]
            all_images = []
            images_per_term = math.ceil(images_needed / len(search_terms))
            
            for term in search_terms:
                images = self.get_multiple_images(term, images_per_term, 'test/images')
                if images:
                    all_images.extend(images)

            # 5. Génération des sous-titres avec timing adapté aux images
            print("\n🎬 Génération des sous-titres...")
            subtitles = self.split_into_subtitles(translated.text)
            
            # Calcul du nombre d'images nécessaires
            total_duration = len(subtitles) * 2.5  # 2.5 secondes par sous-titre
            images_needed = math.ceil(total_duration / 4)  # Une image toutes les 4 secondes
            
            # Sauvegarde des sous-titres au format SRT avec timing des images
            with open('test/sous-titres/science.srt', 'w', encoding='utf-8') as f:
                for idx, subtitle in enumerate(subtitles, 1):
                    start_time = self.format_timecode(idx-1, 2.5)
                    end_time = self.format_timecode(idx, 2.5)
                    
                    # Ajout d'un marqueur pour le changement d'image
                    image_change = (idx-1) * 2.5 % 4 == 0
                    if image_change:
                        f.write(f"# IMAGE_CHANGE: {idx//2}\n")
                    
                    f.write(f"{idx}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle}\n\n")
            
            print(f"✅ Sous-titres sauvegardés (nécessite {images_needed} images)")
            print(f"✅ {len(all_images)} images téléchargées")

            return True

        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            return False

    def format_timecode(self, index, duration_per_subtitle):
        """Convertit un index en timecode SRT"""
        total_seconds = index * duration_per_subtitle
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def test_voice_generation(self):
        """Teste la génération de voix avec Google TTS"""
        print("\n🎤 Test de génération de voix...")
        
        try:
            # Création du dossier de test pour l'audio
            os.makedirs('test/audio', exist_ok=True)
            
            # Utiliser le texte anglais existant s'il existe
            if os.path.exists('test/textes/science_en.txt'):
                with open('test/textes/science_en.txt', 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = "Hey there! Today we're exploring the fascinating world of exoplanets. Scientists have made incredible discoveries in 2024!"
            
            print("\n📝 Texte à convertir:")
            print(text[:100] + "..." if len(text) > 100 else text)
            
            output_path = 'test/audio/test_josh.mp3'
            return self.text_to_speech(text, output_path)
                
        except Exception as e:
            print(f"❌ Erreur lors du test de voix: {str(e)}")
            return False

    def get_trending_topics(self):
        """Récupère les sujets tendances"""
        try:
            logging.info("Tentative de récupération des tendances...")
            # Configuration de Google Trends
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Dictionnaire pour stocker les résultats
            trending_topics = {
                "science": [],
                "crypto": [],
                "ai": []
            }
            
            # Mots-clés de recherche par catégorie
            search_queries = {
                "science": ["space discovery", "scientific breakthrough", "new planet", "NASA"],
                "crypto": ["bitcoin", "ethereum", "cryptocurrency", "blockchain"],
                "ai": ["artificial intelligence", "machine learning", "ChatGPT", "AI"]
            }
            
            for category, queries in search_queries.items():
                print(f"\n🔍 Recherche des tendances pour {category}...")
                
                # Utilisation de interest_over_time au lieu de trending_searches
                pytrends.build_payload(queries, timeframe='now 7-d')
                trends_data = pytrends.interest_over_time()
                
                if not trends_data.empty:
                    # Calcul des moyennes pour chaque requête
                    avg_trends = trends_data.mean().sort_values(ascending=False)
                    
                    # Sélection des 3 termes les plus populaires
                    top_trends = avg_trends.head(3)
                    trending_topics[category] = [
                        f"{term} ({int(score)})" 
                        for term, score in top_trends.items()
                    ]
                    
                    print(f"✅ Tendances trouvées pour {category}:")
                    for idx, trend in enumerate(trending_topics[category], 1):
                        print(f"  {idx}. {trend}")
                else:
                    print(f"❌ Aucune tendance trouvée pour {category}")
            
            # Mise à jour des topics de la classe avec les tendances les plus populaires
            for category, trends in trending_topics.items():
                if trends:
                    top_trend = trends[0].split(' (')[0]  # Retire le score entre parenthèses
                    self.topics[category] = f"Les dernières découvertes sur {top_trend}"
            
            logging.info(f"Tendances récupérées avec succès : {self.topics}")
            return trending_topics
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des tendances : {str(e)}")
            return None 