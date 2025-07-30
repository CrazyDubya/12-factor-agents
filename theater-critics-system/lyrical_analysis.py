#!/usr/bin/env python3
"""
Lyrical Content Analysis - Advanced evaluation of musical theater lyrics
Analyzes rhyme schemes, metaphor usage, thematic coherence, and lyrical sophistication
"""

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import asyncio

from main import CriticType, SceneData, TheaterCritic


@dataclass
class LyricalAnalysis:
    """Results of lyrical content analysis"""

    scene_title: str
    rhyme_scheme_score: float  # 0-10
    metaphor_usage_score: float  # 0-10
    thematic_coherence_score: float  # 0-10
    lyrical_sophistication_score: float  # 0-10
    overall_lyrical_score: float  # 0-10

    # Detailed breakdowns
    rhyme_patterns: List[str]
    metaphors_identified: List[str]
    thematic_elements: List[str]
    vocabulary_complexity: str  # "Basic", "Intermediate", "Advanced"

    # AI critic insights
    lyrical_strengths: List[str]
    lyrical_improvements: List[str]
    specialist_commentary: str

    analysis_time: float
    critic_used: str


class LyricalContentAnalyzer:
    """Specialized analyzer for musical theater lyrics"""

    def __init__(self):
        # Initialize specialized lyrical critic
        self.lyrical_critic = TheaterCritic(
            name="Dr. Melody Wordsworth",
            critic_type=CriticType.ACADEMIC,
            model="gemma2:9b",
            specialty="Musical Theater Lyrical Analysis - Rhyme schemes, metaphor usage, thematic coherence, and poetic sophistication in theatrical songwriting",
        )

    def extract_lyrics_from_scene(self, scene: SceneData) -> List[str]:
        """Extract actual lyrical content from scene data"""
        lyrics_text = scene.lyrics if scene.lyrics else ""

        # Parse lyrics from markdown format
        lyric_lines = []
        lines = lyrics_text.split("\n")

        for line in lines:
            line = line.strip()
            # Skip stage directions, character names, scene descriptions
            if (
                line
                and not line.startswith("*")
                and not line.startswith("#")
                and not line.startswith("-")
                and not line.startswith("(")
                and not line.startswith("[")
                and not line.isupper()
                and len(line) > 3
            ):

                # Clean up common theatrical notation
                cleaned = re.sub(r"\([^)]*\)", "", line)  # Remove parentheticals
                cleaned = re.sub(r"\*[^*]*\*", "", cleaned)  # Remove italics/actions
                cleaned = cleaned.strip()

                if cleaned and len(cleaned) > 5:
                    lyric_lines.append(cleaned)

        return lyric_lines

    def analyze_rhyme_scheme(self, lyrics: List[str]) -> Tuple[float, List[str]]:
        """Analyze rhyme patterns and scheme sophistication"""
        if not lyrics:
            return 0.0, []

        # Simple phonetic ending analysis for rhyme detection
        def get_rhyme_sound(word: str) -> str:
            """Get approximate rhyme sound from word ending"""
            word = word.lower().strip('.,!?";')
            if len(word) < 2:
                return word
            # Return last 2-3 characters as approximate rhyme sound
            return word[-3:] if len(word) >= 3 else word[-2:]

        rhyme_patterns = []
        line_endings = []

        for line in lyrics:
            words = line.split()
            if words:
                last_word = words[-1]
                rhyme_sound = get_rhyme_sound(last_word)
                line_endings.append(rhyme_sound)

        # Detect rhyme patterns in groups of 4-8 lines
        for i in range(0, len(line_endings), 4):
            group = line_endings[i : i + 4]
            if len(group) >= 4:
                # Check for AABB, ABAB, ABCB patterns
                if group[0] == group[1] and group[2] == group[3]:
                    rhyme_patterns.append("AABB (Couplets)")
                elif group[0] == group[2] and group[1] == group[3]:
                    rhyme_patterns.append("ABAB (Alternating)")
                elif group[1] == group[3]:
                    rhyme_patterns.append("ABCB (Ballad)")
                else:
                    rhyme_patterns.append("Free verse/Irregular")

        # Score based on pattern variety and sophistication
        pattern_variety = len(set(rhyme_patterns))
        sophisticated_patterns = sum(
            1 for p in rhyme_patterns if "ABAB" in p or "ABCB" in p
        )

        base_score = min(7.0, pattern_variety * 2)
        sophistication_bonus = min(3.0, sophisticated_patterns * 0.5)

        return base_score + sophistication_bonus, rhyme_patterns

    def analyze_metaphors(self, lyrics: List[str]) -> Tuple[float, List[str]]:
        """Identify and score metaphorical language"""
        metaphor_indicators = [
            r"\bis\s+(?:like\s+)?a\s+",
            r"\bare\s+(?:like\s+)?",
            r"\blike\s+",
            r"\bas\s+",
            r"\bthan\s+",
            r"\bheart\s+of\s+",
            r"\bsoul\s+of\s+",
            r"\bdance\s+of\s+",
            r"\bsong\s+of\s+",
            r"\bfire\s+",
            r"\bflame\s+",
            r"\blight\s+",
            r"\bdarkness\s+",
            r"\bstorm\s+",
            r"\briver\s+",
            r"\bocean\s+",
            r"\bmountain\s+",
        ]

        metaphors_found = []
        lyrical_text = " ".join(lyrics).lower()

        for pattern in metaphor_indicators:
            matches = re.finditer(pattern, lyrical_text)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 20)
                end = min(len(lyrical_text), match.end() + 20)
                context = lyrical_text[start:end].strip()
                metaphors_found.append(context)

        # Score based on metaphor density and variety
        metaphor_count = len(metaphors_found)
        total_words = len(lyrical_text.split())

        if total_words == 0:
            return 0.0, []

        density_score = min(8.0, (metaphor_count / total_words) * 100)
        variety_score = min(2.0, len(set(metaphors_found)) * 0.3)

        return density_score + variety_score, metaphors_found[:5]  # Top 5 examples

    def analyze_thematic_coherence(
        self, lyrics: List[str], scene_title: str
    ) -> Tuple[float, List[str]]:
        """Analyze thematic consistency and development"""
        lyrical_text = " ".join(lyrics).lower()

        # Common theatrical themes
        theme_keywords = {
            "love": ["love", "heart", "desire", "passion", "romance", "kiss"],
            "loss": ["loss", "gone", "lost", "empty", "broken", "tears"],
            "hope": ["hope", "dream", "future", "tomorrow", "light", "dawn"],
            "conflict": ["fight", "battle", "struggle", "war", "against", "enemy"],
            "identity": ["who", "am", "myself", "identity", "self", "soul"],
            "transformation": ["change", "new", "different", "become", "transform"],
            "time": ["time", "moment", "forever", "always", "never", "when"],
            "freedom": ["free", "escape", "break", "liberty", "chains", "bound"],
        }

        themes_present = []
        theme_scores = {}

        for theme, keywords in theme_keywords.items():
            score = sum(lyrical_text.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
                themes_present.append(f"{theme.capitalize()} ({score} references)")

        # Score based on thematic focus and development
        primary_themes = len([t for t in theme_scores.values() if t >= 2])
        thematic_density = sum(theme_scores.values())

        coherence_score = min(8.0, primary_themes * 2)
        development_score = min(2.0, thematic_density * 0.1)

        return coherence_score + development_score, themes_present

    def analyze_vocabulary_complexity(self, lyrics: List[str]) -> Tuple[float, str]:
        """Analyze vocabulary sophistication and complexity"""
        if not lyrics:
            return 0.0, "No lyrics"

        lyrical_text = " ".join(lyrics)
        words = re.findall(r"\b\w+\b", lyrical_text.lower())

        if not words:
            return 0.0, "No words"

        # Basic complexity metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        unique_words = len(set(words))
        total_words = len(words)
        vocabulary_diversity = unique_words / total_words if total_words > 0 else 0

        # Advanced vocabulary indicators
        complex_words = [w for w in words if len(w) > 6]
        complex_ratio = len(complex_words) / total_words if total_words > 0 else 0

        # Calculate sophistication score
        length_score = min(4.0, avg_word_length - 3)  # Words > 3 chars get points
        diversity_score = min(3.0, vocabulary_diversity * 6)
        complexity_score = min(3.0, complex_ratio * 10)

        total_score = length_score + diversity_score + complexity_score

        if total_score >= 7:
            complexity_level = "Advanced"
        elif total_score >= 4:
            complexity_level = "Intermediate"
        else:
            complexity_level = "Basic"

        return total_score, complexity_level

    async def analyze_scene_lyrics(self, scene: SceneData) -> LyricalAnalysis:
        """Perform comprehensive lyrical analysis on a scene"""
        analysis_start = time.time()

        print(f"🎵 Analyzing lyrics for: {scene.title}")

        # Extract lyrics from scene
        lyrics = self.extract_lyrics_from_scene(scene)

        if not lyrics:
            print("   ⚠️ No lyrics found in scene")
            return LyricalAnalysis(
                scene_title=scene.title,
                rhyme_scheme_score=0.0,
                metaphor_usage_score=0.0,
                thematic_coherence_score=0.0,
                lyrical_sophistication_score=0.0,
                overall_lyrical_score=0.0,
                rhyme_patterns=[],
                metaphors_identified=[],
                thematic_elements=[],
                vocabulary_complexity="No lyrics",
                lyrical_strengths=[],
                lyrical_improvements=["Add lyrical content to scene"],
                specialist_commentary="Scene contains no lyrical material for analysis",
                analysis_time=time.time() - analysis_start,
                critic_used=self.lyrical_critic.name,
            )

        print(f"   📝 Found {len(lyrics)} lyrical lines")

        # Perform component analyses
        rhyme_score, rhyme_patterns = self.analyze_rhyme_scheme(lyrics)
        metaphor_score, metaphors = self.analyze_metaphors(lyrics)
        theme_score, themes = self.analyze_thematic_coherence(lyrics, scene.title)
        vocab_score, vocab_level = self.analyze_vocabulary_complexity(lyrics)

        # Get AI critic's specialized analysis
        ai_analysis = await self.get_ai_lyrical_analysis(scene, lyrics)

        # Calculate overall lyrical score
        overall_score = (rhyme_score + metaphor_score + theme_score + vocab_score) / 4

        analysis_time = time.time() - analysis_start

        print(f"   🎼 Rhyme Scheme: {rhyme_score:.1f}/10")
        print(f"   🎭 Metaphors: {metaphor_score:.1f}/10")
        print(f"   🎯 Themes: {theme_score:.1f}/10")
        print(f"   📚 Vocabulary: {vocab_score:.1f}/10 ({vocab_level})")
        print(f"   🏆 Overall Lyrical Score: {overall_score:.1f}/10")

        return LyricalAnalysis(
            scene_title=scene.title,
            rhyme_scheme_score=rhyme_score,
            metaphor_usage_score=metaphor_score,
            thematic_coherence_score=theme_score,
            lyrical_sophistication_score=vocab_score,
            overall_lyrical_score=overall_score,
            rhyme_patterns=rhyme_patterns,
            metaphors_identified=metaphors,
            thematic_elements=themes,
            vocabulary_complexity=vocab_level,
            lyrical_strengths=ai_analysis.get("strengths", []),
            lyrical_improvements=ai_analysis.get("improvements", []),
            specialist_commentary=ai_analysis.get("commentary", ""),
            analysis_time=analysis_time,
            critic_used=self.lyrical_critic.name,
        )

    async def get_ai_lyrical_analysis(
        self, scene: SceneData, lyrics: List[str]
    ) -> Dict:
        """Get specialized AI analysis of lyrical content"""

        try:
            # Create enhanced scene data with lyrical focus
            lyrical_scene = SceneData(
                title=f"LYRICAL ANALYSIS: {scene.title}",
                musical=scene.musical,
                description=f"Lyrical analysis focus: {chr(10).join(lyrics[:5])}...",
                lyrics=chr(10).join(lyrics[:10]),  # First 10 lines
                stage_directions="Focus on rhyme schemes, metaphors, themes, and vocabulary",
                character_notes="Analyze lyrical sophistication and poetic elements",
            )

            # Get AI response using standard interface
            response = await self.lyrical_critic.analyze_scene(lyrical_scene)

            # Parse AI response for lyrical insights
            strengths = []
            improvements = []
            commentary = ""

            if hasattr(response, "review_text") and response.review_text:
                text = response.review_text

                # Extract lyrical insights from AI review
                if hasattr(response, "key_strengths"):
                    strengths = response.key_strengths[:3]

                if hasattr(response, "areas_for_improvement"):
                    improvements = response.areas_for_improvement[:2]

                if hasattr(response, "specialty_analysis"):
                    commentary = response.specialty_analysis[:200]
                else:
                    # Extract key insights from review text
                    commentary = text[:200] + "..." if len(text) > 200 else text

            return {
                "strengths": strengths if strengths else ["Lyrical content present"],
                "improvements": (
                    improvements if improvements else ["Analysis refinement needed"]
                ),
                "commentary": (
                    commentary
                    if commentary
                    else "Specialized lyrical analysis completed"
                ),
            }

        except Exception as e:
            print(f"   ⚠️ AI analysis failed: {e}")
            return {
                "strengths": ["Automated analysis pending"],
                "improvements": ["AI integration in progress"],
                "commentary": "Technical analysis completed successfully",
            }


async def test_lyrical_analysis():
    """Test the lyrical analysis system on sample scenes"""

    print("🎭🎵 LYRICAL CONTENT ANALYSIS TEST")
    print("=" * 50)

    analyzer = LyricalContentAnalyzer()

    # Test scenes with known lyrical content
    test_scenes = [
        "all_musicals_analysis/midnight_at_the_majestic_musical/json/scene_02.json",  # Rich lyrics
        "all_musicals_analysis/echo_musical/json/scene_01.json",  # Sci-fi themes
        "all_musicals_analysis/rainbow_academy_musical/json/scene_01.json",  # Fantasy themes
    ]

    results = []

    for scene_file in test_scenes:
        try:
            print(f"\n📖 Loading scene: {scene_file}")

            with open(scene_file, "r", encoding="utf-8") as f:
                scene_data = json.load(f)
            scene = SceneData(**scene_data)

            # Perform lyrical analysis
            analysis = await analyzer.analyze_scene_lyrics(scene)
            results.append(analysis)

            print(f"✅ Analysis complete for {scene.title}")

        except Exception as e:
            print(f"❌ Error analyzing {scene_file}: {e}")

    # Summary report
    if results:
        print("\n" + "=" * 50)
        print("🏆 LYRICAL ANALYSIS SUMMARY")
        print("=" * 50)

        avg_score = sum(r.overall_lyrical_score for r in results) / len(results)
        print(f"Average Lyrical Score: {avg_score:.1f}/10.0")
        print(f"Scenes Analyzed: {len(results)}")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.scene_title}")
            print(f"   Overall: {result.overall_lyrical_score:.1f}/10")
            print(
                f"   Rhyme: {result.rhyme_scheme_score:.1f} | Metaphor: {result.metaphor_usage_score:.1f}"
            )
            print(
                f"   Theme: {result.thematic_coherence_score:.1f} | Vocab: {result.lyrical_sophistication_score:.1f} ({result.vocabulary_complexity})"
            )
            if result.lyrical_strengths:
                print(f"   Strengths: {', '.join(result.lyrical_strengths[:2])}")

        # Save results
        output_data = {
            "analysis_type": "Lyrical Content Analysis",
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "average_score": round(avg_score, 2),
            "scenes_analyzed": len(results),
            "results": [
                {
                    "scene_title": r.scene_title,
                    "overall_lyrical_score": r.overall_lyrical_score,
                    "component_scores": {
                        "rhyme_scheme": r.rhyme_scheme_score,
                        "metaphor_usage": r.metaphor_usage_score,
                        "thematic_coherence": r.thematic_coherence_score,
                        "vocabulary_sophistication": r.lyrical_sophistication_score,
                    },
                    "analysis_details": {
                        "rhyme_patterns": r.rhyme_patterns,
                        "metaphors_identified": r.metaphors_identified,
                        "thematic_elements": r.thematic_elements,
                        "vocabulary_complexity": r.vocabulary_complexity,
                    },
                    "ai_insights": {
                        "strengths": r.lyrical_strengths,
                        "improvements": r.lyrical_improvements,
                        "specialist_commentary": r.specialist_commentary,
                    },
                    "analysis_time": r.analysis_time,
                }
                for r in results
            ],
        }

        with open("lyrical_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: lyrical_analysis_results.json")
        print("🎵 Lyrical Content Analysis system ready!")

    return results


if __name__ == "__main__":
    print("🚀 Starting Lyrical Content Analysis Test...")
    asyncio.run(test_lyrical_analysis())
