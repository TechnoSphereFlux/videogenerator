import schedule
import time
from auto_generator import generate_videos

def main():
    # Planification des générations (3 fois par jour)
    schedule.every().day.at("06:00").do(generate_videos)  # Matin
    schedule.every().day.at("14:00").do(generate_videos)  # Après-midi
    schedule.every().day.at("22:00").do(generate_videos)  # Soir
    
    print("🤖 Planificateur démarré...")
    print("📅 Horaires de génération : 06:00, 14:00, 22:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérification toutes les minutes

if __name__ == "__main__":
    # Première génération au démarrage
    generate_videos()
    # Démarrage du planificateur
    main() 