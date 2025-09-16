"""
Transcript processing pipeline for analyzing speeches, hearings, and video content.
"""
import asyncio
import whisper
import openai
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
import spacy
from transformers import pipeline
import structlog
from config.settings import settings

logger = structlog.get_logger()


class TranscriptProcessor:
    """Main transcript processing class."""

    def __init__(self):
        self.whisper_model = None
        self.nlp = None
        self.sentiment_analyzer = None
        self.summarizer = None
        self._load_models()

    def _load_models(self):
        """Load NLP models."""
        try:
            # Load spaCy model for NLP
            self.nlp = spacy.load(settings.SPACY_MODEL)

            # Load Whisper for transcription
            self.whisper_model = whisper.load_model("base")

            # Load transformers models
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # CPU
            )

            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # CPU
            )

            logger.info("NLP models loaded successfully")

        except Exception as e:
            logger.error("Failed to load NLP models", error=str(e))

    async def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio file to text using Whisper."""
        if not self.whisper_model:
            return {"error": "Whisper model not loaded"}

        try:
            result = self.whisper_model.transcribe(audio_path)

            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "transcribed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Transcription failed", audio_path=audio_path, error=str(e))
            return {"error": str(e)}

    async def process_transcript(self, transcript_text: str,
                               speaker_info: Dict = None) -> Dict:
        """Process transcript text for analysis."""
        if not self.nlp:
            return {"error": "NLP model not loaded"}

        analysis = {
            "original_text": transcript_text,
            "processed_at": datetime.now().isoformat(),
            "speaker_info": speaker_info or {},
            "word_count": len(transcript_text.split()),
            "char_count": len(transcript_text)
        }

        try:
            # Clean and preprocess text
            cleaned_text = self._clean_transcript_text(transcript_text)
            analysis["cleaned_text"] = cleaned_text

            # Process with spaCy
            doc = self.nlp(cleaned_text)

            # Extract entities
            analysis["entities"] = self._extract_entities(doc)

            # Extract key phrases
            analysis["key_phrases"] = self._extract_key_phrases(doc)

            # Sentiment analysis
            analysis["sentiment"] = await self._analyze_sentiment(cleaned_text)

            # Topic extraction
            analysis["topics"] = self._extract_topics(doc)

            # Policy positions detection
            analysis["policy_positions"] = self._detect_policy_positions(doc)

            # Generate summary
            analysis["summary"] = await self._generate_summary(cleaned_text)

            # Quote extraction
            analysis["notable_quotes"] = self._extract_quotes(cleaned_text)

        except Exception as e:
            logger.error("Transcript processing failed", error=str(e))
            analysis["processing_error"] = str(e)

        return analysis

    def _clean_transcript_text(self, text: str) -> str:
        """Clean transcript text for analysis."""
        # Remove timestamps
        text = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', text)

        # Remove speaker labels (e.g., "SENATOR SMITH:")
        text = re.sub(r'^[A-Z\s]+:', '', text, flags=re.MULTILINE)

        # Remove filler words and sounds
        fillers = ['um', 'uh', 'er', 'ah', '(inaudible)', '(crosstalk)', '(laughter)']
        for filler in fillers:
            text = re.sub(re.escape(filler), '', text, flags=re.IGNORECASE)

        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from spaCy doc."""
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "money": [],
            "laws": [],
            "events": []
        }

        for ent in doc.ents:
            text = ent.text.strip()
            if len(text) < 2:
                continue

            if ent.label_ in ["PERSON"]:
                entities["persons"].append(text)
            elif ent.label_ in ["ORG"]:
                entities["organizations"].append(text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].append(text)
            elif ent.label_ in ["DATE", "TIME"]:
                entities["dates"].append(text)
            elif ent.label_ in ["MONEY"]:
                entities["money"].append(text)
            elif ent.label_ in ["LAW"]:
                entities["laws"].append(text)
            elif ent.label_ in ["EVENT"]:
                entities["events"].append(text)

        # Remove duplicates and sort
        for category in entities:
            entities[category] = sorted(list(set(entities[category])))

        return entities

    def _extract_key_phrases(self, doc) -> List[Dict]:
        """Extract key phrases using noun chunks and custom patterns."""
        key_phrases = []

        # Extract noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Multi-word phrases
                key_phrases.append({
                    "phrase": chunk.text.strip(),
                    "type": "noun_chunk",
                    "pos": chunk.start
                })

        # Extract verb phrases (custom pattern)
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                # Get verb phrase
                phrase_tokens = [token]
                for child in token.children:
                    if child.dep_ in ["dobj", "prep", "advmod"]:
                        phrase_tokens.append(child)

                if len(phrase_tokens) > 1:
                    phrase_text = " ".join([t.text for t in phrase_tokens])
                    key_phrases.append({
                        "phrase": phrase_text.strip(),
                        "type": "verb_phrase",
                        "pos": token.i
                    })

        return sorted(key_phrases, key=lambda x: x["pos"])

    async def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text."""
        if not self.sentiment_analyzer or len(text.strip()) == 0:
            return {"error": "Cannot analyze sentiment"}

        try:
            # Split text into chunks for analysis
            chunks = self._split_text_for_analysis(text, max_length=512)
            sentiments = []

            for chunk in chunks:
                result = self.sentiment_analyzer(chunk)[0]
                sentiments.append({
                    "label": result["label"],
                    "score": result["score"]
                })

            # Aggregate results
            if sentiments:
                avg_positive = sum(1 for s in sentiments if s["label"] == "POSITIVE") / len(sentiments)
                avg_negative = sum(1 for s in sentiments if s["label"] == "NEGATIVE") / len(sentiments)
                avg_neutral = sum(1 for s in sentiments if s["label"] == "NEUTRAL") / len(sentiments)

                overall_sentiment = "NEUTRAL"
                if avg_positive > avg_negative and avg_positive > avg_neutral:
                    overall_sentiment = "POSITIVE"
                elif avg_negative > avg_positive and avg_negative > avg_neutral:
                    overall_sentiment = "NEGATIVE"

                return {
                    "overall_sentiment": overall_sentiment,
                    "positive_ratio": avg_positive,
                    "negative_ratio": avg_negative,
                    "neutral_ratio": avg_neutral,
                    "chunk_sentiments": sentiments
                }

        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))

        return {"error": "Sentiment analysis failed"}

    def _extract_topics(self, doc) -> List[str]:
        """Extract main topics from the document."""
        # Use named entities and key phrases to infer topics
        topics = set()

        # Government/Political topics
        political_terms = [
            "healthcare", "economy", "education", "defense", "immigration",
            "environment", "infrastructure", "taxes", "budget", "trade",
            "foreign policy", "national security", "civil rights", "gun",
            "abortion", "climate", "energy", "medicare", "social security"
        ]

        text_lower = doc.text.lower()
        for term in political_terms:
            if term in text_lower:
                topics.add(term.title())

        # Extract topics from entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "EVENT", "LAW"]:
                if len(ent.text.split()) <= 3:  # Keep it concise
                    topics.add(ent.text)

        return sorted(list(topics))

    def _detect_policy_positions(self, doc) -> List[Dict]:
        """Detect policy positions and stances."""
        positions = []

        # Define patterns for stance detection
        support_patterns = [
            "support", "back", "endorse", "favor", "advocate", "champion",
            "believe in", "stand behind", "promote", "defend"
        ]

        oppose_patterns = [
            "oppose", "against", "reject", "condemn", "disagree", "resist",
            "fight", "block", "prevent", "stop"
        ]

        # Look for stance indicators
        for sent in doc.sents:
            sent_text = sent.text.lower()

            stance = None
            if any(pattern in sent_text for pattern in support_patterns):
                stance = "SUPPORT"
            elif any(pattern in sent_text for pattern in oppose_patterns):
                stance = "OPPOSE"

            if stance:
                # Try to identify the topic being discussed
                topic_entities = [ent.text for ent in sent.ents
                                if ent.label_ in ["ORG", "EVENT", "LAW", "PRODUCT"]]

                if topic_entities:
                    positions.append({
                        "stance": stance,
                        "topic": topic_entities[0],
                        "sentence": sent.text.strip(),
                        "confidence": 0.7  # Basic confidence score
                    })

        return positions

    async def _generate_summary(self, text: str) -> str:
        """Generate summary of the transcript."""
        if not self.summarizer or len(text.strip()) < 100:
            return "Text too short for summarization"

        try:
            # Split into manageable chunks
            chunks = self._split_text_for_analysis(text, max_length=1024)
            summaries = []

            for chunk in chunks:
                if len(chunk.strip()) < 100:
                    continue

                summary = self.summarizer(
                    chunk,
                    max_length=150,
                    min_length=30,
                    do_sample=False
                )[0]["summary_text"]

                summaries.append(summary)

            # Combine summaries
            if len(summaries) > 1:
                combined = " ".join(summaries)
                # Summarize the combined summaries if too long
                if len(combined.split()) > 200:
                    final_summary = self.summarizer(
                        combined,
                        max_length=200,
                        min_length=50,
                        do_sample=False
                    )[0]["summary_text"]
                    return final_summary
                return combined
            elif summaries:
                return summaries[0]

        except Exception as e:
            logger.error("Summarization failed", error=str(e))

        return "Summary generation failed"

    def _extract_quotes(self, text: str) -> List[Dict]:
        """Extract notable quotes from the transcript."""
        quotes = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 300:
                continue

            # Score sentences for "quotability"
            score = 0

            # Policy keywords boost score
            policy_keywords = [
                "believe", "think", "support", "oppose", "will", "must",
                "should", "need to", "have to", "important", "critical"
            ]

            for keyword in policy_keywords:
                if keyword in sentence.lower():
                    score += 1

            # Emotional language boosts score
            emotional_words = [
                "strongly", "deeply", "absolutely", "completely", "totally",
                "critical", "urgent", "essential", "vital", "crucial"
            ]

            for word in emotional_words:
                if word in sentence.lower():
                    score += 1

            # First person statements boost score
            if re.search(r'\b(I|we)\b', sentence, re.IGNORECASE):
                score += 1

            # Future tense boosts score
            if re.search(r'\b(will|going to|plan to)\b', sentence, re.IGNORECASE):
                score += 1

            if score >= 2:  # Threshold for notable quotes
                quotes.append({
                    "text": sentence,
                    "score": score,
                    "length": len(sentence)
                })

        # Sort by score and return top quotes
        quotes.sort(key=lambda x: x["score"], reverse=True)
        return quotes[:10]  # Top 10 quotes

    def _split_text_for_analysis(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks for model processing."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def process_speaker_identification(self, transcript_segments: List[Dict]) -> Dict:
        """Identify and analyze different speakers in a transcript."""
        speaker_analysis = {
            "speakers": {},
            "speaking_time": {},
            "interaction_patterns": []
        }

        for segment in transcript_segments:
            speaker = segment.get("speaker", "Unknown")
            text = segment.get("text", "")
            duration = segment.get("duration", 0)

            # Initialize speaker data
            if speaker not in speaker_analysis["speakers"]:
                speaker_analysis["speakers"][speaker] = {
                    "total_words": 0,
                    "segments": 0,
                    "topics": set(),
                    "sentiment_scores": []
                }
                speaker_analysis["speaking_time"][speaker] = 0

            # Update speaker stats
            speaker_data = speaker_analysis["speakers"][speaker]
            speaker_data["total_words"] += len(text.split())
            speaker_data["segments"] += 1
            speaker_analysis["speaking_time"][speaker] += duration

            # Analyze this segment
            if text.strip():
                segment_analysis = await self.process_transcript(text)

                # Add topics
                if "topics" in segment_analysis:
                    speaker_data["topics"].update(segment_analysis["topics"])

                # Add sentiment
                if "sentiment" in segment_analysis:
                    if "overall_sentiment" in segment_analysis["sentiment"]:
                        speaker_data["sentiment_scores"].append(
                            segment_analysis["sentiment"]["overall_sentiment"]
                        )

        # Convert sets to lists for JSON serialization
        for speaker in speaker_analysis["speakers"]:
            speaker_analysis["speakers"][speaker]["topics"] = \
                list(speaker_analysis["speakers"][speaker]["topics"])

        return speaker_analysis