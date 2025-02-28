from video_generator import VideoGenerator
import traceback

if __name__ == "__main__":
    try:
        generator = VideoGenerator()
        
        print("🎬 Test complet pour le topic Science...")
        generator.test_science_content()
        
        print("\n🎬 Test de génération de voix...")
        generator.test_voice_generation()
        
        print("🎬 Génération de la vidéo finale...")
        generator.create_video(
            images_dir='test/images',
            audio_path='test/audio/test_josh.mp3',
            output_path='test/video_finale.mp4'
        )

        print("📈 Analyse des tendances...")
        trending_topics = generator.get_trending_topics()
        if trending_topics:
            print("\n✨ Nouveaux sujets de vidéos:")
            for category, topics in trending_topics.items():
                print(f"\n{category.upper()}:")
                for idx, topic in enumerate(topics, 1):
                    print(f"{idx}. {topic}")
    except Exception as e:
        print(f"❌ Erreur détaillée:")
        print(traceback.format_exc()) 