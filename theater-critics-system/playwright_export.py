#!/usr/bin/env python3
"""
Theater Critics System - Playwright Export Module

This module creates playwright-friendly exports of critical evaluations
in readable text format, organized by show and scene with actionable feedback.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PlaywrightExporter:
    """Exports critical evaluations in playwright-friendly text format."""

    def __init__(self, output_dir: str = "playwright_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Analysis file mappings
        self.analysis_files = {
            "core_review": "REAL_AI_broadway_analysis.json",
            "lyrical": "LYRICAL_analysis.json", 
            "character_arc": "CHARACTER_arc_analysis.json",
            "emotional_journey": "EMOTIONAL_journey_analysis.json",
            "cultural_commentary": "CULTURAL_commentary_analysis.json",
            "dialogue_balance": "DIALOGUE_balance_analysis.json",
            "ensemble_solo": "ENSEMBLE_solo_analysis.json",
            "audience_demographic": "AUDIENCE_demographic_analysis.json",
            "genre_authenticity": "GENRE_authenticity_analysis.json",
            "genre_evolution": "GENRE_evolution_analysis.json",
            "historical_accuracy": "HISTORICAL_accuracy_analysis.json",
            "production_complexity": "PRODUCTION_complexity_analysis.json",
            "thematic_resonance": "THEMATIC_resonance_analysis.json"
        }

    def load_analysis_data(self) -> Dict[str, any]:
        """Load all available analysis data."""
        analysis_data = {}
        
        for analysis_type, filename in self.analysis_files.items():
            file_path = Path(filename)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        analysis_data[analysis_type] = data
                        print(f"✅ Loaded {analysis_type} data from {filename}")
                except Exception as e:
                    print(f"⚠️ Could not load {filename}: {e}")
            else:
                print(f"📝 {filename} not found - skipping {analysis_type}")
        
        return analysis_data

    def format_scores_summary(self, scores: Dict[str, float]) -> str:
        """Format scores in a playwright-friendly summary."""
        if not scores:
            return "No scores available"
        
        summary = []
        
        # Overall score first - check both possible locations
        overall_score = scores.get("overall", scores.get("overall_score", None))
        if overall_score is not None:
            summary.append(f"OVERALL RATING: {overall_score}/10 {'🌟' * int(overall_score/2)}")
        
        # Category scores
        category_mapping = {
            "musical_composition": "Musical Composition",
            "performance_quality": "Performance Quality", 
            "production_elements": "Production Elements",
            "narrative_integration": "Story Integration",
            "audience_engagement": "Audience Appeal",
            "specialty_score": "Specialty Focus"
        }
        
        for key, label in category_mapping.items():
            if key in scores:
                score = scores[key]
                summary.append(f"  {label}: {score}/10")
        
        return "\n".join(summary)

    def format_key_insights(self, review_data: Dict) -> str:
        """Extract and format key insights for playwright."""
        insights = []
        
        # Strengths - check multiple possible field names
        strengths = review_data.get("key_strengths", review_data.get("real_strengths", []))
        if strengths:
            insights.append("🎭 WHAT'S WORKING WELL:")
            for i, strength in enumerate(strengths[:5], 1):
                insights.append(f"  {i}. {strength}")
        
        # Areas for improvement - check multiple possible field names
        improvements = review_data.get("areas_for_improvement", review_data.get("real_improvements", []))
        if improvements:
            insights.append("\n📝 AREAS TO CONSIDER:")
            for i, improvement in enumerate(improvements[:5], 1):
                insights.append(f"  {i}. {improvement}")
        
        # Review text - check multiple possible field names
        review_text = review_data.get("review_text", review_data.get("real_ai_review", ""))
        if review_text and review_text.strip():
            insights.append(f"\n📖 CRITICAL ASSESSMENT:")
            # Truncate if too long for readability
            if len(review_text) > 400:
                review_text = review_text[:400] + "..."
            insights.append(f"  {review_text}")
        
        # Specialty analysis
        analysis = review_data.get("specialty_analysis", "")
        if analysis and analysis.strip():
            insights.append(f"\n🎨 EXPERT PERSPECTIVE:")
            # Truncate if too long
            if len(analysis) > 300:
                analysis = analysis[:300] + "..."
            insights.append(f"  {analysis}")
        
        return "\n".join(insights)

    def format_detailed_analysis(self, analysis_type: str, data: Dict) -> str:
        """Format detailed analysis for specific evaluation type."""
        if not data or "rankings" not in data:
            return f"No {analysis_type} data available"
        
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"📊 {analysis_type.upper().replace('_', ' ')} ANALYSIS")
        output.append(f"{'='*60}")
        
        # Metadata
        if "analysis_metadata" in data:
            metadata = data["analysis_metadata"]
            if "total_scenes" in metadata:
                output.append(f"Scenes Analyzed: {metadata['total_scenes']}")
            if "collection_average" in metadata:
                output.append(f"Collection Average: {metadata['collection_average']}/10")
        
        # Top performers
        rankings = data["rankings"][:3]  # Top 3
        output.append(f"\n🏆 TOP PERFORMING SCENES:")
        
        for i, scene in enumerate(rankings, 1):
            title = scene.get("scene_title", "Unknown Scene")
            musical = scene.get("musical_name", "Unknown Musical")
            
            if "scores" in scene:
                scores = scene["scores"]
                overall = scores.get("overall_score", scores.get("overall", "N/A"))
                output.append(f"  {i}. {title} ({musical}) - {overall}/10")
                
                # Key insights for this scene
                if "analysis_details" in scene:
                    details = scene["analysis_details"]
                    if isinstance(details, dict):
                        # Look for key findings
                        for key in ["key_findings", "strengths", "recommendations"]:
                            if key in details and details[key]:
                                items = details[key][:2]  # Top 2 items
                                for item in items:
                                    output.append(f"     • {item}")
        
        return "\n".join(output)

    def create_scene_report(self, scene_title: str, musical_name: str, 
                          analysis_data: Dict[str, any]) -> str:
        """Create comprehensive scene report for playwright."""
        
        report = []
        report.append(f"{'='*80}")
        report.append(f"🎭 SCENE ANALYSIS REPORT")
        report.append(f"{'='*80}")
        report.append(f"Scene: {scene_title}")
        report.append(f"Musical: {musical_name}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*80}")
        
        # Core review first
        if "core_review" in analysis_data:
            core_data = analysis_data["core_review"]
            # Find this scene in core reviews - handle both data structures
            scene_review = None
            reviews_list = core_data.get("reviews", core_data.get("real_musical_rankings", []))
            for review in reviews_list:
                review_scene_title = review.get("scene_title", review.get("title", ""))
                review_musical = review.get("musical", review.get("name", ""))
                if (scene_title.lower() in review_scene_title.lower() and
                    musical_name.lower() in review_musical.lower()):
                    scene_review = review
                    break
            
            if scene_review:
                report.append(f"\n🎯 CORE CRITICAL REVIEW")
                report.append(f"{'-'*40}")
                
                # Scores summary - check both possible locations
                scores = scene_review.get("scores", scene_review.get("category_scores", {}))
                if scores:
                    scores_text = self.format_scores_summary(scores)
                    report.append(scores_text)
                
                # Review text - check multiple possible field names
                review_text = scene_review.get("review_text", scene_review.get("real_ai_review", ""))
                if review_text:
                    report.append(f"\n📝 CRITIC'S ASSESSMENT:")
                    report.append(f"{review_text}")
                
                # Key insights
                insights = self.format_key_insights(scene_review)
                if insights:
                    report.append(f"\n{insights}")
        
        # Specialized analyses
        specialized_sections = {
            "lyrical": "🎵 LYRICAL ANALYSIS",
            "character_arc": "👥 CHARACTER DEVELOPMENT", 
            "emotional_journey": "💭 EMOTIONAL IMPACT",
            "cultural_commentary": "🌍 CULTURAL RELEVANCE",
            "dialogue_balance": "🗣️ DIALOGUE & BALANCE",
            "thematic_resonance": "🎨 THEMATIC DEPTH"
        }
        
        for analysis_type, section_title in specialized_sections.items():
            if analysis_type in analysis_data:
                data = analysis_data[analysis_type]
                
                # Find scene data
                scene_data = self.find_scene_in_analysis(scene_title, musical_name, data)
                if scene_data:
                    report.append(f"\n{section_title}")
                    report.append(f"{'-'*40}")
                    
                    # Scores if available
                    if "scores" in scene_data:
                        scores = scene_data["scores"]
                        if isinstance(scores, dict):
                            for key, value in scores.items():
                                if "overall" in key or "score" in key:
                                    clean_key = key.replace("_", " ").title()
                                    report.append(f"{clean_key}: {value}/10")
                    
                    # Key findings
                    if "analysis_details" in scene_data:
                        details = scene_data["analysis_details"]
                        if isinstance(details, dict):
                            for key in ["key_findings", "strengths", "insights", "recommendations"]:
                                if key in details and details[key]:
                                    items = details[key][:3]  # Top 3
                                    key_title = key.replace("_", " ").title()
                                    report.append(f"\n{key_title}:")
                                    for item in items:
                                        report.append(f"  • {item}")
        
        # Overall recommendations
        report.append(f"\n{'='*80}")
        report.append(f"📋 PLAYWRIGHT RECOMMENDATIONS")
        report.append(f"{'='*80}")
        
        recommendations = self.generate_playwright_recommendations(scene_title, analysis_data)
        for rec in recommendations:
            report.append(f"• {rec}")
        
        report.append(f"\n{'='*80}")
        report.append(f"End of Scene Analysis Report")
        report.append(f"{'='*80}")
        
        return "\n".join(report)

    def find_scene_in_analysis(self, scene_title: str, musical_name: str, data: Dict) -> Optional[Dict]:
        """Find scene data within analysis results."""
        if not data or "rankings" not in data:
            return None
        
        for item in data["rankings"]:
            # Check scene title match
            item_title = item.get("scene_title", "")
            item_musical = item.get("musical_name", "")
            
            if (scene_title.lower() in item_title.lower() and 
                musical_name.lower() in item_musical.lower()):
                return item
        
        return None

    def generate_playwright_recommendations(self, scene_title: str, analysis_data: Dict) -> List[str]:
        """Generate actionable recommendations for playwright."""
        recommendations = []
        
        # Analyze patterns across all data
        score_totals = {}
        issue_patterns = []
        strength_patterns = []
        
        for analysis_type, data in analysis_data.items():
            scene_data = self.find_scene_in_analysis(scene_title, "", data)
            if scene_data and "scores" in scene_data:
                scores = scene_data["scores"]
                if isinstance(scores, dict):
                    for key, value in scores.items():
                        if isinstance(value, (int, float)):
                            if key not in score_totals:
                                score_totals[key] = []
                            score_totals[key].append(value)
        
        # Generate recommendations based on score patterns
        for score_type, values in score_totals.items():
            if values:
                avg_score = sum(values) / len(values)
                if avg_score < 6.0:
                    category = score_type.replace("_", " ").title()
                    recommendations.append(f"Focus on improving {category} (current avg: {avg_score:.1f}/10)")
                elif avg_score >= 8.0:
                    category = score_type.replace("_", " ").title()
                    recommendations.append(f"Leverage your strength in {category} (current avg: {avg_score:.1f}/10)")
        
        # Default recommendations if no specific patterns found
        if not recommendations:
            recommendations = [
                "Consider strengthening the emotional arc of key characters",
                "Evaluate pacing and dramatic tension throughout the scene", 
                "Review dialogue for authenticity and character voice",
                "Assess musical numbers for narrative integration",
                "Consider audience engagement and accessibility"
            ]
        
        return recommendations[:5]  # Limit to 5 key recommendations

    def export_by_musical(self, analysis_data: Dict[str, any]) -> None:
        """Export reports organized by musical."""
        
        # Group scenes by musical
        musicals = {}
        
        # Extract from core review data
        if "core_review" in analysis_data:
            # Handle the real_musical_rankings structure
            if "real_musical_rankings" in analysis_data["core_review"]:
                for review in analysis_data["core_review"]["real_musical_rankings"]:
                    musical = review.get("name", "Unknown Musical")
                    scene = review.get("scene_title", "Unknown Scene")
                    
                    if musical not in musicals:
                        musicals[musical] = []
                    musicals[musical].append({
                        "scene_title": scene,
                        "review_data": review
                    })
            # Handle the standard reviews structure as fallback
            elif "reviews" in analysis_data["core_review"]:
                for review in analysis_data["core_review"]["reviews"]:
                    musical = review.get("musical", "Unknown Musical")
                    scene = review.get("scene_title", review.get("title", "Unknown Scene"))
                    
                    if musical not in musicals:
                        musicals[musical] = []
                    musicals[musical].append({
                        "scene_title": scene,
                        "review_data": review
                    })
        
        # Create reports for each musical
        for musical_name, scenes in musicals.items():
            safe_name = "".join(c for c in musical_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(" ", "_").lower()
            
            # Musical overview report
            musical_report = self.create_musical_overview(musical_name, scenes, analysis_data)
            overview_file = self.output_dir / f"{safe_name}_overview.txt"
            with open(overview_file, 'w', encoding='utf-8') as f:
                f.write(musical_report)
            
            print(f"📄 Created musical overview: {overview_file}")
            
            # Individual scene reports
            scene_dir = self.output_dir / safe_name
            scene_dir.mkdir(exist_ok=True)
            
            for scene_info in scenes:
                scene_title = scene_info["scene_title"]
                scene_report = self.create_scene_report(scene_title, musical_name, analysis_data)
                
                safe_scene_name = "".join(c for c in scene_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_scene_name = safe_scene_name.replace(" ", "_").lower()
                
                scene_file = scene_dir / f"{safe_scene_name}_analysis.txt"
                with open(scene_file, 'w', encoding='utf-8') as f:
                    f.write(scene_report)
                
                print(f"📄 Created scene report: {scene_file}")

    def create_musical_overview(self, musical_name: str, scenes: List[Dict], 
                               analysis_data: Dict[str, any]) -> str:
        """Create overview report for entire musical."""
        
        report = []
        report.append(f"{'='*90}")
        report.append(f"🎭 MUSICAL OVERVIEW REPORT")
        report.append(f"{'='*90}")
        report.append(f"Musical: {musical_name}")
        report.append(f"Scenes Analyzed: {len(scenes)}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*90}")
        
        # Overall statistics
        total_scores = []
        for scene in scenes:
            review_data = scene["review_data"]
            # Check multiple possible score locations
            scores = review_data.get("scores", review_data.get("category_scores", {}))
            overall = scores.get("overall", scores.get("overall_score", review_data.get("overall_score", 0)))
            if overall > 0:
                total_scores.append(overall)
        
        if total_scores:
            avg_score = sum(total_scores) / len(total_scores)
            max_score = max(total_scores)
            min_score = min(total_scores)
            
            report.append(f"\n📊 OVERALL PERFORMANCE")
            report.append(f"{'-'*50}")
            report.append(f"Average Score: {avg_score:.1f}/10 {'🌟' * int(avg_score/2)}")
            report.append(f"Score Range: {min_score:.1f} - {max_score:.1f}")
            report.append(f"Total Scenes: {len(scenes)}")
        
        # Scene performance ranking
        def get_scene_score(scene):
            review_data = scene["review_data"]
            scores = review_data.get("scores", review_data.get("category_scores", {}))
            return scores.get("overall", scores.get("overall_score", review_data.get("overall_score", 0)))
        
        sorted_scenes = sorted(scenes, key=get_scene_score, reverse=True)
        
        report.append(f"\n🏆 SCENE PERFORMANCE RANKING")
        report.append(f"{'-'*50}")
        
        for i, scene in enumerate(sorted_scenes[:10], 1):  # Top 10
            title = scene["scene_title"]
            score = get_scene_score(scene)
            score_display = f"{score}/10" if score > 0 else "N/A"
            report.append(f"{i:2d}. {title} - {score_display}")
        
        # Common strengths across musical
        all_strengths = []
        all_improvements = []
        
        for scene in scenes:
            review_data = scene["review_data"]
            # Extract strengths from multiple possible field names
            strengths = review_data.get("key_strengths", review_data.get("real_strengths", []))
            if strengths:
                all_strengths.extend(strengths)
            # Extract improvements from multiple possible field names
            improvements = review_data.get("areas_for_improvement", review_data.get("real_improvements", []))
            if improvements:
                all_improvements.extend(improvements)
        
        # Find common patterns
        strength_patterns = self.find_common_patterns(all_strengths)
        improvement_patterns = self.find_common_patterns(all_improvements)
        
        if strength_patterns:
            report.append(f"\n🎯 RECURRING STRENGTHS")
            report.append(f"{'-'*50}")
            for pattern, count in strength_patterns[:5]:
                report.append(f"• {pattern} (mentioned {count} times)")
        
        if improvement_patterns:
            report.append(f"\n📝 RECURRING IMPROVEMENT AREAS")
            report.append(f"{'-'*50}")
            for pattern, count in improvement_patterns[:5]:
                report.append(f"• {pattern} (mentioned {count} times)")
        
        # Overall recommendations for the musical
        report.append(f"\n{'='*90}")
        report.append(f"🎨 PLAYWRIGHT RECOMMENDATIONS FOR {musical_name.upper()}")
        report.append(f"{'='*90}")
        
        musical_recommendations = self.generate_musical_recommendations(musical_name, scenes, analysis_data)
        for i, rec in enumerate(musical_recommendations, 1):
            report.append(f"{i}. {rec}")
        
        report.append(f"\n{'='*90}")
        report.append(f"End of Musical Overview Report")
        report.append(f"{'='*90}")
        
        return "\n".join(report)

    def find_common_patterns(self, items: List[str]) -> List[tuple]:
        """Find common patterns in feedback items."""
        if not items:
            return []
        
        # Simple pattern matching based on key words
        patterns = {}
        for item in items:
            words = item.lower().split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    patterns[word] = patterns.get(word, 0) + 1
        
        # Return top patterns
        return sorted(patterns.items(), key=lambda x: x[1], reverse=True)

    def generate_musical_recommendations(self, musical_name: str, scenes: List[Dict], 
                                       analysis_data: Dict[str, any]) -> List[str]:
        """Generate overall recommendations for the musical."""
        
        recommendations = []
        
        # Analyze score patterns across all scenes
        category_scores = {}
        for scene in scenes:
            review_data = scene["review_data"]
            # Check multiple possible score locations
            scores = review_data.get("scores", review_data.get("category_scores", {}))
            for category, score in scores.items():
                if isinstance(score, (int, float)):
                    if category not in category_scores:
                        category_scores[category] = []
                    category_scores[category].append(score)
        
        # Generate recommendations based on patterns
        for category, scores in category_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                category_name = category.replace("_", " ").title()
                
                if avg_score < 6.0:
                    recommendations.append(
                        f"Priority Focus: {category_name} needs improvement across multiple scenes "
                        f"(average: {avg_score:.1f}/10)"
                    )
                elif avg_score >= 8.5:
                    recommendations.append(
                        f"Maintain Excellence: {category_name} is a consistent strength "
                        f"(average: {avg_score:.1f}/10)"
                    )
        
        # Add general structural recommendations
        if len(scenes) < 5:
            recommendations.append("Consider expanding the musical with additional scenes for fuller narrative development")
        elif len(scenes) > 15:
            recommendations.append("Review pacing - consider if all scenes are essential for the narrative flow")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                "Focus on creating stronger emotional arcs across scenes",
                "Ensure consistent character development throughout the musical",
                "Balance musical numbers with dialogue for optimal pacing",
                "Consider audience accessibility and engagement",
                "Review thematic consistency across all scenes"
            ]
        
        return recommendations[:7]  # Limit to 7 key recommendations

    def run_export(self) -> None:
        """Run the complete export process."""
        print(f"\n🎭 THEATER CRITICS PLAYWRIGHT EXPORT")
        print(f"{'='*60}")
        print(f"Loading analysis data...")
        
        analysis_data = self.load_analysis_data()
        
        if not analysis_data:
            print("❌ No analysis data found. Please run analyses first.")
            return
        
        print(f"\n📊 Found {len(analysis_data)} analysis types")
        print(f"Output directory: {self.output_dir.absolute()}")
        
        # Export by musical
        self.export_by_musical(analysis_data)
        
        # Create master index
        self.create_master_index()
        
        print(f"\n✅ Playwright export complete!")
        print(f"📁 Check {self.output_dir.absolute()} for all reports")

    def create_master_index(self) -> None:
        """Create master index of all generated reports."""
        index_content = []
        index_content.append(f"🎭 THEATER CRITICS PLAYWRIGHT REPORTS INDEX")
        index_content.append(f"{'='*70}")
        index_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        index_content.append(f"")
        
        # List all generated files
        index_content.append(f"📁 AVAILABLE REPORTS:")
        index_content.append(f"{'-'*30}")
        
        for item in sorted(self.output_dir.iterdir()):
            if item.is_file() and item.suffix == '.txt':
                size_kb = item.stat().st_size / 1024
                index_content.append(f"📄 {item.name} ({size_kb:.1f} KB)")
            elif item.is_dir():
                scene_count = len(list(item.glob("*.txt")))
                index_content.append(f"📂 {item.name}/ ({scene_count} scene reports)")
        
        index_content.append(f"")
        index_content.append(f"💡 HOW TO USE THESE REPORTS:")
        index_content.append(f"• Musical overview files provide high-level insights")
        index_content.append(f"• Scene-specific files offer detailed analysis")
        index_content.append(f"• Focus on 'Playwright Recommendations' sections")
        index_content.append(f"• Use scores to prioritize improvement areas")
        
        index_file = self.output_dir / "INDEX.txt"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(index_content))
        
        print(f"📄 Created master index: {index_file}")


def main():
    """Main entry point for playwright export."""
    exporter = PlaywrightExporter()
    exporter.run_export()


if __name__ == "__main__":
    main()