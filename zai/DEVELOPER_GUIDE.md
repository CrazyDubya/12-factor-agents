# V2 Context Selection System - Developer Guide

**Date**: October 1, 2025
**Audience**: Developers integrating or extending the V2 Context Selection System

---

## Architecture Overview

The V2 Context Selection System is built with a modular architecture that separates concerns and enables easy extension and customization.

```
v2_context_selector/
├── core/                    # Core functionality
│   ├── models.py           # Data models (TextSegment, SelectionResult)
│   ├── selector.py         # Main selection logic
│   ├── embedding_manager.py # Embedding generation and caching
│   └── evaluator.py        # Evaluation and metrics
├── config/                  # Configuration management
│   └── settings.py         # Configuration classes and presets
├── utils/                   # Utility modules
│   ├── tfidf.py           # TF-IDF processing
│   └── validation.py      # Input validation
└── features/               # Extensible feature modules
    ├── temporal_ranking.py # Time-sensitive query processing
    ├── query_expansion.py  # Query enhancement
    └── diversity_scoring.py # Content diversity algorithms
```

## Core Components

### 1. ContextSelector (Main API)

The primary interface for document selection. Provides a simple API while handling complex internal logic.

```python
from v2_context_selector import ContextSelector, Config

# Basic usage
selector = ContextSelector()
result = selector.select(query, segments, budget=1000)

# Advanced usage with custom config
config = Config(enable_temporal_ranking=True)
selector = ContextSelector(config)
```

**Key Methods:**
- `select(query, segments, budget)`: Main selection method
- `preload_documents(segments)`: Pre-cache embeddings for performance
- `get_performance_stats()`: Performance monitoring
- `update_config(**kwargs)`: Runtime configuration updates

### 2. EmbeddingManager

Handles text embedding generation with intelligent caching and fallback mechanisms.

```python
from v2_context_selector.core import EmbeddingManager

manager = EmbeddingManager(
    model_name="paraphrase-MiniLM-L3-v2",
    cache_size=1000
)

# Generate embeddings
embedding = manager.encode("Some text")
batch_embeddings = manager.encode_batch(["text1", "text2"])
```

**Features:**
- Automatic model loading with fallback to mock embeddings
- LRU caching with configurable size
- Batch processing for efficiency
- Performance tracking and statistics

### 3. TFIDFProcessor

Computes Term Frequency-Inverse Document Frequency scores to complement semantic similarity.

```python
from v2_context_selector.utils import TFIDFProcessor

processor = TFIDFProcessor()
processor.precompute(segments)

# Compute TF-IDF score for query
score = processor.compute_score("query text", segment_index)
```

**Capabilities:**
- Efficient precomputation for document collections
- Punctuation-aware text processing
- Statistical analysis and reporting

### 4. Configuration System

Flexible configuration management with presets and runtime updates.

```python
from v2_context_selector.config import Config, fast_config, accurate_config

# Use preset
config = fast_config()

# Custom configuration
config = Config(
    embedding_model="all-MiniLM-L6-v2",
    enable_temporal_ranking=True,
    semantic_weight=0.8,
    tfidf_weight=0.2
)

# Runtime updates
selector.update_config(cache_size=2000)
```

## Integration Patterns

### Pattern 1: Basic Document Q&A

```python
from v2_context_selector import ContextSelector, TextSegment

class DocumentQA:
    def __init__(self):
        self.selector = ContextSelector()
        self.documents = []
        self.segments = []

    def add_document(self, text, doc_id):
        """Add a document and split into segments."""
        # Split document into chunks
        chunks = self._chunk_document(text)

        # Create segments
        for i, chunk in enumerate(chunks):
            segment = TextSegment(
                id=f"{doc_id}_{i}",
                text=chunk,
                document_id=doc_id,
                position=i
            )
            self.segments.append(segment)

        # Preload for performance
        self.selector.preload_documents(self.segments)

    def query(self, question, max_results=3):
        """Answer a question using document content."""
        result = self.selector.select(
            question,
            self.segments,
            budget=1000
        )

        return result.selected_segments[:max_results]

    def _chunk_document(self, text, chunk_size=150):
        """Split document into chunks."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks
```

