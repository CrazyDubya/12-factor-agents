#!/usr/bin/env python3
"""
Theater Critics Multi-Agent System
Uses Ollama models to provide rotating ensemble of theater critics for musical scene reviews
"""

import json
import random
import asyncio
import httpx
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class CriticType(Enum):
    PRIMARY = "primary"
    ACADEMIC = "academic"
    POPULAR = "popular"
    EXPERIMENTAL = "experimental"
    COMMERCIAL = "commercial"
    EMOTION = "emotion"

@dataclass
class SceneData:
    title: str
    musical: str
    description: str
    lyrics: Optional[str] = None
    stage_directions: Optional[str] = None
    character_notes: Optional[str] = None

@dataclass
class ReviewScore:
    overall: float  # 1-10
    musical_composition: float
    performance_quality: float
    production_elements: float
    narrative_integration: float
    audience_engagement: float
    specialty_score: float  # Critic's specialty focus

@dataclass
class CriticReview:
    critic_name: str
    critic_type: CriticType
    model_used: str
    review_text: str
    scores: ReviewScore
    key_strengths: List[str]
    areas_for_improvement: List[str]
    specialty_analysis: str

class TheaterCritic:
    """Base class for theater critics using different Ollama models"""
    
    def __init__(self, name: str, critic_type: CriticType, model: str, specialty: str):
        self.name = name
        self.critic_type = critic_type
        self.model = model
        self.specialty = specialty
        self.ollama_url = "http://localhost:11434/api/generate"
    
    async def analyze_scene(self, scene: SceneData) -> CriticReview:
        """Analyze a musical theater scene from this critic's perspective"""
        prompt = self._build_analysis_prompt(scene)
        
        try:
            response = await self._query_ollama(prompt)
            return self._parse_response(response, scene)
        except Exception as e:
            return self._create_error_review(str(e))
    
    def _build_analysis_prompt(self, scene: SceneData) -> str:
        """Build specialized prompt for this critic type"""
        base_prompt = f"""
You are {self.name}, a renowned theater critic specializing in {self.specialty}.

Analyze this musical theater scene:

**Musical:** {scene.musical}
**Scene:** {scene.title}
**Description:** {scene.description}
"""
        
        if scene.lyrics:
            base_prompt += f"\n**Lyrics:**\n{scene.lyrics}\n"
        if scene.stage_directions:
            base_prompt += f"\n**Stage Directions:**\n{scene.stage_directions}\n"
        if scene.character_notes:
            base_prompt += f"\n**Character Notes:**\n{scene.character_notes}\n"
        
        specialty_prompt = self._get_specialty_prompt()
        
        scoring_prompt = """
Provide your analysis in this JSON format:
{
    "review_text": "Your comprehensive review (2-3 paragraphs)",
    "scores": {
        "overall": 7.5,
        "musical_composition": 8.0,
        "performance_quality": 7.0,
        "production_elements": 8.5,
        "narrative_integration": 6.5,
        "audience_engagement": 7.8,
        "specialty_score": 8.2
    },
    "key_strengths": ["strength 1", "strength 2", "strength 3"],
    "areas_for_improvement": ["improvement 1", "improvement 2"],
    "specialty_analysis": "Your focused analysis on your specialty area"
}

All scores should be between 1.0 and 10.0. Be critical but fair.
"""
        
        return base_prompt + specialty_prompt + scoring_prompt
    
    def _get_specialty_prompt(self) -> str:
        """Get specialized analysis prompt based on critic type"""
        prompts = {
            CriticType.PRIMARY: """
As the lead critic, provide a comprehensive analysis covering all aspects of the scene. 
Focus on overall artistic merit, technical execution, and cultural significance.
""",
            CriticType.ACADEMIC: """
Focus on musical theory, composition techniques, historical context, and artistic innovation.
Analyze harmony, melody, lyrical sophistication, and connections to musical theater traditions.
""",
            CriticType.POPULAR: """
Evaluate audience appeal, entertainment value, and mainstream accessibility.
Consider singability, memorability, emotional connection, and commercial potential.
""",
            CriticType.EXPERIMENTAL: """
Assess artistic risk-taking, innovation, and avant-garde elements.
Look for experimental staging, unconventional musical structures, and boundary-pushing concepts.
""",
            CriticType.COMMERCIAL: """
Analyze production value, marketability, and mainstream appeal.
Consider budget implications, touring potential, and broad audience accessibility.
""",
            CriticType.EMOTION: """
Focus on emotional impact, character development, and storytelling effectiveness.
Evaluate how well the scene conveys emotion and advances character arcs.
"""
        }
        return prompts.get(self.critic_type, prompts[CriticType.PRIMARY])
    
    async def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()["response"]
                print(f"✅ {self.name} analysis complete")
                return result
        except httpx.TimeoutException:
            raise Exception(f"Timeout waiting for {self.model}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to query {self.model}: {str(e)}")
    
    def _parse_response(self, response: str, scene: SceneData) -> CriticReview:
        """Parse Ollama response into CriticReview object"""
        try:
            # Try to extract JSON from response if it contains other text
            response = response.strip()
            
            # Look for JSON block in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                # If no JSON found, create fallback review
                return self._create_fallback_review(response)
            
            scores = ReviewScore(
                overall=data["scores"]["overall"],
                musical_composition=data["scores"]["musical_composition"],
                performance_quality=data["scores"]["performance_quality"],
                production_elements=data["scores"]["production_elements"],
                narrative_integration=data["scores"]["narrative_integration"],
                audience_engagement=data["scores"]["audience_engagement"],
                specialty_score=data["scores"]["specialty_score"]
            )
            
            return CriticReview(
                critic_name=self.name,
                critic_type=self.critic_type,
                model_used=self.model,
                review_text=data["review_text"],
                scores=scores,
                key_strengths=data["key_strengths"],
                areas_for_improvement=data["areas_for_improvement"],
                specialty_analysis=data["specialty_analysis"]
            )
        except (json.JSONDecodeError, KeyError) as e:
            return self._create_fallback_review(response)
    
    def _create_fallback_review(self, response: str) -> CriticReview:
        """Create fallback review from non-JSON response"""
        # Extract basic analysis from text response
        review_text = response[:500] + "..." if len(response) > 500 else response
        
        # Assign moderate scores as fallback
        scores = ReviewScore(
            overall=7.0,
            musical_composition=7.0,
            performance_quality=7.0,
            production_elements=7.0,
            narrative_integration=7.0,
            audience_engagement=7.0,
            specialty_score=7.5
        )
        
        return CriticReview(
            critic_name=self.name,
            critic_type=self.critic_type,
            model_used=self.model,
            review_text=review_text,
            scores=scores,
            key_strengths=["Analysis provided in narrative form"],
            areas_for_improvement=["Structured scoring format needed"],
            specialty_analysis=f"Free-form analysis from {self.specialty} perspective"
        )
    
    def _create_error_review(self, error_msg: str) -> CriticReview:
        """Create error review when analysis fails"""
        return CriticReview(
            critic_name=self.name,
            critic_type=self.critic_type,
            model_used=self.model,
            review_text=f"Analysis failed: {error_msg}",
            scores=ReviewScore(5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0),
            key_strengths=["Unable to analyze"],
            areas_for_improvement=["System error occurred"],
            specialty_analysis="Analysis unavailable due to error"
        )

