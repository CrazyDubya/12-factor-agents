#!/usr/bin/env python3
"""
Massive Asset Generator - Phase 2
Scale up from 65 assets to 300+ assets across all games
Add missing categories and expand variety in existing ones
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import json

class MassiveAssetGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sd_generator = self.base_dir / "working_sd_generator.py"
        self.assets_dir = self.base_dir / "unicorn-games" / "assets"
        self.generated_count = 0
        self.failed_count = 0
        self.start_time = time.time()
        
        # Massive asset expansion plan
        self.massive_assets = {
            "crystal-crown": {
                "name": "Crystal Crown Quest",
                "theme": "magical crystals and crowns",
                "expansion": {
                    # More characters (3 -> 8)
                    "characters": [
                        ("crystal_wizard", "wise crystal wizard with crystal staff, long beard with crystal sparkles, magical robes, mentor character", (96, 96)),
                        ("crystal_knight", "brave crystal knight in crystal armor, crystal sword, protective pose, heroic character", (96, 96)),
                        ("crystal_dragon", "friendly baby crystal dragon, crystal scales, cute expression, magical companion", (80, 80)),
                        ("evil_shadow", "dark shadow villain, purple and black colors, mysterious enemy, boss character", (96, 96)),
                        ("crystal_merchant", "cheerful crystal merchant character, bag of crystals, trading pose, helpful NPC", (96, 96)),
                    ],
                    
                    # More cards (4 -> 12) 
                    "cards": [
                        ("yellow_crystal", "magical yellow crystal gem card, citrine crystal, lightning sparkles, bright border", (80, 120)),
                        ("orange_crystal", "magical orange crystal gem card, amber crystal, fire sparkles, warm border", (80, 120)),
                        ("rainbow_crystal", "magical rainbow crystal gem card, prismatic crystal, rainbow sparkles, colorful border", (80, 120)),
                        ("power_crystal", "ultimate power crystal card, glowing white crystal, intense energy, golden border", (80, 120)),
                        ("shield_spell", "crystal shield protection spell card, defensive magic, blue glow", (80, 120)),
                        ("heal_spell", "crystal healing spell card, restoration magic, green sparkles", (80, 120)),
                        ("attack_spell", "crystal attack spell card, offensive magic, red energy", (80, 120)),
                        ("teleport_spell", "crystal teleport spell card, movement magic, purple swirls", (80, 120)),
                    ],
                    
                    # More tiles (3 -> 10)
                    "tiles": [
                        ("crystal_bridge", "crystal bridge tile, transparent crystal bridge, magical crossing", (128, 128)),
                        ("crystal_fountain", "crystal fountain tile, magical water with crystals, healing spot", (128, 128)),
                        ("crystal_maze", "crystal maze wall tile, crystal barriers, puzzle element", (128, 128)),
                        ("crystal_portal", "crystal portal tile, magical gateway, teleportation point", (128, 128)),
                        ("crystal_treasure", "crystal treasure chest tile, locked chest with crystals, goal tile", (128, 128)),
                        ("crystal_trap", "crystal trap tile, dangerous crystal spikes, hazard tile", (128, 128)),
                        ("crystal_stairs", "crystal staircase tile, ascending crystal steps, vertical movement", (128, 128)),
                    ],
                    
                    # New: Obstacles (0 -> 8)
                    "obstacles": [
                        ("crystal_wall", "solid crystal wall obstacle, blocks movement, crystal barrier", (96, 96)),
                        ("crystal_spikes", "dangerous crystal spike obstacle, damage hazard, sharp crystals", (96, 96)),
                        ("shadow_blob", "dark shadow obstacle, moving enemy, avoid or fight", (96, 96)),
                        ("crystal_lock", "crystal lock obstacle, needs key to pass, puzzle element", (96, 96)),
                        ("broken_bridge", "broken crystal bridge, gap obstacle, needs repair", (128, 96)),
                        ("crystal_boulder", "large crystal boulder, heavy obstacle, blocks path", (96, 96)),
                        ("magic_barrier", "magical force field, energy barrier, temporary obstacle", (96, 96)),
                        ("crystal_thornvines", "thorny crystal vines, nature obstacle, sharp barrier", (96, 96)),
                    ],
                    
                    # New: Resources (0 -> 10)
                    "resources": [
                        ("crystal_shard", "small crystal shard, collectible resource, crafting material", (48, 48)),
                        ("crystal_key", "crystal key item, unlocks doors, special resource", (48, 48)),
                        ("health_potion", "crystal health potion, red liquid, healing item", (48, 64)),
                        ("magic_potion", "crystal magic potion, blue liquid, mana restoration", (48, 64)),
                        ("crystal_coin", "crystal currency coin, valuable resource, trading item", (48, 48)),
                        ("crystal_gem", "perfect crystal gem, rare resource, valuable treasure", (48, 48)),
                        ("crystal_scroll", "magic scroll item, spell knowledge, learning resource", (64, 48)),
                        ("crystal_wand", "magic crystal wand, tool item, spellcasting aid", (64, 32)),
                        ("crystal_armor", "crystal armor piece, protection item, equipment", (64, 64)),
                        ("crystal_food", "magical crystal fruit, sustenance item, energy restore", (48, 48)),
                    ],
                    
                    # New: Board pieces (0 -> 6)
                    "boards": [
                        ("game_board_center", "crystal quest game board center piece, main play area", (512, 512)),
                        ("game_board_corner", "crystal quest corner board piece, decorative border", (256, 256)),
                        ("game_board_edge", "crystal quest edge board piece, connecting border", (512, 128)),
                        ("start_area", "crystal quest starting area, player beginning zone", (256, 256)),
                        ("goal_area", "crystal quest goal area, victory destination zone", (256, 256)),
                        ("crystal_castle_board", "crystal castle board piece, main location", (400, 400)),
                    ]
                }
            },
            
            "memory-palace": {
                "name": "Memory Palace Matching Game",
                "theme": "royal palace and matching pairs", 
                "expansion": {
                    "characters": [
                        ("queen_character", "elegant queen character, royal crown, regal dress, authority pose", (96, 96)),
                        ("king_character", "wise king character, golden crown, royal robes, leadership pose", (96, 96)),
                        ("court_jester", "cheerful court jester, colorful outfit, entertaining pose", (96, 96)),
                        ("royal_horse", "majestic royal horse, decorated saddle, noble stance", (96, 96)),
                        ("palace_chef", "friendly palace chef, chef hat, cooking pose, kitchen character", (96, 96)),
                    ],
                    
                    "cards": [
                        ("diamond_card", "memory card with sparkling diamond, jewel illustration, luxury theme", (100, 100)),
                        ("scepter_card", "memory card with royal scepter, golden staff with jewels", (100, 100)),
                        ("throne_card", "memory card with royal throne, ornate chair illustration", (100, 100)),
                        ("shield_card", "memory card with royal shield, heraldic design, coat of arms", (100, 100)),
                        ("horse_card", "memory card with royal horse, majestic steed illustration", (100, 100)),
                        ("flower_card", "memory card with royal garden flower, elegant bloom", (100, 100)),
                        ("book_card", "memory card with royal library book, knowledge symbol", (100, 100)),
                        ("music_card", "memory card with royal harp, musical instrument", (100, 100)),
                    ],
                    
                    "tiles": [
                        ("throne_room", "royal throne room tile, grand hall with throne", (128, 128)),
                        ("royal_kitchen", "palace kitchen tile, cooking area, food preparation", (128, 128)),
                        ("treasure_room", "royal treasure room tile, gold and jewels storage", (128, 128)),
                        ("armory_tile", "palace armory tile, weapons and armor storage", (128, 128)),
                        ("royal_bedroom", "luxurious royal bedroom tile, ornate sleeping quarters", (128, 128)),
                        ("balcony_tile", "palace balcony tile, outdoor viewing area", (128, 128)),
                        ("dungeon_tile", "palace dungeon tile, lower level prison area", (128, 128)),
                    ],
                    
                    "obstacles": [
                        ("locked_door", "heavy palace door obstacle, ornate lock, needs key", (96, 128)),
                        ("royal_guard", "palace guard obstacle, must solve puzzle to pass", (96, 96)),
                        ("heavy_curtain", "thick palace curtain, blocks view, hidden passage", (96, 128)),
                        ("broken_stairs", "damaged palace stairs, gap obstacle", (128, 96)),
                        ("flooded_hall", "flooded palace hallway, water obstacle", (128, 96)),
                        ("sleeping_dragon", "palace dragon guardian, sleeping obstacle", (128, 96)),
                    ],
                    
                    "resources": [
                        ("palace_key", "ornate palace key, unlocks royal doors", (48, 48)),
                        ("royal_seal", "official royal seal, authority item", (48, 48)),
                        ("gold_coin", "royal gold coin, palace currency", (48, 48)),
                        ("royal_letter", "sealed royal letter, message item", (64, 48)),
                        ("crown_jewel", "precious crown jewel, valuable treasure", (48, 48)),
                        ("royal_ring", "royal signet ring, status symbol", (48, 48)),
                    ],
                    
                    "boards": [
                        ("palace_courtyard", "royal palace courtyard board, main area", (512, 512)),
                        ("palace_entrance", "grand palace entrance, starting area", (256, 256)),
                        ("royal_gardens", "palace gardens board piece, outdoor area", (400, 400)),
                    ]
                }
            },
            
            "princess-academy": {
                "name": "Princess Academy Learning Game",
                "theme": "princess school and lessons",
                "expansion": {
                    "characters": [
                        ("headmistress", "wise academy headmistress, elegant dress, leadership pose", (96, 96)),
                        ("study_buddy", "helpful study buddy princess, books in hand, friendly", (96, 96)),
                        ("academy_owl", "wise academy owl, professor glasses, knowledge symbol", (64, 64)),
                        ("visiting_prince", "young prince visitor, formal outfit, guest character", (96, 96)),
                        ("librarian", "academy librarian princess, surrounded by books", (96, 96)),
                    ],
                    
                    "cards": [
                        ("math_card", "princess math lesson card, numbers and equations, learning theme", (80, 120)),
                        ("art_card", "princess art lesson card, paintbrush and palette, creative theme", (80, 120)),
                        ("music_card", "princess music lesson card, musical notes, performance theme", (80, 120)),
                        ("dance_card", "princess dance lesson card, ballet shoes, movement theme", (80, 120)),
                        ("etiquette_card", "princess etiquette lesson card, proper manners, social theme", (80, 120)),
                        ("languages_card", "princess language lesson card, foreign words, communication theme", (80, 120)),
                        ("history_card", "princess history lesson card, ancient scroll, knowledge theme", (80, 120)),
                        ("science_card", "princess science lesson card, beakers and experiments, discovery theme", (80, 120)),
                    ],
                    
                    "tiles": [
                        ("music_room", "academy music room tile, piano and instruments", (128, 128)),
                        ("art_studio", "academy art studio tile, easels and paint supplies", (128, 128)),
                        ("dance_hall", "academy dance hall tile, mirrors and ballet barres", (128, 128)),
                        ("laboratory", "academy science lab tile, experiments and equipment", (128, 128)),
                        ("dining_hall", "academy dining hall tile, tables and elegant meals", (128, 128)),
                        ("dormitory", "academy dormitory tile, sleeping quarters", (128, 128)),
                        ("exam_room", "academy exam room tile, testing area", (128, 128)),
                    ],
                    
                    "obstacles": [
                        ("difficult_test", "challenging exam obstacle, must study to pass", (96, 64)),
                        ("strict_teacher", "stern teacher obstacle, must behave properly", (96, 96)),
                        ("locked_library", "locked library obstacle, needs permission", (128, 96)),
                        ("broken_instrument", "damaged musical instrument, needs repair", (96, 64)),
                        ("messy_room", "untidy room obstacle, must clean to proceed", (128, 96)),
                    ],
                    
                    "resources": [
                        ("textbook", "academy textbook, learning resource", (48, 64)),
                        ("quill_pen", "writing quill, note-taking tool", (48, 32)),
                        ("ink_bottle", "ink bottle, writing supply", (32, 48)),
                        ("study_notes", "handwritten study notes, knowledge resource", (64, 48)),
                        ("academy_badge", "achievement badge, progress reward", (48, 48)),
                        ("report_card", "excellent report card, success item", (64, 48)),
                    ],
                    
                    "boards": [
                        ("academy_campus", "princess academy campus board, main area", (512, 512)),
                        ("graduation_stage", "academy graduation ceremony area", (400, 256)),
                    ]
                }
            },
            
            "rainbow-bridge": {
                "name": "Rainbow Bridge Adventure",
                "theme": "rainbow bridges and cloud hopping",
                "expansion": {
                    "characters": [
                        ("storm_cloud", "grumpy storm cloud character, rain and lightning, obstacle enemy", (80, 64)),
                        ("sun_spirit", "cheerful sun spirit, golden rays, helpful character", (80, 80)),
                        ("wind_fairy", "playful wind fairy, swirling air, movement helper", (64, 64)),
                        ("rainbow_bird", "colorful rainbow bird, flying companion, guide character", (64, 64)),
                        ("cloud_king", "majestic cloud king, crown of mist, sky ruler", (96, 96)),
                    ],
                    
                    "cards": [
                        ("wind_card", "wind power card, swirling air currents, movement boost", (80, 120)),
                        ("sun_card", "sunshine power card, golden rays, energy boost", (80, 120)),
                        ("rain_card", "gentle rain card, water droplets, growth power", (80, 120)),
                        ("lightning_card", "lightning power card, electric energy, speed boost", (80, 120)),
                        ("mist_card", "cloud mist card, fog effect, hiding power", (80, 120)),
                        ("breeze_card", "gentle breeze card, soft wind, calm effect", (80, 120)),
                        ("storm_card", "storm power card, weather control, powerful effect", (80, 120)),
                        ("clear_sky", "clear sky card, perfect weather, bonus effect", (80, 120)),
                    ],
                    
                    "tiles": [
                        ("storm_cloud_tile", "dark storm cloud tile, dangerous weather area", (128, 128)),
                        ("sun_tile", "bright sunshine tile, warm and safe area", (128, 128)),
                        ("wind_current", "wind current tile, movement boost area", (128, 128)),
                        ("rain_tile", "gentle rain tile, refreshing area", (128, 128)),
                        ("lightning_tile", "lightning strike tile, high energy area", (128, 128)),
                        ("mist_tile", "misty cloud tile, mysterious hidden area", (128, 128)),
                        ("tornado_tile", "tornado tile, spinning wind hazard", (128, 128)),
                    ],
                    
                    "obstacles": [
                        ("dark_cloud", "threatening dark cloud, storm obstacle", (96, 64)),
                        ("wind_barrier", "strong wind wall, air current obstacle", (96, 96)),
                        ("lightning_storm", "dangerous lightning, electrical hazard", (96, 96)),
                        ("thick_fog", "dense fog obstacle, visibility blocker", (128, 96)),
                        ("broken_rainbow", "damaged rainbow bridge, gap obstacle", (128, 64)),
                    ],
                    
                    "resources": [
                        ("rainbow_gem", "rainbow colored gem, bridge building material", (48, 48)),
                        ("cloud_essence", "bottled cloud essence, floating power", (48, 64)),
                        ("wind_bottled", "captured wind, movement resource", (48, 64)),
                        ("sunbeam_crystal", "crystallized sunbeam, light resource", (48, 48)),
                        ("rain_drop", "magical rain drop, growth resource", (32, 48)),
                        ("lightning_jar", "contained lightning, energy resource", (48, 64)),
                    ],
                    
                    "boards": [
                        ("sky_kingdom", "celestial sky kingdom board, main play area", (512, 512)),
                        ("rainbow_crossroads", "rainbow bridge intersection, path choice area", (400, 400)),
                    ]
                }
            },
            
            "starlight-stable": {
                "name": "Starlight Stable Unicorn Care",
                "theme": "unicorn care and starlight magic",
                "expansion": {
                    "characters": [
                        ("stable_master", "wise stable master, experienced caretaker, mentor figure", (96, 96)),
                        ("unicorn_family", "unicorn family group, parents and foals together", (128, 96)),
                        ("forest_spirit", "gentle forest spirit, nature guardian, helpful guide", (80, 96)),
                        ("star_fairy", "tiny star fairy, night magic helper, twinkling companion", (48, 64)),
                        ("moon_unicorn", "mystical moon unicorn, silver coat, night magic", (96, 96)),
                    ],
                    
                    "cards": [
                        ("grooming_brush", "magical grooming brush card, care tool, beauty item", (80, 120)),
                        ("unicorn_medicine", "healing medicine card, health restoration, care item", (80, 120)),
                        ("magic_feed", "enchanted unicorn feed card, nutrition, growth item", (80, 120)),
                        ("blanket_card", "warm stable blanket card, comfort, care item", (80, 120)),
                        ("saddle_card", "beautiful unicorn saddle card, riding equipment", (80, 120)),
                        ("bridle_card", "gentle unicorn bridle card, guidance equipment", (80, 120)),
                        ("toy_card", "unicorn toy card, entertainment, happiness item", (80, 120)),
                        ("treat_card", "special unicorn treat card, reward, bonding item", (80, 120)),
                    ],
                    
                    "tiles": [
                        ("feeding_area", "unicorn feeding area tile, food and water stations", (128, 128)),
                        ("grooming_station", "unicorn grooming station tile, care equipment area", (128, 128)),
                        ("exercise_field", "unicorn exercise field tile, running and playing area", (128, 128)),
                        ("medical_bay", "stable medical bay tile, healing and treatment area", (128, 128)),
                        ("star_pool", "magical star pool tile, bathing and cleansing area", (128, 128)),
                        ("hay_storage", "hay storage area tile, food supply storage", (128, 128)),
                        ("unicorn_nursery", "baby unicorn nursery tile, foal care area", (128, 128)),
                    ],
                    
                    "obstacles": [
                        ("sick_unicorn", "ill unicorn obstacle, needs medical care", (96, 96)),
                        ("broken_fence", "damaged stable fence, needs repair", (128, 64)),
                        ("empty_feed_bin", "empty food container, needs refilling", (64, 96)),
                        ("muddy_area", "muddy stable area, needs cleaning", (96, 96)),
                        ("escaped_unicorn", "runaway unicorn, needs gentle retrieval", (96, 96)),
                    ],
                    
                    "resources": [
                        ("unicorn_brush", "grooming brush tool, care equipment", (48, 32)),
                        ("star_apple", "magical star apple, unicorn treat", (48, 48)),
                        ("healing_herbs", "medicinal herbs, health resource", (48, 48)),
                        ("golden_hay", "premium golden hay, nutrition resource", (64, 48)),
                        ("star_water", "enchanted star water, magical drink", (48, 64)),
                        ("unicorn_toy", "colorful unicorn toy, entertainment item", (48, 48)),
                    ],
                    
                    "boards": [
                        ("stable_complex", "complete stable complex board, main facility", (512, 512)),
                        ("magical_pasture", "enchanted pasture board, outdoor area", (400, 400)),
                    ]
                }
            }
        }
    
    def generate_asset(self, prompt, width, height, output_path, asset_name, game_theme):
        """Generate a single asset using Stable Diffusion"""
        try:
            print(f"    🎨 {asset_name} ({width}x{height})...")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Enhanced prompt with game theme
            full_prompt = f"{prompt}, {game_theme}, children's board game art, cute cartoon style, bright colors, high quality, transparent background"
            
            start_time = time.time()
            cmd = [
                'python3', str(self.sd_generator),
                '--prompt', full_prompt,
                '--width', str(width),
                '--height', str(height),
                '--steps', '20',
                '--output', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            gen_time = time.time() - start_time
            
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                print(f"    ✅ {asset_name} ({gen_time:.1f}s) - {output_path.stat().st_size} bytes")
                self.generated_count += 1
                return True
            else:
                print(f"    ❌ {asset_name} failed")
                self.failed_count += 1
                return False
                
        except Exception as e:
            print(f"    ❌ {asset_name} error: {str(e)[:50]}")
            self.failed_count += 1
            return False
    
    def generate_massive_expansion(self, target_game=None):
        """Generate massive asset expansion"""
        print("🚀 MASSIVE ASSET GENERATION - PHASE 2")
        print("Scaling from 65 assets to 300+ assets")
        print("Adding 5 new asset categories + expanding existing ones")
        print("=" * 70)
        
        games_to_process = [target_game] if target_game else list(self.massive_assets.keys())
        
        for game_key in games_to_process:
            game_data = self.massive_assets[game_key]
            print(f"\n🎮 {game_data['name']} - MASSIVE EXPANSION")
            print(f"Theme: {game_data['theme']}")
            print("=" * 60)
            
            game_start_time = time.time()
            game_generated = 0
            game_failed = 0
            
            for asset_type, assets in game_data["expansion"].items():
                print(f"\n📁 {asset_type.title()} ({len(assets)} new assets):")
                
                for asset_name, prompt, (width, height) in assets:
                    output_path = self.assets_dir / game_key / asset_type / f"{asset_name}.png"
                    
                    if self.generate_asset(prompt, width, height, output_path, asset_name, game_data['theme']):
                        game_generated += 1
                    else:
                        game_failed += 1
            
            game_time = time.time() - game_start_time
            print(f"\n📊 {game_data['name']} Expansion Complete:")
            print(f"   New Assets: {game_generated}")
            print(f"   Failed: {game_failed}")
            print(f"   Success Rate: {game_generated/(game_generated+game_failed)*100:.1f}%")
            print(f"   Time: {game_time:.1f}s")
        
        total_time = time.time() - self.start_time
        
        print(f"\n🎉 MASSIVE EXPANSION COMPLETE")
        print("=" * 50)
        print(f"New Assets Generated: {self.generated_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Success Rate: {self.generated_count/(self.generated_count+self.failed_count)*100:.1f}%")
        print(f"Total Time: {total_time:.1f}s")
        print(f"Average per Asset: {total_time/(self.generated_count+self.failed_count):.1f}s")
        
        # Calculate totals
        original = 65
        new_total = original + self.generated_count
        print(f"\nAsset Scale Progress:")
        print(f"  Phase 1 (fixes): 65 assets")
        print(f"  Phase 2 (expansion): +{self.generated_count} = {new_total} assets")
        print(f"  Target achieved: {new_total >= 200}")
        
        return self.generated_count > self.failed_count

def main():
    if len(sys.argv) > 1:
        # Generate specific game expansion
        game_key = sys.argv[1]
        generator = MassiveAssetGenerator()
        if game_key in generator.massive_assets:
            generator.generate_massive_expansion(game_key)
        else:
            print(f"Unknown game: {game_key}")
            print(f"Available games: {list(generator.massive_assets.keys())}")
    else:
        # Generate all massive expansions
        generator = MassiveAssetGenerator()
        success = generator.generate_massive_expansion()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()