### Pattern 2: Customer Service Bot

```python
from v2_context_selector import ContextSelector, balanced_config
from v2_context_selector.core import TextSegment

class CustomerServiceBot:
    def __init__(self):
        self.selector = ContextSelector(balanced_config())
        self.knowledge_base = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load FAQs and product manuals."""
        faqs = self._load_faqs()
        manuals = self._load_manuals()

        for source, content in faqs + manuals:
            segments = self._create_segments(content, source)
            self.knowledge_base.extend(segments)

        self.selector.preload_documents(self.knowledge_base)

    def handle_query(self, query):
        """Process customer query."""
        result = self.selector.select(query, self.knowledge_base, budget=800)

        if not result.selected_segments:
            return "I'm sorry, I couldn't find relevant information."

        # Format response
        responses = []
        for segment in result.selected_segments[:2]:
            response = f"From {segment.document_id}: {segment.text}"
            responses.append(response)

        return "\n\n".join(responses)

    def get_performance_stats(self):
        """Monitor bot performance."""
        return self.selector.get_performance_stats()
```

### Pattern 3: Research Assistant

```python
from v2_context_selector import ContextSelector, accurate_config
from v2_context_selector.core import TextSegment

class ResearchAssistant:
    def __init__(self):
        self.selector = ContextSelector(accurate_config())
        self.papers = []

    def add_paper(self, title, content, paper_id):
        """Add research paper to collection."""
        segments = self._create_segments(content, paper_id, title)
        self.papers.extend(segments)

    def find_relevant_papers(self, research_question, max_papers=5):
        """Find papers relevant to research question."""
        self.selector.preload_documents(self.papers)

        result = self.selector.select(
            research_question,
            self.papers,
            budget=1500
        )

        # Group by paper
        paper_results = {}
        for segment in result.selected_segments:
            paper_id = segment.document_id
            if paper_id not in paper_results:
                paper_results[paper_id] = []
            paper_results[paper_id].append(segment)

        # Return top papers
        top_papers = list(paper_results.items())[:max_papers]

        return {
            'papers': [
                {
                    'id': paper_id,
                    'segments': segments,
                    'relevance_score': len(segments)
                }
                for paper_id, segments in top_papers
            ],
            'confidence': result.confidence_score,
            'method': result.method
        }
```

## Extension Points

### 1. Custom Scoring Functions

Add custom scoring algorithms by extending the selector:

```python
class CustomContextSelector(ContextSelector):
    def __init__(self, config=None):
        super().__init__(config)
        self.custom_scorers = []

    def add_custom_scorer(self, scorer_func):
        """Add a custom scoring function."""
        self.custom_scorers.append(scorer_func)

    def _compute_custom_scores(self, segments, query):
        """Compute custom scores."""
        scores = np.zeros(len(segments))

        for scorer in self.custom_scorers:
            custom_scores = scorer(segments, query)
            scores += custom_scores

        return scores

# Usage
def recency_scorer(segments, query):
    """Score based on recency (newer content gets higher scores)."""
    scores = np.zeros(len(segments))

    for i, segment in enumerate(segments):
        if segment.timestamp:
            # Parse timestamp and compute recency score
            days_old = (datetime.now() - parse_timestamp(segment.timestamp)).days
            scores[i] = 1.0 / (1.0 + days_old / 30.0)  # Decay over 30 days

    return scores

selector = CustomContextSelector()
selector.add_custom_scorer(recency_scorer)
```

### 2. Custom Feature Modules

Create new feature modules in the `features/` directory:

```python
# features/custom_feature.py
class CustomFeature:
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('enable_custom_feature', False)

    def should_activate(self, query_analysis):
        """Determine if feature should be activated for this query."""
        return self.enabled and self._needs_feature(query_analysis)

    def process(self, query, segments, query_analysis):
        """Apply custom feature processing."""
        if not self.should_activate(query_analysis):
            return None

        # Custom processing logic
        return self._apply_feature(query, segments, query_analysis)

    def _needs_feature(self, query_analysis):
        """Internal logic for feature activation."""
        return query_analysis.complexity_score > 0.5

    def _apply_feature(self, query, segments, query_analysis):
        """Apply the custom feature."""
        # Implementation specific to the feature
        pass
```