class CriticEnsemble:
    """Manages the rotating ensemble of theater critics"""
    
    def __init__(self):
        self.critics = self._initialize_critics()
        self.primary_critic = self.critics[CriticType.PRIMARY]
    
    def _initialize_critics(self) -> Dict[CriticType, TheaterCritic]:
        """Initialize all critic agents with their specialized models"""
        return {
            CriticType.PRIMARY: TheaterCritic(
                "Eleanor Hartwell", CriticType.PRIMARY, "gemma2:9b", 
                "comprehensive theatrical analysis"
            ),
            CriticType.ACADEMIC: TheaterCritic(
                "Dr. Marcus Steinberg", CriticType.ACADEMIC, "qwen2.5:3b",
                "musical theory and historical context"
            ),
            CriticType.POPULAR: TheaterCritic(
                "Casey Rodriguez", CriticType.POPULAR, "llama3.2:3b",
                "audience appeal and entertainment value"
            ),
            CriticType.EXPERIMENTAL: TheaterCritic(
                "Zara Blackthorne", CriticType.EXPERIMENTAL, "theater-long-context:latest",
                "artistic innovation and experimental theater"
            ),
            CriticType.COMMERCIAL: TheaterCritic(
                "Robert Sterling", CriticType.COMMERCIAL, "llama3:8b",
                "production value and commercial viability"
            ),
            CriticType.EMOTION: TheaterCritic(
                "Luna Chen", CriticType.EMOTION, "gemma:7b",
                "emotional impact and character development"
            )
        }
    
    def select_rotating_critics(self, count: int = 3) -> List[TheaterCritic]:
        """Select random subset of secondary critics for this review"""
        secondary_critics = [
            critic for critic_type, critic in self.critics.items()
            if critic_type != CriticType.PRIMARY
        ]
        return random.sample(secondary_critics, min(count, len(secondary_critics)))
    
    async def review_scene(self, scene: SceneData, num_rotating_critics: int = 3) -> List[CriticReview]:
        """Get reviews from primary critic and rotating ensemble"""
        print(f"🎭 Analyzing scene: {scene.title} from {scene.musical}")
        print(f"📝 Primary critic: {self.primary_critic.name}")
        
        # Always include primary critic
        reviews = []
        
        # Get rotating critics
        rotating_critics = self.select_rotating_critics(num_rotating_critics)
        print(f"🔄 Rotating critics: {', '.join(c.name for c in rotating_critics)}")
        
        # Run all analyses concurrently
        all_critics = [self.primary_critic] + rotating_critics
        tasks = [critic.analyze_scene(scene) for critic in all_critics]
        
        print("⏳ Running critic analyses...")
        reviews = await asyncio.gather(*tasks)
        
        return reviews

