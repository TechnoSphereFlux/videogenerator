from video_generator import VideoGenerator

if __name__ == "__main__":
    try:
        print("🔍 Test de l'analyse des tendances...")
        generator = VideoGenerator()
        
        trending_topics = generator.get_trending_topics()
        
        if trending_topics:
            print("\n✨ Sujets tendances trouvés :")
            for category, topics in trending_topics.items():
                print(f"\n📊 {category.upper()} :")
                if topics:
                    for idx, topic in enumerate(topics, 1):
                        print(f"  {idx}. {topic}")
                else:
                    print("  Aucune tendance trouvée")
                    
            print("\n📝 Nouveaux sujets de vidéos mis à jour :")
            for category, topic in generator.topics.items():
                print(f"\n{category.upper()} :")
                print(f"  {topic}")
    
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}") 