### 3. Custom Embedding Models

Support different embedding backends:

```python
from v2_context_selector.core import EmbeddingManager

class CustomEmbeddingManager(EmbeddingManager):
    def __init__(self, model_backend, **kwargs):
        super().__init__(**kwargs)
        self.model_backend = model_backend

    def _load_model(self):
        """Load custom embedding model."""
        if self.model_backend == 'openai':
            self._load_openai_model()
        elif self.model_backend == 'huggingface':
            self._load_huggingface_model()
        else:
            super()._load_model()

    def _load_openai_model(self):
        """Load OpenAI embedding model."""
        import openai
        self._model = "text-embedding-ada-002"
        self._embedding_dimension = 1536

    def encode(self, text):
        """Encode using custom backend."""
        if self.model_backend == 'openai':
            return self._encode_openai(text)
        else:
            return super().encode(text)
```

## Performance Optimization

### 1. Caching Strategies

```python
# Configure large cache for frequently accessed documents
config = Config(cache_size=5000)

# Preload documents at startup
selector = ContextSelector(config)
selector.preload_documents(documents)

# Monitor cache performance
stats = selector.get_performance_stats()
print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.1%}")
```

### 2. Feature Flag Optimization

```python
# Disable expensive features for speed
fast_config = Config(
    enable_temporal_ranking=False,
    enable_semantic_diversity=False,
    enable_topic_clustering=False,
    max_segments_per_query=50
)

# Enable features for accuracy
accurate_config = Config(
    enable_temporal_ranking=True,
    enable_semantic_diversity=True,
    enable_topic_clustering=True,
    max_segments_per_query=200
)
```

### 3. Batch Processing

```python
def batch_queries(selector, queries, segments):
    """Process multiple queries efficiently."""
    results = []

    # Preload all segments once
    selector.preload_documents(segments)

    # Process queries
    for query in queries:
        result = selector.select(query, segments, budget=1000)
        results.append(result)

    return results
```

## Testing Strategy

### 1. Unit Testing

```python
import pytest
from v2_context_selector import ContextSelector, TextSegment

class TestContextSelector:
    def setup_method(self):
        self.selector = ContextSelector()
        self.segments = [
            TextSegment("seg1", "Whales are large mammals.", "doc1", 0),
            TextSegment("seg2", "Ships sail on the ocean.", "doc1", 1)
        ]

    def test_basic_selection(self):
        result = self.selector.select("What are whales?", self.segments, budget=500)
        assert len(result.selected_segments) > 0
        assert result.execution_time_ms < 100

    def test_empty_query(self):
        with pytest.raises(ValueError):
            self.selector.select("", self.segments, budget=500)
```

### 2. Integration Testing

```python
def test_real_world_performance():
    """Test with real documents."""
    # Load real documents
    documents = load_test_documents()

    # Create segments
    segments = create_segments(documents)

    # Test with realistic queries
    queries = [
        "What is artificial intelligence?",
        "How do neural networks work?",
        "Explain machine learning algorithms"
    ]

    selector = ContextSelector()
    results = []

    for query in queries:
        result = selector.select(query, segments, budget=1000)
        results.append(result)
        assert result.execution_time_ms < 200

    # Evaluate overall performance
    avg_time = sum(r.execution_time_ms for r in results) / len(results)
    assert avg_time < 100
```

### 3. Performance Testing

```python
import time
import statistics

def benchmark_performance():
    """Benchmark system performance."""
    selector = ContextSelector()
    documents = load_large_dataset()
    segments = create_segments(documents)

    queries = generate_test_queries(100)

    times = []
    for query in queries:
        start = time.time()
        result = selector.select(query, segments, budget=1000)
        end = time.time()
        times.append((end - start) * 1000)

    print(f"Average time: {statistics.mean(times):.1f}ms")
    print(f"Median time: {statistics.median(times):.1f}ms")
    print(f"95th percentile: {statistics.quantiles(times, n=20)[18]:.1f}ms")
```

## Deployment Considerations

### 1. Production Configuration

