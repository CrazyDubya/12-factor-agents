# Theater Critics Multi-Agent System

A sophisticated multi-agent system utilizing Ollama and various language models to provide rotating ensemble theater criticism for musical scenes.

## 🎭 System Overview

The system employs **Gemma2:9b as the primary critic** alongside a **rotating ensemble of 5 specialized critics**, each using different Ollama models with distinct analytical perspectives:

### Critics Ensemble

| Critic | Model | Specialty | Focus Area |
|--------|-------|-----------|------------|
| **Eleanor Hartwell** (Primary) | `gemma2:9b` | Comprehensive Analysis | Overall artistic merit, technical execution |
| **Dr. Marcus Steinberg** | `qwen2.5:3b` | Academic Analysis | Musical theory, historical context |
| **Casey Rodriguez** | `llama3.2:3b` | Popular Appeal | Audience engagement, entertainment value |
| **Zara Blackthorne** | `theater-long-context` | Experimental Theater | Innovation, avant-garde elements |
| **Robert Sterling** | `llama3:8b` | Commercial Viability | Production value, marketability |
| **Luna Chen** | `gemma:7b` | Emotional Impact | Character development, storytelling |

## 🚀 Features

- **Multi-Perspective Analysis**: Each critic brings specialized expertise
- **Rotating Selection**: Random subset of critics for diverse viewpoints
- **Consensus Analysis**: Aggregated scoring with agreement/disagreement tracking
- **Comprehensive Scoring**: 6-category rating system plus specialty scores
- **CLI Interface**: Interactive and file-based scene analysis
- **Fallback Handling**: Graceful degradation when JSON parsing fails

## 📊 Analysis Framework

Each scene is evaluated across:
- **Musical Composition** - Melody, harmony, lyrical quality
- **Performance Quality** - Vocals, acting, choreography
- **Production Elements** - Staging, costumes, lighting
- **Narrative Integration** - Plot advancement, character development
- **Audience Engagement** - Entertainment value, emotional connection
- **Specialty Focus** - Critic's area of expertise

## 🛠️ Setup

### Prerequisites
- **Ollama** installed and running (`http://localhost:11434`)
- **Python 3.8+**
- Required models pulled in Ollama

### Install Required Models
```bash
ollama pull gemma2:9b
ollama pull qwen2.5:3b  
ollama pull llama3.2:3b
ollama pull llama3:8b
ollama pull gemma:7b
ollama pull theater-long-context:latest  # Custom model if available
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 🎪 Usage

### Command Line Interface

#### Basic Analysis (Default: Defying Gravity)
```bash
python3 cli.py
```

#### Analyze Scene from File
```bash
python3 cli.py --file sample_memory.json --critics 4
```

#### Interactive Scene Creation
```bash
python3 cli.py --interactive --save my_scene.json
```

#### List Available Critics
```bash
python3 cli.py --list-critics
```

#### Create Sample Scenes
```bash
python3 cli.py --create-samples
```

### Python API

```python
import asyncio
from main import SceneData, CriticEnsemble, ConsensusAnalyzer

async def analyze_scene():
    # Create scene
    scene = SceneData(
        title="Defying Gravity",
        musical="Wicked",
        description="Elphaba's climactic moment",
        lyrics="Something has changed within me..."
    )
    
    # Initialize ensemble
    ensemble = CriticEnsemble()
    
    # Get reviews (primary + 3 rotating critics)
    reviews = await ensemble.review_scene(scene, num_rotating_critics=3)
    
    # Calculate consensus
    consensus = ConsensusAnalyzer.calculate_consensus(reviews)
    
    return reviews, consensus

# Run analysis
asyncio.run(analyze_scene())
```

## 📁 File Structure

```
theater-critics-system/
├── main.py              # Core system implementation
├── cli.py               # Command-line interface
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── sample_*.json       # Sample scene files
└── *_results.json      # Analysis result outputs
```

## 🎯 Example Output

```
🎭 THEATER CRITICS ENSEMBLE REVIEW
================================================================================

📊 CONSENSUS: Strong Agreement
Overall Score: 8.2/10.0
Critics Participating: 4

🎬 Eleanor Hartwell (Primary) - Model: gemma2:9b
Overall Score: 8.5/10.0
Review: "Defying Gravity stands as one of musical theater's most powerful anthems...

🎬 Luna Chen (Emotion) - Model: gemma:7b  
Overall Score: 8.0/10.0
Specialty Analysis: The emotional trajectory is masterfully crafted...

📈 DETAILED CONSENSUS SCORES
Musical Composition: 8.8/10.0 (±0.4)
Performance Quality: 8.2/10.0 (±0.6)
Production Elements: 8.5/10.0 (±0.3)
```

## ⚙️ Configuration

### Model Selection
Modify the critic initialization in `main.py` to use different models:

```python
CriticType.ACADEMIC: TheaterCritic(
    "Dr. Marcus Steinberg", CriticType.ACADEMIC, "your-model:latest",
    "musical theory and historical context"
)
```

### Ollama Configuration
Ensure Ollama is running on `localhost:11434` or modify the URL in `main.py`:

```python
self.ollama_url = "http://your-ollama-host:11434/api/generate"
```

## 🚧 System Behavior

- **Graceful Fallback**: If models don't return JSON, the system extracts narrative analysis
- **Timeout Handling**: 120-second timeout per critic with error recovery
- **Consensus Analysis**: Automatic agreement/disagreement detection
- **Rotating Selection**: Random critic selection ensures diverse perspectives

## 📈 Performance

- **Concurrent Analysis**: All critics run in parallel for faster results
- **Model Efficiency**: Uses appropriate model sizes for different specialties
- **Error Recovery**: Robust handling of model failures and timeouts

## 🎨 Future Enhancements

- **Custom Model Training**: Fine-tune models for specific theater criticism styles
- **Historical Comparison**: Compare scenes against theater history database
- **Sentiment Analysis**: Deep emotional impact measurement
- **Visual Analysis**: Integration with staging and costume analysis
- **Audience Simulation**: Predict audience reactions based on demographics

---

*Built with Ollama, Python, and a passion for musical theater* 🎭