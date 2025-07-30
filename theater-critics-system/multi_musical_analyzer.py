#!/usr/bin/env python3
"""
Multi-Musical Analyzer
Analyzes representative scenes from all Broadway musicals with critic ensemble
"""

import asyncio
import json
import time
from pathlib import Path
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

class MultiMusicalAnalyzer:
    """Analyzes multiple musicals with theater critics ensemble"""
    
    def __init__(self, analysis_dir: str = "all_musicals_analysis"):
        self.analysis_dir = Path(analysis_dir)
        self.ensemble = CriticEnsemble()
        self.results = {}
    
    def load_conversion_summary(self) -> dict:
        """Load the conversion summary to get musical info"""
        summary_file = self.analysis_dir / "conversion_summary.json"
        with open(summary_file, 'r') as f:
            return json.load(f)
    
    def select_representative_scenes(self, musical_dir: str, scene_count: int) -> list:
        """Select key scenes for analysis (opening, middle, finale)"""
        json_dir = self.analysis_dir / musical_dir / "json"
        scene_files = sorted(json_dir.glob("scene_*.json"))
        
        if not scene_files:
            return []
        
        # Select key scenes based on count
        if scene_count == 1:
            selected = [scene_files[0]]  # Just opening
        elif scene_count == 2:
            selected = [scene_files[0], scene_files[-1]]  # Opening and finale
        elif scene_count <= 6:
            # Small musical: opening, middle, finale
            middle_idx = len(scene_files) // 2
            selected = [scene_files[0], scene_files[middle_idx], scene_files[-1]]
        else:
            # Large musical: opening, two middle scenes, finale
            quarter = len(scene_files) // 4
            half = len(scene_files) // 2
            three_quarter = 3 * len(scene_files) // 4
            selected = [scene_files[0], scene_files[quarter], scene_files[half], scene_files[three_quarter], scene_files[-1]]
        
        return selected[:4]  # Maximum 4 scenes per musical for time efficiency
    
    async def analyze_musical_scenes(self, musical_dir: str, musical_info: dict) -> dict:
        """Analyze representative scenes from one musical"""
        print(f"\n🎭 ANALYZING: {musical_info['name']}")
        print("="*60)
        
        # Select representative scenes
        scene_files = self.select_representative_scenes(musical_dir, musical_info['scene_count'])
        
        if not scene_files:
            print("❌ No scenes found to analyze")
            return {"error": "No scenes found"}
        
        print(f"📊 Analyzing {len(scene_files)} representative scenes")
        
        musical_results = {
            "musical_name": musical_info['name'],
            "total_scenes": musical_info['scene_count'],
            "analyzed_scenes": len(scene_files),
            "scene_analyses": [],
            "musical_average": 0,
            "analysis_time": 0
        }
        
        start_time = time.time()
        
        for i, scene_file in enumerate(scene_files, 1):
            try:
                # Load scene
                with open(scene_file, 'r', encoding='utf-8') as f:
                    scene_data = json.load(f)
                scene = SceneData(**scene_data)
                
                print(f"\n🎬 Scene {i}: {scene.title}")
                print("-" * 40)
                
                # Analyze with reduced critics for speed (primary + 1 rotating)
                reviews = await self.ensemble.review_scene(scene, num_rotating_critics=1)
                consensus = ConsensusAnalyzer.calculate_consensus(reviews)
                
                scene_result = {
                    "scene_title": scene.title,
                    "scene_file": scene_file.name,
                    "overall_score": consensus['average_scores']['overall'],
                    "consensus_level": consensus['consensus_level'],
                    "critics": [r.critic_name for r in reviews],
                    "category_scores": consensus['average_scores'],
                    "primary_review_preview": reviews[0].review_text[:150] + "..."
                }
                
                musical_results["scene_analyses"].append(scene_result)
                
                print(f"Score: {scene_result['overall_score']:.1f}/10.0")
                print(f"Critics: {', '.join(scene_result['critics'])}")
                
                # Brief delay between scenes
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error analyzing scene {i}: {e}")
        
        # Calculate musical average
        if musical_results["scene_analyses"]:
            scores = [s["overall_score"] for s in musical_results["scene_analyses"]]
            musical_results["musical_average"] = sum(scores) / len(scores)
        
        musical_results["analysis_time"] = time.time() - start_time
        
        print(f"\n✅ {musical_info['name']} Complete")
        print(f"Average Score: {musical_results['musical_average']:.1f}/10.0")
        print(f"Analysis Time: {musical_results['analysis_time']:.1f}s")
        
        return musical_results
    
    async def analyze_all_musicals(self):
        """Analyze representative scenes from all musicals"""
        print("🎭 MULTI-MUSICAL CRITIC ANALYSIS")
        print("="*80)
        print("Analyzing representative scenes from all Broadway musicals")
        print("Using primary critic + 1 rotating critic for efficiency")
        print()
        
        # Load musical info
        conversion_summary = self.load_conversion_summary()
        
        total_start = time.time()
        
        # Analyze each musical
        for musical_dir, musical_info in conversion_summary.items():
            try:
                result = await self.analyze_musical_scenes(musical_dir, musical_info)
                self.results[musical_dir] = result
                
                # Longer delay between musicals
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"❌ Error analyzing {musical_info['name']}: {e}")
                self.results[musical_dir] = {
                    "musical_name": musical_info['name'],
                    "error": str(e)
                }
        
        total_time = time.time() - total_start
        
        print(f"\n🏁 MULTI-MUSICAL ANALYSIS COMPLETE")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"🎭 Musicals analyzed: {len([r for r in self.results.values() if 'error' not in r])}")
        
        return self.results
    
    def generate_comparison_report(self) -> dict:
        """Generate comprehensive comparison report across all musicals"""
        successful_results = {k: v for k, v in self.results.items() if 'error' not in v}
        
        if not successful_results:
            return {"error": "No successful analyses to compare"}
        
        # Rank musicals by average score
        musical_rankings = []
        for musical_dir, result in successful_results.items():
            if result.get('musical_average', 0) > 0:
                musical_rankings.append({
                    "name": result['musical_name'],
                    "average_score": result['musical_average'],
                    "scenes_analyzed": result['analyzed_scenes'],
                    "total_scenes": result['total_scenes']
                })
        
        musical_rankings.sort(key=lambda x: x['average_score'], reverse=True)
        
        # Calculate overall statistics
        all_scores = []
        for result in successful_results.values():
            for scene in result.get('scene_analyses', []):
                all_scores.append(scene['overall_score'])
        
        # Category analysis across all musicals
        category_totals = {}
        category_counts = {}
        
        for result in successful_results.values():
            for scene in result.get('scene_analyses', []):
                for category, score in scene.get('category_scores', {}).items():
                    if category not in category_totals:
                        category_totals[category] = 0
                        category_counts[category] = 0
                    category_totals[category] += score
                    category_counts[category] += 1
        
        category_averages = {
            category: category_totals[category] / category_counts[category]
            for category in category_totals
        }
        
        comparison_report = {
            "analysis_overview": {
                "total_musicals": len(successful_results),
                "total_scenes_analyzed": sum(r.get('analyzed_scenes', 0) for r in successful_results.values()),
                "total_scenes_available": sum(r.get('total_scenes', 0) for r in successful_results.values()),
                "overall_average_score": sum(all_scores) / len(all_scores) if all_scores else 0
            },
            "musical_rankings": musical_rankings,
            "category_performance": category_averages,
            "top_individual_scenes": self.get_top_scenes(successful_results),
            "analysis_methodology": {
                "critics_used": "Primary critic (Gemma2:9b) + 1 rotating specialist",
                "scenes_per_musical": "Representative scenes (opening, middle, finale)",
                "scoring_system": "6-category evaluation (1-10 scale)"
            }
        }
        
        return comparison_report
    
    def get_top_scenes(self, successful_results: dict, top_count: int = 10) -> list:
        """Get top-rated individual scenes across all musicals"""
        all_scenes = []
        
        for result in successful_results.values():
            musical_name = result['musical_name']
            for scene in result.get('scene_analyses', []):
                all_scenes.append({
                    "musical": musical_name,
                    "scene_title": scene['scene_title'],
                    "score": scene['overall_score'],
                    "consensus": scene['consensus_level']
                })
        
        all_scenes.sort(key=lambda x: x['score'], reverse=True)
        return all_scenes[:top_count]
    
    def save_results(self, filename: str = "multi_musical_analysis_results.json"):
        """Save all analysis results"""
        output_data = {
            "analysis_metadata": {
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system": "Theater Critics Multi-Agent Ensemble",
                "scope": "Multi-Musical Broadway Collection Analysis"
            },
            "comparison_report": self.generate_comparison_report(),
            "detailed_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to {filename}")
        return filename
    
    def print_summary_report(self):
        """Print formatted summary report"""
        report = self.generate_comparison_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"\n{'='*80}")
        print("🎭 BROADWAY MUSICALS COLLECTION - CRITIC ENSEMBLE ANALYSIS")
        print(f"{'='*80}")
        
        overview = report['analysis_overview']
        print(f"\n📊 COLLECTION OVERVIEW")
        print(f"Musicals Analyzed: {overview['total_musicals']}")
        print(f"Scenes Analyzed: {overview['total_scenes_analyzed']}/{overview['total_scenes_available']}")
        print(f"Collection Average: {overview['overall_average_score']:.1f}/10.0")
        
        print(f"\n🏆 MUSICAL RANKINGS")
        print("-" * 60)
        for i, musical in enumerate(report['musical_rankings'], 1):
            print(f"{i:2d}. {musical['name']}")
            print(f"     Score: {musical['average_score']:.1f}/10.0 ({musical['scenes_analyzed']} scenes)")
        
        print(f"\n🎯 CATEGORY PERFORMANCE (All Scenes)")
        print("-" * 50)
        for category, score in sorted(report['category_performance'].items()):
            category_name = category.replace('_', ' ').title()
            print(f"{category_name:25s}: {score:.1f}/10.0")
        
        print(f"\n⭐ TOP INDIVIDUAL SCENES")
        print("-" * 50)
        for i, scene in enumerate(report['top_individual_scenes'][:5], 1):
            print(f"{i}. {scene['scene_title']} ({scene['musical']}) - {scene['score']:.1f}/10.0")

async def main():
    """Main multi-musical analysis function"""
    analyzer = MultiMusicalAnalyzer()
    
    print("🎭 Starting Multi-Musical Broadway Collection Analysis")
    print("This will analyze representative scenes from all musicals")
    print("Estimated time: 20-30 minutes for full collection\n")
    
    # Run analysis
    results = await analyzer.analyze_all_musicals()
    
    # Generate and print summary
    analyzer.print_summary_report()
    
    # Save results
    output_file = analyzer.save_results()
    
    print(f"\n✅ Multi-musical analysis complete!")
    print(f"📄 Detailed results: {output_file}")
    print(f"🎭 Analyzed {len(results)} Broadway musicals with AI theater critics")

if __name__ == "__main__":
    asyncio.run(main())