```python
# Production-optimized configuration
prod_config = Config(
    # Model settings
    embedding_model="paraphrase-MiniLM-L3-v2",
    cache_size=2000,

    # Performance settings
    max_segments_per_query=100,
    default_budget=1000,

    # Features (selective for performance)
    enable_temporal_ranking=True,
    enable_semantic_diversity=False,
    enable_topic_clustering=False,

    # Monitoring
    timeout_seconds=30
)
```

### 2. Resource Management

```python
class ManagedContextSelector:
    def __init__(self, config=None):
        self.selector = ContextSelector(config)
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour

    def select(self, query, segments, budget=None):
        """Select with automatic cleanup."""
        # Periodic cleanup
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self._cleanup()
            self.last_cleanup = time.time()

        return self.selector.select(query, segments, budget)

    def _cleanup(self):
        """Cleanup resources."""
        self.selector.embedding_manager.clear_cache()
        self.selector.reset_stats()
```

### 3. Monitoring and Logging

```python
import logging

class MonitoredContextSelector:
    def __init__(self, config=None):
        self.selector = ContextSelector(config)
        self.logger = logging.getLogger(__name__)

    def select(self, query, segments, budget=None):
        """Select with monitoring."""
        start_time = time.time()

        try:
            result = self.selector.select(query, segments, budget)

            # Log success
            self.logger.info(
                f"Query processed successfully: {result.execution_time_ms:.1f}ms, "
                f"{len(result.selected_segments)} segments selected"
            )

            return result

        except Exception as e:
            # Log error
            self.logger.error(f"Query failed: {e}")
            raise

    def get_health_status(self):
        """Get system health status."""
        stats = self.selector.get_performance_stats()

        return {
            'status': 'healthy',
            'queries_processed': stats['queries_processed'],
            'avg_response_time': stats['average_execution_time_ms'],
            'cache_hit_rate': stats['cache_stats']['hit_rate'],
            'last_updated': time.time()
        }
```

## Best Practices

### 1. Document Preparation
- **Segment Size**: Use 100-200 word segments for optimal performance
- **Content Quality**: Clean text without headers/metadata
- **Domain Matching**: Ensure query vocabulary matches document content

### 2. Performance Optimization
- **Preload Documents**: Use `preload_documents()` for frequently accessed content
- **Configure Cache**: Adjust `cache_size` based on memory constraints
- **Feature Flags**: Disable unnecessary features for better performance

### 3. Error Handling
- **Input Validation**: Always validate queries and segments
- **Graceful Degradation**: Handle embedding model failures
- **Timeout Protection**: Set appropriate timeouts for production use

### 4. Testing
- **Real Data**: Test with actual documents, not synthetic data
- **Performance Testing**: Benchmark with realistic query loads
- **Edge Cases**: Test empty queries, malformed input, etc.

## Troubleshooting

### Common Issues

**Problem: Slow Performance**
```python
# Solution: Use fast configuration
selector = ContextSelector(fast_config())
selector.preload_documents(segments)
```

**Problem: Low Accuracy**
```python
# Solution: Check segment quality and domain matching
def validate_segments(segments):
    for seg in segments:
        if len(seg.text.split()) < 50:
            print(f"Warning: Segment {seg.id} too short")
        if len(seg.text.split()) > 300:
            print(f"Warning: Segment {seg.id} too long")
```

**Problem: No Results**
```python
# Solution: Debug query processing
result = selector.select(query, segments, budget=1000)
print("Debug info:", result.debug_info)

# Check TF-IDF vocabulary
processor = selector.tfidf_processor
vocab_size = processor.get_vocabulary_size()
print(f"Vocabulary size: {vocab_size}")
```

**Problem: Memory Issues**
```python
# Solution: Reduce cache size
selector.update_config(cache_size=500)

# Or clear cache periodically
selector.embedding_manager.clear_cache()
```

### Debug Mode

Enable detailed debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Create selector with debug info
selector = ContextSelector()
result = selector.select(query, segments, budget=1000)

# Print debug information
print("Query analysis:", result.debug_info.get('query_analysis'))
print("Score distribution:", result.debug_info.get('score_distribution'))
print("Additional features:", result.debug_info.get('additional_features'))
```

This developer guide provides comprehensive information for integrating, extending, and maintaining the V2 Context Selection System in production environments.