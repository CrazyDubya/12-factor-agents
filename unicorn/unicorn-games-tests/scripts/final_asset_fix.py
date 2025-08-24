#!/usr/bin/env python3
"""
Final Asset Fix - Address Both Root Causes
1. Remove text from button prompts (SD can't generate readable text)
2. Use 8-divisible dimensions (SD requirement)
3. Simplify Memory Palace card prompts
"""

import os
import sys
import time
import subprocess
from pathlib import Path

class FinalAssetFixer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sd_generator = self.base_dir / "working_sd_generator.py"
        self.assets_dir = self.base_dir / "unicorn-games" / "assets"
        self.fixed_count = 0
        self.still_failed_count = 0
        
        # Final fixes - no text, 8-divisible dimensions, simpler prompts
        self.final_fixes = {
            # Crystal Crown
            "crystal-crown": {
                "ui": [
                    ("start_button", "crystal game button, rounded rectangle, sparkly crystal texture, golden glow, magical button design, no text", (120, 64)),  # 8-divisible
                ]
            },
            
            # Memory Palace - Simplified card prompts
            "memory-palace": {
                "cards": [
                    ("rose_card", "simple pink rose on white background, card format, memory game card, clean design", (96, 96)),  # Square, 8-divisible
                    ("crown_card", "golden crown illustration on card background, simple design, memory game card, royal theme", (96, 96)),
                    ("castle_card", "fairy tale castle illustration, pink castle, card background, simple cartoon style", (96, 96)),
                    ("star_card", "golden star with sparkles, card background, simple design, memory game card", (96, 96)),
                ],
                "ui": [
                    ("match_button", "royal game button, elegant design, gold and blue colors, rounded rectangle, no text", (120, 56)),  # 8-divisible
                    ("pairs_counter", "elegant number display panel, royal palace theme, decorative frame, score display", (112, 64)),  # 8-divisible
                ]
            },
            
            # Princess Academy
            "princess-academy": {
                "ui": [
                    ("learn_button", "academy game button, book symbol, educational colors, rounded design, no text", (120, 56)),  # 8-divisible
                ]
            },
            
            # Rainbow Bridge
            "rainbow-bridge": {
                "ui": [
                    ("jump_button", "action game button, cloud and rainbow design, dynamic style, bright colors, no text", (120, 56)),  # 8-divisible
                ]
            },
            
            # Starlight Stable
            "starlight-stable": {
                "ui": [
                    ("care_button", "heart-shaped game button, star decoration, nurturing colors, magical design, no text", (120, 56)),  # 8-divisible
                ]
            }
        }
    
    def generate_asset(self, prompt, width, height, output_path, asset_name):
        """Generate a single asset using Stable Diffusion"""
        try:
            print(f"    🎯 Final fix: {asset_name} ({width}x{height})...")
            
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Enhanced prompt for better results
            enhanced_prompt = f"{prompt}, children's board game art, cute cartoon style, bright colors, high quality, clean design, transparent background"
            
            # Run SD generation
            start_time = time.time()
            cmd = [
                'python3', str(self.sd_generator),
                '--prompt', enhanced_prompt,
                '--width', str(width),
                '--height', str(height),
                '--steps', '30',  # High quality for final fix
                '--output', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            gen_time = time.time() - start_time
            
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                print(f"    ✅ {asset_name} FINALLY FIXED ({gen_time:.1f}s) - {output_path.stat().st_size} bytes")
                self.fixed_count += 1
                return True
            else:
                print(f"    ❌ {asset_name} still problematic: {result.stderr[:100] if result.stderr else 'Unknown error'}")
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
    
    def final_fix_all(self):
        """Apply final fixes to remaining problematic assets"""
        print("🎯 FINAL ASSET FIXES")
        print("Applying lessons learned:")
        print("- No text in button prompts")
        print("- 8-divisible dimensions only") 
        print("- Simplified card prompts")
        print("=" * 50)
        
        total_fixed = 0
        total_still_failed = 0
        start_time = time.time()
        
        for game_key, asset_types in self.final_fixes.items():
            print(f"\n🎮 {game_key.title()} Final Fixes:")
            
            for asset_type, assets in asset_types.items():
                print(f"\n📁 {asset_type.title()}:")
                
                for asset_name, prompt, (width, height) in assets:
                    output_path = self.assets_dir / game_key / asset_type / f"{asset_name}.png"
                    
                    if self.generate_asset(prompt, width, height, output_path, asset_name):
                        total_fixed += 1
                    else:
                        total_still_failed += 1
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 FINAL FIX COMPLETE")
        print("=" * 35)
        print(f"Finally Fixed: {total_fixed}")
        print(f"Hopeless Cases: {total_still_failed}")
        print(f"Success Rate: {total_fixed/(total_fixed+total_still_failed)*100:.1f}%")
        print(f"Time: {total_time:.1f}s")
        
        # Calculate new totals
        original_total = 51  # From first generation
        first_fix = 4       # From first fix attempt
        final_fix = total_fixed
        new_total = original_total + first_fix + final_fix
        
        print(f"\nAsset Count Progress:")
        print(f"  Original generation: 51")
        print(f"  First fix attempt: +4 = 55")
        print(f"  Final fix: +{final_fix} = {new_total}")
        
        success_threshold = 8  # Need to fix most of the 10 remaining
        if total_fixed >= success_threshold:
            print(f"\n✅ SUCCESS! Fixed most problematic assets")
            print(f"Ready for Phase 2: Scaling up to hundreds of assets")
        else:
            print(f"\n⚠️  Partial success. {total_still_failed} assets remain problematic")
            print("May need to generate alternative assets or use different approach")
        
        return total_fixed >= success_threshold

def main():
    fixer = FinalAssetFixer()
    success = fixer.final_fix_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()