class ConsensusAnalyzer:
    """Analyzes consensus and disagreements between critics"""
    
    @staticmethod
    def calculate_consensus(reviews: List[CriticReview]) -> Dict:
        """Calculate consensus scores and identify agreements/disagreements"""
        if not reviews:
            return {}
        
        # Calculate average scores
        avg_scores = {}
        score_fields = ['overall', 'musical_composition', 'performance_quality', 
                       'production_elements', 'narrative_integration', 'audience_engagement']
        
        for field in score_fields:
            scores = [getattr(review.scores, field) for review in reviews]
            avg_scores[field] = sum(scores) / len(scores)
        
        # Find score variations
        score_variations = {}
        for field in score_fields:
            scores = [getattr(review.scores, field) for review in reviews]
            score_variations[field] = max(scores) - min(scores)
        
        # Identify consensus level
        overall_variation = score_variations['overall']
        if overall_variation <= 1.0:
            consensus_level = "Strong Agreement"
        elif overall_variation <= 2.0:
            consensus_level = "Moderate Agreement" 
        elif overall_variation <= 3.0:
            consensus_level = "Some Disagreement"
        else:
            consensus_level = "Significant Disagreement"
        
        # Find common themes in strengths and improvements
        all_strengths = []
        all_improvements = []
        for review in reviews:
            all_strengths.extend(review.key_strengths)
            all_improvements.extend(review.areas_for_improvement)
        
        return {
            "consensus_level": consensus_level,
            "average_scores": avg_scores,
            "score_variations": score_variations,
            "common_strengths": list(set(all_strengths)),
            "common_improvements": list(set(all_improvements)),
            "critic_count": len(reviews)
        }

def print_review_summary(reviews: List[CriticReview], consensus: Dict):
    """Print formatted review summary"""
    print("\n" + "="*80)
    print("🎭 THEATER CRITICS ENSEMBLE REVIEW")
    print("="*80)
    
    # Consensus overview
    print(f"\n📊 CONSENSUS: {consensus['consensus_level']}")
    print(f"Overall Score: {consensus['average_scores']['overall']:.1f}/10.0")
    print(f"Critics Participating: {consensus['critic_count']}")
    
    # Individual reviews
    print("\n" + "-"*60)
    print("INDIVIDUAL CRITIC REVIEWS")
    print("-"*60)
    
    for review in reviews:
        print(f"\n🎬 {review.critic_name} ({review.critic_type.value.title()})")
        print(f"Model: {review.model_used}")
        print(f"Overall Score: {review.scores.overall}/10.0")
        print(f"Specialty Score: {review.scores.specialty_score}/10.0")
        print(f"\nReview: {review.review_text}")
        print(f"\nStrengths: {', '.join(review.key_strengths)}")
        print(f"Improvements: {', '.join(review.areas_for_improvement)}")
        print(f"\nSpecialty Analysis: {review.specialty_analysis}")
        print("-" * 40)
    
    # Detailed scores
    print(f"\n📈 DETAILED CONSENSUS SCORES")
    print("-"*40)
    for category, score in consensus['average_scores'].items():
        variation = consensus['score_variations'][category]
        print(f"{category.replace('_', ' ').title()}: {score:.1f}/10.0 (±{variation:.1f})")

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create sample scene
        scene = SceneData(
            title="Defying Gravity",
            musical="Wicked",
            description="Elphaba's climactic moment of self-realization and defiance at the end of Act I",
            lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game

Too late for second-guessing
Too late to go back to sleep
It's time to trust my instincts
Close my eyes and leap!""",
            stage_directions="Elphaba rises above the stage on a mechanical lift, cape billowing, as the ensemble looks up in awe and fear",
            character_notes="Elphaba transforms from outcast to empowered individual, accepting her differences as strengths"
        )
        
        # Initialize critic ensemble
        ensemble = CriticEnsemble()
        
        # Get reviews
        reviews = await ensemble.review_scene(scene)
        
        # Calculate consensus
        consensus = ConsensusAnalyzer.calculate_consensus(reviews)
        
        # Print results
        print_review_summary(reviews, consensus)

    # Run the example
    asyncio.run(main())