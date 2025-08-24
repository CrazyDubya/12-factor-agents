#!/usr/bin/env python3
"""
Working Stable Diffusion generator for unicorn games testing
"""

import torch
from diffusers import StableDiffusionPipeline
import sys
import time
import argparse
from pathlib import Path

class WorkingSDGenerator:
    def __init__(self):
        self.pipe = None
        self.model_loaded = False
        
    def load_model(self):
        """Load the Stable Diffusion model"""
        if self.model_loaded:
            return True
            
        try:
            print("📥 Loading Stable Diffusion model...")
            model_id = "runwayml/stable-diffusion-v1-5"
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32,
                use_safetensors=True,
                safety_checker=None,  # Disable broken safety checker
                feature_extractor=None,  # Remove feature extractor requirement
                requires_safety_checker=False  # Bypass safety requirement
            )
            
            if torch.backends.mps.is_available():
                self.pipe = self.pipe.to("mps")
                print("✅ Using Apple Silicon MPS acceleration")
            else:
                print("⚠️  Using CPU (slower)")
                
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def generate_image(self, prompt, output_path, width=512, height=512, steps=20):
        """Generate a single image"""
        if not self.model_loaded and not self.load_model():
            return False
            
        try:
            print(f"🎨 Generating: {Path(output_path).name}")
            
            with torch.no_grad():
                image = self.pipe(
                    prompt,
                    height=height,
                    width=width,
                    num_inference_steps=steps,
                    guidance_scale=7.5,
                    generator=torch.Generator().manual_seed(42)
                ).images[0]
            
            # Save image
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            # Verify
            if Path(output_path).exists() and Path(output_path).stat().st_size > 1000:
                print(f"✅ Saved: {output_path}")
                return True
            else:
                print(f"❌ Failed to save: {output_path}")
                return False
                
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Working SD Generator for Unicorn Games")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=512, help="Image height")
    parser.add_argument("--steps", type=int, default=20, help="Inference steps")
    
    args = parser.parse_args()
    
    generator = WorkingSDGenerator()
    success = generator.generate_image(
        args.prompt, 
        args.output, 
        args.width, 
        args.height, 
        args.steps
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()