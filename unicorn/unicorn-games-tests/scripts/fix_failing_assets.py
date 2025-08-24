#!/usr/bin/env python3
"""
Fix Failing Assets
Regenerate the 14 failed assets with SD-friendly dimensions and improved prompts
"""

import os
import sys
import time
import subprocess
from pathlib import Path

class FailingAssetsFixer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sd_generator = self.base_dir / "working_sd_generator.py"
        self.assets_dir = self.base_dir / "unicorn-games" / "assets"
        self.fixed_count = 0
        self.still_failed_count = 0
        
        # Failed assets with SD-friendly fixes
        self.failing_assets = {
            # Crystal Crown UI fixes
            "crystal-crown": {
                "ui": [
                    ("start_button", "START GAME crystal button, rounded rectangle button, crystal texture background, golden sparkles, large readable font, game UI element, transparent background", (120, 60)),  # was 200x60
                    ("score_panel", "crystal score display panel, transparent crystal background, gold number display area, decorative crystal frame borders, UI panel, transparent background", (120, 80)),  # was 150x80
                ]
            },
            
            # Memory Palace - ALL cards + UI fixes  
            "memory-palace": {
                "cards": [
                    ("rose_card", "elegant memory matching card with beautiful pink rose illustration, detailed rose drawing, royal palace style border, matching game card format, soft colors", (100, 100)),  # was 100x100 but failed
                    ("crown_card", "memory matching card with golden royal crown, detailed crown with jewels illustration, royal blue decorative border, matching game card format", (100, 100)),
                    ("castle_card", "memory matching card with cute fairy tale castle illustration, pink and purple castle colors, decorative card border, matching game format", (100, 100)),
                    ("star_card", "memory matching card with golden star illustration, sparkles around star, purple background, decorative border, matching game format", (100, 100)),
                ],
                "ui": [
                    ("match_button", "FIND MATCH button, royal palace theme, elegant readable font, gold and blue colors, rounded rectangle button, UI element", (120, 50)),  # was 180x50
                    ("pairs_counter", "pairs found counter display, elegant palace design, number display area, decorative royal frame, UI panel", (100, 60)),  # was 120x60
                ]
            },
            
            # Princess Academy UI fixes
            "princess-academy": {
                "ui": [
                    ("learn_button", "LEARN button, princess academy theme, book icon integrated, encouraging colors, educational feel, rounded button, readable font", (120, 50)),  # was 160x50
                    ("progress_bar", "learning progress bar, magical stars filling effect, milestone markers, academy colors, horizontal progress indicator", (120, 40)),  # was 200x30
                ]
            },
            
            # Rainbow Bridge UI fixes  
            "rainbow-bridge": {
                "ui": [
                    ("jump_button", "JUMP button, cloud and rainbow theme, dynamic design, encouraging colors, action button, readable font", (120, 50)),  # was 150x50
                    ("bridge_meter", "rainbow bridge progress meter, colorful rainbow gradient filling, horizontal progress bar, bright colors", (120, 40)),  # was 180x25
                ]
            },
            
            # Starlight Stable UI fixes
            "starlight-stable": {
                "ui": [
                    ("care_button", "CARE button, heart and star theme, nurturing colors, love and kindness design, rounded button, readable font", (120, 50)),  # was 150x50
                    ("happiness_meter", "unicorn happiness meter, heart-shaped design with starlight, magical filling effect, horizontal meter", (120, 40)),  # was 160x30
                ]
            }
        }
    
    def generate_asset(self, prompt, width, height, output_path, asset_name):
        """Generate a single asset using Stable Diffusion"""
        try:
            print(f"    🔧 Fixing {asset_name} ({width}x{height})...")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Run SD generation with more steps for better quality
            start_time = time.time()
            cmd = [
                'python3', str(self.sd_generator),
                '--prompt', f"{prompt}, children's board game art, cute cartoon style, bright colors, high quality, clear details",
                '--width', str(width),
                '--height', str(height), 
                '--steps', '25',  # Higher quality for fixes
                '--output', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            gen_time = time.time() - start_time
            
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                print(f"    ✅ {asset_name} FIXED ({gen_time:.1f}s) - {output_path.stat().st_size} bytes")
                self.fixed_count += 1
                return True
            else:
                print(f"    ❌ {asset_name} STILL FAILS: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                self.still_failed_count += 1
                return False
                
        except subprocess.TimeoutExpired:
            print(f"    ❌ {asset_name} timed out")
            self.still_failed_count += 1
            return False
        except Exception as e:
            print(f"    ❌ {asset_name} error: {str(e)[:100]}")
            self.still_failed_count += 1
            return False
    
    def fix_game_assets(self, game_key):
        """Fix failing assets for a specific game"""
        if game_key not in self.failing_assets:
            print(f"No failing assets recorded for {game_key}")
            return 0, 0
            
        game_data = self.failing_assets[game_key]
        print(f"\n🔧 Fixing failing assets for {game_key}")
        print("=" * 50)
        
        game_fixed = 0
        game_still_failed = 0
        
        for asset_type, assets in game_data.items():
            print(f"\n📁 {asset_type.title()} Fixes:")
            
            for asset_name, prompt, (width, height) in assets:
                output_path = self.assets_dir / game_key / asset_type / f"{asset_name}.png"
                
                if self.generate_asset(prompt, width, height, output_path, asset_name):
                    game_fixed += 1
                else:
                    game_still_failed += 1
        
        return game_fixed, game_still_failed
    
    def fix_all_failing_assets(self):
        """Fix all 14 failing assets"""
        print("🔧 FIXING FAILING ASSETS")
        print("Targeting 14 failed assets with SD-friendly dimensions")
        print("=" * 60)
        
        total_fixed = 0
        total_still_failed = 0
        start_time = time.time()
        
        for game_key in self.failing_assets.keys():
            fixed, still_failed = self.fix_game_assets(game_key)
            total_fixed += fixed
            total_still_failed += still_failed
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 FIXING COMPLETE")
        print("=" * 40)
        print(f"Assets Fixed: {total_fixed}")
        print(f"Still Failed: {total_still_failed}")
        print(f"Success Rate: {total_fixed/(total_fixed+total_still_failed)*100:.1f}%")
        print(f"Time: {total_time:.1f}s")
        
        if total_fixed > 10:
            print("\n✅ Most assets fixed! Ready for phase 2 (scaling up)")
        elif total_fixed > 5:
            print("\n⚠️  Partial success. Some assets still problematic")
        else:
            print("\n❌ Major issues remain. Need different approach")
        
        # Update counts
        current_total = 51 + total_fixed
        print(f"\nNew Total Assets: {current_total}")
        
        return total_fixed > (total_still_failed * 2)  # Success if we fix >66%

def main():
    if len(sys.argv) > 1:
        # Fix specific game
        game_key = sys.argv[1]
        fixer = FailingAssetsFixer()
        if game_key in fixer.failing_assets:
            fixer.fix_game_assets(game_key)
        else:
            print(f"No failing assets for: {game_key}")
            print(f"Games with failing assets: {list(fixer.failing_assets.keys())}")
    else:
        # Fix all failing assets
        fixer = FailingAssetsFixer()
        success = fixer.fix_all_failing_assets()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()