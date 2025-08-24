#!/usr/bin/env python3
"""
Game Asset Generator
Generate all assets for the 5 unicorn/princess games using Stable Diffusion
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

class GameAssetGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sd_generator = self.base_dir / "working_sd_generator.py"
        self.assets_dir = self.base_dir / "unicorn-games" / "assets"
        self.generated_count = 0
        self.failed_count = 0
        self.total_start_time = time.time()
        
        # Game asset definitions
        self.game_assets = {
            "crystal-crown": {
                "name": "Crystal Crown Quest",
                "theme": "magical crystals and crowns",
                "assets": {
                    "characters": [
                        ("princess_crystal", "cute cartoon crystal princess with sparkling crown, long purple hair, crystal dress, magical glow, side view, transparent background", (96, 96)),
                        ("crystal_fairy", "tiny crystal fairy helper with crystal wings, sparkles, magical dust, flying pose, transparent background", (64, 64)),
                        ("crystal_guardian", "friendly crystal guardian creature, made of rainbow crystals, protective pose, magical aura, transparent background", (96, 96))
                    ],
                    "cards": [
                        ("red_crystal", "magical red crystal gem card, ruby red crystal in center, sparkle effects, decorative golden border, card format", (80, 120)),
                        ("blue_crystal", "magical blue crystal gem card, sapphire blue crystal in center, ice sparkles, silver border, card format", (80, 120)),
                        ("green_crystal", "magical green crystal gem card, emerald green crystal in center, nature sparkles, wooden border, card format", (80, 120)),
                        ("purple_crystal", "magical purple crystal gem card, amethyst crystal in center, mystical sparkles, purple border, card format", (80, 120))
                    ],
                    "tiles": [
                        ("crystal_path", "sparkling crystal pathway tile, rainbow crystals embedded in path, magical glow, seamless edges", (128, 128)),
                        ("crystal_cave", "crystal cave entrance tile, glowing crystals around opening, mysterious glow, game tile format", (128, 128)),
                        ("crystal_garden", "magical crystal garden tile, crystal flowers growing, sparkly ground, enchanted atmosphere", (128, 128))
                    ],
                    "ui": [
                        ("start_button", "START GAME button with crystal theme, rounded rectangle, crystal texture background, sparkles, large friendly font", (200, 60)),
                        ("score_panel", "crystal score display panel, transparent crystal with gold numbers area, decorative crystal borders", (150, 80)),
                        ("crown_icon", "golden crystal crown icon, simple but elegant, sparkles, perfect for UI elements", (48, 48))
                    ]
                }
            },
            
            "memory-palace": {
                "name": "Memory Palace Matching Game", 
                "theme": "royal palace and matching pairs",
                "assets": {
                    "characters": [
                        ("palace_princess", "elegant palace princess character, royal blue dress, golden crown, kind expression, standing pose", (96, 96)),
                        ("royal_cat", "cute royal palace cat with jeweled collar, fluffy white fur, regal pose, friendly expression", (64, 64)),
                        ("palace_guard", "friendly palace guard character, colorful uniform, ceremonial hat, welcoming pose, cartoon style", (96, 96))
                    ],
                    "cards": [
                        ("rose_card", "memory card with beautiful pink rose, detailed rose illustration, elegant card border, matching game format", (100, 100)),
                        ("crown_card", "memory card with golden crown, detailed crown with jewels, royal blue border, matching game format", (100, 100)),
                        ("castle_card", "memory card with cute castle illustration, fairy tale castle, pink and purple colors, card border", (100, 100)),
                        ("star_card", "memory card with golden star, sparkles around star, purple background, decorative border", (100, 100))
                    ],
                    "tiles": [
                        ("marble_floor", "royal palace marble floor tile, elegant patterns, soft colors, seamless tile design", (128, 128)),
                        ("carpet_tile", "royal palace carpet tile, ornate patterns, deep red with gold details, luxury feel", (128, 128)),
                        ("garden_tile", "palace garden tile, beautiful flowers, stone paths, royal garden atmosphere", (128, 128))
                    ],
                    "ui": [
                        ("match_button", "FIND MATCH button, royal theme, elegant font, gold and blue colors, rounded rectangle", (180, 50)),
                        ("pairs_counter", "pairs found counter display, elegant palace design, numbers area, decorative frame", (120, 60)),
                        ("palace_icon", "cute palace building icon, simple but recognizable, royal colors, UI friendly", (48, 48))
                    ]
                }
            },
            
            "princess-academy": {
                "name": "Princess Academy Learning Game",
                "theme": "princess school and lessons", 
                "assets": {
                    "characters": [
                        ("student_princess", "young princess student character, school uniform with princess touches, books in hand, eager expression", (96, 96)),
                        ("teacher_princess", "wise teacher princess, elegant dress, kind expression, holding a wand or book, teaching pose", (96, 96)),
                        ("academy_pet", "cute academy pet companion, small dragon or unicorn, friendly, wearing a school bow", (64, 64))
                    ],
                    "cards": [
                        ("lesson_card", "princess lesson card, open book with sparkles, education theme, soft pastel border", (80, 120)),
                        ("skill_card", "princess skill card, magical star with achievement symbol, encouraging colors, card format", (80, 120)),
                        ("diploma_card", "princess diploma card, scroll with ribbon, congratulations theme, gold and white", (80, 120)),
                        ("homework_card", "princess homework card, quill and parchment, cute academic theme, soft colors", (80, 120))
                    ],
                    "tiles": [
                        ("classroom_tile", "princess academy classroom tile, desks and blackboard, educational and magical atmosphere", (128, 128)),
                        ("library_tile", "academy library tile, books and reading area, cozy learning environment", (128, 128)),
                        ("courtyard_tile", "academy courtyard tile, outdoor study area, trees and benches, peaceful setting", (128, 128))
                    ],
                    "ui": [
                        ("learn_button", "LEARN button, academy theme, book icon, encouraging colors, educational feel", (160, 50)),
                        ("progress_bar", "learning progress bar, magical filling effect, stars for milestones, academy colors", (200, 30)),
                        ("academy_crest", "princess academy crest icon, school shield with crown, official but friendly", (48, 48))
                    ]
                }
            },
            
            "rainbow-bridge": {
                "name": "Rainbow Bridge Adventure",
                "theme": "rainbow bridges and cloud hopping",
                "assets": {
                    "characters": [
                        ("rainbow_princess", "rainbow princess character, dress with rainbow colors, cheerful expression, adventuring pose", (96, 96)),
                        ("cloud_sprite", "cute cloud sprite companion, fluffy white with rainbow details, floating pose, magical sparkles", (64, 64)),
                        ("rainbow_unicorn", "beautiful rainbow unicorn, colorful mane and tail, kind expression, side view pose", (96, 96))
                    ],
                    "cards": [
                        ("rainbow_card", "rainbow power card, beautiful rainbow arc, sparkles, bright cheerful colors, card format", (80, 120)),
                        ("cloud_card", "fluffy cloud card, white cloud with rainbow edges, soft and dreamy, card border", (80, 120)),
                        ("bridge_card", "rainbow bridge piece card, bridge segment with rainbow colors, connecting piece design", (80, 120)),
                        ("star_power", "rainbow star power card, star with rainbow trails, magical energy, dynamic design", (80, 120))
                    ],
                    "tiles": [
                        ("cloud_platform", "fluffy cloud platform tile, white cloud with soft shadows, safe landing spot", (128, 128)),
                        ("rainbow_segment", "rainbow bridge segment tile, colorful bridge piece, connects to other segments", (128, 128)),
                        ("sky_background", "sky background tile, blue sky with white clouds, peaceful heavenly atmosphere", (128, 128))
                    ],
                    "ui": [
                        ("jump_button", "JUMP button, cloud and rainbow theme, dynamic design, encouraging colors", (150, 50)),
                        ("bridge_meter", "rainbow bridge progress meter, colorful filling bar, rainbow gradient", (180, 25)),
                        ("rainbow_icon", "simple rainbow arc icon, bright colors, perfect for UI elements and menus", (48, 48))
                    ]
                }
            },
            
            "starlight-stable": {
                "name": "Starlight Stable Unicorn Care",
                "theme": "unicorn care and starlight magic",
                "assets": {
                    "characters": [
                        ("caretaker_girl", "young unicorn caretaker girl, overalls and boots, kind expression, caring pose, magical sparkles", (96, 96)),
                        ("baby_unicorn", "adorable baby unicorn, small size, innocent expression, playful pose, rainbow mane", (64, 64)),
                        ("adult_unicorn", "majestic adult unicorn, beautiful and wise, starlight in mane, noble standing pose", (96, 96))
                    ],
                    "cards": [
                        ("food_card", "unicorn food card, magical hay or rainbow apples, nourishing theme, warm colors", (80, 120)),
                        ("grooming_card", "unicorn grooming card, brush and sparkles, care theme, gentle colors", (80, 120)),
                        ("healing_card", "unicorn healing card, magical herbs or starlight, wellness theme, soothing colors", (80, 120)),
                        ("play_card", "unicorn play card, toys or games, happiness theme, bright cheerful colors", (80, 120))
                    ],
                    "tiles": [
                        ("stable_floor", "magical stable floor tile, hay and starlight patterns, cozy and clean", (128, 128)),
                        ("pasture_tile", "unicorn pasture tile, green grass with flowers, peaceful grazing area", (128, 128)),
                        ("stable_stall", "unicorn stable stall tile, wooden stall with magical touches, safe and comfortable", (128, 128))
                    ],
                    "ui": [
                        ("care_button", "CARE button, heart and star theme, nurturing colors, love and kindness", (150, 50)),
                        ("happiness_meter", "unicorn happiness meter, heart-shaped with starlight, magical filling", (160, 30)),
                        ("star_icon", "magical star icon, starlight stable theme, twinkling effect, UI perfect", (48, 48))
                    ]
                }
            }
        }
    
    def generate_asset(self, prompt, width, height, output_path, asset_name):
        """Generate a single asset using Stable Diffusion"""
        try:
            print(f"    🎨 Generating {asset_name}...")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Run SD generation
            start_time = time.time()
            cmd = [
                'python3', str(self.sd_generator),
                '--prompt', prompt,
                '--width', str(width),
                '--height', str(height),
                '--steps', '20',  # Good quality
                '--output', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            gen_time = time.time() - start_time
            
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                print(f"    ✅ {asset_name} ({gen_time:.1f}s) - {output_path.stat().st_size} bytes")
                self.generated_count += 1
                return True
            else:
                print(f"    ❌ {asset_name} failed: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                self.failed_count += 1
                return False
                
        except subprocess.TimeoutExpired:
            print(f"    ❌ {asset_name} timed out")
            self.failed_count += 1
            return False
        except Exception as e:
            print(f"    ❌ {asset_name} error: {str(e)[:100]}")
            self.failed_count += 1
            return False
    
    def generate_game_assets(self, game_key):
        """Generate all assets for a specific game"""
        game_data = self.game_assets[game_key]
        print(f"\n🎮 Generating assets for {game_data['name']}")
        print(f"Theme: {game_data['theme']}")
        print("=" * 60)
        
        game_start_time = time.time()
        game_generated = 0
        game_failed = 0
        
        for asset_type, assets in game_data["assets"].items():
            print(f"\n📁 {asset_type.title()} Assets:")
            
            for asset_name, prompt, (width, height) in assets:
                output_path = self.assets_dir / game_key / asset_type / f"{asset_name}.png"
                
                # Add game theme to prompt for consistency
                themed_prompt = f"{prompt}, {game_data['theme']} style, children's board game art, cute cartoon style, bright colors, transparent background"
                
                if self.generate_asset(themed_prompt, width, height, output_path, asset_name):
                    game_generated += 1
                else:
                    game_failed += 1
        
        game_time = time.time() - game_start_time
        print(f"\n📊 {game_data['name']} Complete:")
        print(f"   Generated: {game_generated}")
        print(f"   Failed: {game_failed}")
        print(f"   Success Rate: {game_generated/(game_generated+game_failed)*100:.1f}%")
        print(f"   Time: {game_time:.1f}s")
        
        return game_generated, game_failed
    
    def generate_all_games(self):
        """Generate assets for all games"""
        print("🚀 Starting Game Asset Generation")
        print("Using Stable Diffusion for high-quality assets")
        print("=" * 70)
        
        total_generated = 0
        total_failed = 0
        
        for game_key in self.game_assets.keys():
            generated, failed = self.generate_game_assets(game_key)
            total_generated += generated
            total_failed += failed
        
        total_time = time.time() - self.total_start_time
        
        print(f"\n🎉 FINAL SUMMARY")
        print("=" * 50)
        print(f"Total Assets Generated: {total_generated}")
        print(f"Total Failed: {total_failed}")
        print(f"Overall Success Rate: {total_generated/(total_generated+total_failed)*100:.1f}%")
        print(f"Total Time: {total_time:.1f}s")
        print(f"Average per Asset: {total_time/(total_generated+total_failed):.1f}s")
        
        # Create asset manifest
        manifest_path = self.assets_dir / "generation_manifest.json"
        manifest = {
            "generation_date": datetime.now().isoformat(),
            "generator": "Stable Diffusion v1.5",
            "total_assets": total_generated,
            "failed_assets": total_failed,
            "success_rate": total_generated/(total_generated+total_failed)*100,
            "total_time": total_time,
            "games": list(self.game_assets.keys()),
            "asset_types": ["characters", "cards", "tiles", "ui"]
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n📄 Generation manifest: {manifest_path}")
        
        if total_generated > total_failed:
            print("\n✅ Asset generation successful! Games ready to play.")
            return True
        else:
            print("\n⚠️  Asset generation had issues. Check failed assets.")
            return False

def main():
    if len(sys.argv) > 1:
        # Generate specific game
        game_key = sys.argv[1]
        generator = GameAssetGenerator()
        if game_key in generator.game_assets:
            generator.generate_game_assets(game_key)
        else:
            print(f"Unknown game: {game_key}")
            print(f"Available games: {list(generator.game_assets.keys())}")
    else:
        # Generate all games
        generator = GameAssetGenerator()
        success = generator.generate_all_games()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()