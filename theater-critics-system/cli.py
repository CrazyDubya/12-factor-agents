#!/usr/bin/env python3
"""
CLI interface for Theater Critics Multi-Agent System
Allows interactive scene analysis with rotating critic ensemble
"""

import asyncio
import argparse
import json
from main import SceneData, CriticEnsemble, ConsensusAnalyzer, print_review_summary

class TheaterCriticsInterface:
    """Interactive CLI for theater critics system"""
    
    def __init__(self):
        self.ensemble = CriticEnsemble()
    
    def create_scene_interactive(self) -> SceneData:
        """Interactive scene creation"""
        print("\n🎭 CREATE NEW SCENE FOR ANALYSIS")
        print("="*50)
        
        title = input("Scene Title: ").strip()
        musical = input("Musical Name: ").strip()
        description = input("Scene Description: ").strip()
        
        print("\nOptional Details (press Enter to skip):")
        lyrics = input("Lyrics: ").strip() or None
        stage_directions = input("Stage Directions: ").strip() or None
        character_notes = input("Character Notes: ").strip() or None
        
        return SceneData(
            title=title,
            musical=musical,
            description=description,
            lyrics=lyrics,
            stage_directions=stage_directions,
            character_notes=character_notes
        )
    
    def load_scene_from_file(self, filepath: str) -> SceneData:
        """Load scene from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return SceneData(**data)
    
    def save_scene_to_file(self, scene: SceneData, filepath: str):
        """Save scene to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(scene.__dict__, f, indent=2)
        print(f"💾 Scene saved to {filepath}")
    
    async def analyze_scene(self, scene: SceneData, num_critics: int = 3) -> tuple:
        """Analyze scene with critic ensemble"""
        reviews = await self.ensemble.review_scene(scene, num_critics)
        consensus = ConsensusAnalyzer.calculate_consensus(reviews)
        return reviews, consensus
    
    def list_available_critics(self):
        """List all available critics and their specialties"""
        print("\n🎬 AVAILABLE CRITICS")
        print("="*50)
        for critic_type, critic in self.ensemble.critics.items():
            specialty_icon = {
                "primary": "🎭", "academic": "📚", "popular": "⭐",
                "experimental": "🎨", "commercial": "💰", "emotion": "❤️"
            }.get(critic_type.value, "🎪")
            
            print(f"{specialty_icon} {critic.name}")
            print(f"   Type: {critic_type.value.title()}")
            print(f"   Model: {critic.model}")
            print(f"   Specialty: {critic.specialty}")
            print()

def create_sample_scenes():
    """Create sample scenes for testing"""
    scenes = {
        "defying_gravity": SceneData(
            title="Defying Gravity",
            musical="Wicked",
            description="Elphaba's climactic moment of self-realization and defiance at the end of Act I",
            lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game""",
            stage_directions="Elphaba rises above the stage on a mechanical lift, cape billowing",
            character_notes="Elphaba transforms from outcast to empowered individual"
        ),
        
        "memory": SceneData(
            title="Memory",
            musical="Cats",
            description="Grizabella's haunting ballad about lost youth and longing for acceptance",
            lyrics="""Memory, all alone in the moonlight
I can smile at the old days
I was beautiful then""",
            stage_directions="Lone spotlight on Grizabella center stage, other cats watch from shadows",
            character_notes="Grizabella's desperate plea for understanding and redemption"
        ),
        
        "one_day_more": SceneData(
            title="One Day More",
            musical="Les Misérables",
            description="Act I finale bringing together all storylines before the revolution",
            lyrics="""One day more!
Another day, another destiny
This never-ending road to Calvary""",
            stage_directions="Full company on stage in tableaux, building to revolutionary fervor",
            character_notes="Each character expresses their personal stakes in the coming conflict"
        )
    }
    
    # Save sample scenes
    for name, scene in scenes.items():
        with open(f"sample_{name}.json", 'w') as f:
            json.dump(scene.__dict__, f, indent=2)
    
    print(f"📁 Created {len(scenes)} sample scenes:")
    for name in scenes.keys():
        print(f"   - sample_{name}.json")

async def main():
    parser = argparse.ArgumentParser(description="Theater Critics Multi-Agent System")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Interactive mode for creating scenes")
    parser.add_argument("--file", "-f", type=str, 
                       help="Load scene from JSON file")
    parser.add_argument("--critics", "-c", type=int, default=3,
                       help="Number of rotating critics (1-5)")
    parser.add_argument("--list-critics", action="store_true",
                       help="List available critics and their specialties")
    parser.add_argument("--create-samples", action="store_true",
                       help="Create sample scene files")
    parser.add_argument("--save", "-s", type=str,
                       help="Save scene to JSON file")
    
    args = parser.parse_args()
    
    interface = TheaterCriticsInterface()
    
    if args.list_critics:
        interface.list_available_critics()
        return
    
    if args.create_samples:
        create_sample_scenes()
        return
    
    # Get scene data
    scene = None
    if args.file:
        try:
            scene = interface.load_scene_from_file(args.file)
            print(f"📂 Loaded scene from {args.file}")
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            return
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON file: {args.file}")
            return
    
    elif args.interactive:
        scene = interface.create_scene_interactive()
        
        if args.save:
            interface.save_scene_to_file(scene, args.save)
    
    else:
        # Default to Defying Gravity example
        scene = SceneData(
            title="Defying Gravity",
            musical="Wicked", 
            description="Elphaba's climactic moment of self-realization and defiance at the end of Act I",
            lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game""",
            stage_directions="Elphaba rises above the stage on a mechanical lift, cape billowing",
            character_notes="Elphaba transforms from outcast to empowered individual"
        )
    
    if scene:
        # Validate number of critics
        num_critics = max(1, min(5, args.critics))
        
        # Analyze scene
        reviews, consensus = await interface.analyze_scene(scene, num_critics)
        
        # Print results
        print_review_summary(reviews, consensus)
        
        # Save results if requested
        if args.save and not args.interactive:
            results = {
                "scene": scene.__dict__,
                "reviews": [review.__dict__ for review in reviews],
                "consensus": consensus
            }
            result_file = args.save.replace('.json', '_results.json')
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {result_file}")

if __name__ == "__main__":
    asyncio.run(main())