#!/usr/bin/env python3
"""
Batch Rainbow Academy Musical Analysis System
Analyzes all scenes with theater critics ensemble and generates comprehensive report
"""

import asyncio
import json
import time
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer, print_review_summary

class RainbowBatchAnalyzer:
    """Batch analyzer for Rainbow Academy Musical scenes"""
    
    def __init__(self, scenes_dir: str = "rainbow_scenes_json"):
        self.scenes_dir = Path(scenes_dir)
        self.ensemble = CriticEnsemble()
        self.results = []
    
    def load_scene_from_json(self, filepath: Path) -> SceneData:
        """Load scene from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return SceneData(**data)
    
    async def analyze_single_scene(self, scene: SceneData, scene_num: int) -> dict:
        """Analyze single scene with critic ensemble"""
        print(f"\n{'='*80}")
        print(f"🎭 ANALYZING SCENE {scene_num}: {scene.title}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # Get reviews from critic ensemble
            reviews = await self.ensemble.review_scene(scene, num_rotating_critics=3)
            
            # Calculate consensus
            consensus = ConsensusAnalyzer.calculate_consensus(reviews)
            
            analysis_time = time.time() - start_time
            
            # Create result record
            result = {
                "scene_number": scene_num,
                "scene_title": scene.title,
                "analysis_time": round(analysis_time, 2),
                "scene_data": scene.__dict__,
                "reviews": [
                    {
                        "critic_name": review.critic_name,
                        "critic_type": review.critic_type.value,
                        "model_used": review.model_used,
                        "scores": review.scores.__dict__,
                        "review_text": review.review_text[:300] + "..." if len(review.review_text) > 300 else review.review_text,
                        "key_strengths": review.key_strengths,
                        "areas_for_improvement": review.areas_for_improvement,
                        "specialty_analysis": review.specialty_analysis[:200] + "..." if len(review.specialty_analysis) > 200 else review.specialty_analysis
                    }
                    for review in reviews
                ],
                "consensus": consensus
            }
            
            # Print summary
            print(f"⏱️  Analysis completed in {analysis_time:.1f}s")
            print(f"📊 Consensus: {consensus['consensus_level']}")
            print(f"🎯 Overall Score: {consensus['average_scores']['overall']:.1f}/10.0")
            print(f"👥 Critics: {', '.join([r.critic_name for r in reviews])}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing scene {scene_num}: {e}")
            return {
                "scene_number": scene_num,
                "scene_title": scene.title,
                "error": str(e),
                "analysis_time": time.time() - start_time
            }
    
    async def analyze_all_scenes(self) -> list:
        """Analyze all scenes in the musical"""
        print("🎭 RAINBOW ACADEMY MUSICAL - COMPREHENSIVE CRITIC ANALYSIS")
        print("="*80)
        
        # Load all scene files
        scene_files = sorted(self.scenes_dir.glob("*.json"))
        
        if not scene_files:
            print("❌ No scene files found in rainbow_scenes_json/")
            return []
        
        print(f"📁 Found {len(scene_files)} scenes to analyze")
        
        total_start = time.time()
        
        # Analyze each scene
        for i, filepath in enumerate(scene_files, 1):
            try:
                scene = self.load_scene_from_json(filepath)
                result = await self.analyze_single_scene(scene, i)
                self.results.append(result)
                
                # Small delay between scenes to prevent overwhelming Ollama
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Failed to process {filepath.name}: {e}")
                self.results.append({
                    "scene_number": i,
                    "scene_title": filepath.stem,
                    "error": f"Failed to load scene: {e}",
                    "analysis_time": 0
                })
        
        total_time = time.time() - total_start
        
        print(f"\n🏁 BATCH ANALYSIS COMPLETE")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📊 Scenes analyzed: {len([r for r in self.results if 'error' not in r])}/{len(scene_files)}")
        
        return self.results
    
    def generate_summary_report(self) -> dict:
        """Generate comprehensive summary report"""
        successful_results = [r for r in self.results if 'error' not in r]
        
        if not successful_results:
            return {"error": "No successful analyses to summarize"}
        
        # Calculate overall statistics
        all_scores = []
        category_scores = {
            'overall': [],
            'musical_composition': [],
            'performance_quality': [],
            'production_elements': [],
            'narrative_integration': [],
            'audience_engagement': []
        }
        
        consensus_levels = []
        critic_participation = {}
        
        for result in successful_results:
            consensus = result['consensus']
            all_scores.append(consensus['average_scores']['overall'])
            consensus_levels.append(consensus['consensus_level'])
            
            # Collect category scores
            for category in category_scores:
                category_scores[category].append(consensus['average_scores'][category])
            
            # Track critic participation
            for review in result['reviews']:
                critic_name = review['critic_name']
                critic_participation[critic_name] = critic_participation.get(critic_name, 0) + 1
        
        # Calculate averages
        avg_category_scores = {
            category: sum(scores) / len(scores)
            for category, scores in category_scores.items()
        }
        
        # Find highest and lowest rated scenes
        scored_scenes = [(r['consensus']['average_scores']['overall'], r['scene_title'], r['scene_number']) 
                        for r in successful_results]
        scored_scenes.sort(reverse=True)
        
        summary = {
            "total_scenes": len(self.results),
            "successful_analyses": len(successful_results),
            "overall_musical_score": sum(all_scores) / len(all_scores),
            "category_averages": avg_category_scores,
            "highest_rated_scenes": scored_scenes[:3],
            "lowest_rated_scenes": scored_scenes[-3:],
            "consensus_distribution": {
                level: consensus_levels.count(level) 
                for level in set(consensus_levels)
            },
            "critic_participation": critic_participation,
            "total_analysis_time": sum(r.get('analysis_time', 0) for r in self.results)
        }
        
        return summary
    
    def save_results(self, filename: str = "rainbow_academy_analysis_results.json"):
        """Save all results to JSON file"""
        output_data = {
            "analysis_metadata": {
                "musical": "Rainbow Academy Musical",
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "critic_system": "Theater Critics Multi-Agent Ensemble",
                "total_scenes": len(self.results)
            },
            "summary_report": self.generate_summary_report(),
            "detailed_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to {filename}")
        return filename
    
    def print_summary_report(self):
        """Print formatted summary report"""
        summary = self.generate_summary_report()
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"\n{'='*80}")
        print("🎭 RAINBOW ACADEMY MUSICAL - CRITIC ENSEMBLE SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n📊 OVERALL ASSESSMENT")
        print(f"Musical Score: {summary['overall_musical_score']:.1f}/10.0")
        print(f"Scenes Analyzed: {summary['successful_analyses']}/{summary['total_scenes']}")
        print(f"Analysis Time: {summary['total_analysis_time']/60:.1f} minutes")
        
        print(f"\n🎯 CATEGORY BREAKDOWN")
        for category, score in summary['category_averages'].items():
            category_name = category.replace('_', ' ').title()
            print(f"{category_name:20s}: {score:.1f}/10.0")
        
        print(f"\n🏆 TOP RATED SCENES")
        for i, (score, title, num) in enumerate(summary['highest_rated_scenes'], 1):
            print(f"{i}. Scene {num}: {title} ({score:.1f}/10.0)")
        
        print(f"\n📉 LOWEST RATED SCENES")
        for i, (score, title, num) in enumerate(summary['lowest_rated_scenes'], 1):
            print(f"{i}. Scene {num}: {title} ({score:.1f}/10.0)")
        
        print(f"\n🤝 CONSENSUS ANALYSIS")
        for level, count in summary['consensus_distribution'].items():
            print(f"{level}: {count} scenes")
        
        print(f"\n👥 CRITIC PARTICIPATION")
        for critic, count in sorted(summary['critic_participation'].items()):
            print(f"{critic}: {count} scenes")

async def main():
    """Main batch analysis function"""
    analyzer = RainbowBatchAnalyzer()
    
    print("🎭 Starting Rainbow Academy Musical batch analysis...")
    print("This will analyze all 11 scenes with the critic ensemble")
    print("Estimated time: 15-20 minutes\n")
    
    # Run batch analysis
    results = await analyzer.analyze_all_scenes()
    
    # Generate and print summary
    analyzer.print_summary_report()
    
    # Save results
    output_file = analyzer.save_results()
    
    print(f"\n✅ Batch analysis complete!")
    print(f"📄 Detailed results: {output_file}")
    print(f"🎭 {len(results)} scenes analyzed by AI theater critics")

if __name__ == "__main__":
    asyncio.run(main())