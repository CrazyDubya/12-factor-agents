# Official Profiler - Comprehensive Political Analysis System

A sophisticated system for building detailed profiles of elected officials using public records, with comprehensive analysis of their career evolution, policy positions, and political effectiveness.

## Features

### Core Capabilities
- **Comprehensive Data Collection**: Automated gathering from Congress.gov, FEC, social media, C-SPAN, and government websites
- **Historical Career Tracking**: Complete timeline of positions, achievements, and career progression
- **SWOT Analysis**: Strategic assessment of Strengths, Weaknesses, Opportunities, and Threats
- **Issue Position Tracking**: Monitor evolution of views on key policy areas
- **Geographic Hierarchy**: Analysis across national, regional, state, county, city, and district levels
- **Transcript Processing**: NLP analysis of speeches, hearings, and public statements
- **Async Data Collection**: Background processing for continuous profile updates
- **Multiple Output Formats**: HTML, JSON, and PDF reports with visualizations

### Data Sources
- **Congress.gov API**: Legislative records, votes, bill sponsorship, committee assignments
- **Federal Election Commission**: Campaign finance data, financial disclosures
- **Social Media APIs**: Twitter/X archives, Facebook posts, public statements
- **Government Websites**: Official bios, press releases, committee information
- **C-SPAN Archives**: Video transcripts, speech analysis, public appearances
- **News Archives**: Media coverage, fact-checking databases

### Analysis Frameworks
- **SWOT Analysis**: Comprehensive political assessment with strategic recommendations
- **Position Evolution**: Track changes in policy stances over time with significance scoring
- **Legislative Effectiveness**: Metrics for bill passage, coalition building, and influence
- **Geographic Relevance**: Multi-level analysis from national to district-specific issues
- **Consistency Scoring**: Quantify reliability and flip-flop patterns
- **Media Sentiment**: NLP analysis of public statements and coverage

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for async tasks)
- Node.js (for certain scrapers)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd official_profiler
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database configuration
```

6. Initialize database:
```bash
python main.py --init-db
```

7. Import congressional data:
```bash
python main.py --import-congress 118
```

## Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/official_profiler

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
CONGRESS_API_KEY=your_congress_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
OPENAI_API_KEY=your_openai_api_key

# Processing Settings
SCRAPE_DELAY=1.0
MAX_CONCURRENT_REQUESTS=10
UPDATE_FREQUENCY_HOURS=24
```

### Database Setup
The system uses PostgreSQL with TimescaleDB for time-series data. Ensure TimescaleDB extension is installed:

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
```

## Usage

### Command Line Interface

#### Generate a Complete Profile
```bash
# By bioguide ID
python main.py --profile A000374 --format html

# By name (partial matching supported)
python main.py --profile "Alexandria Ocasio-Cortez" --format pdf

# JSON output for API integration
python main.py --profile "Bernie Sanders" --format json
```

#### SWOT Analysis
```bash
python main.py --swot A000374
```

#### List Officials
```bash
# All current officials
python main.py --list-officials

# Filter by state
python main.py --list-officials --state Virginia --limit 10
```

#### Data Import and Updates
```bash
# Initialize database
python main.py --init-db

# Import current Congress
python main.py --import-congress 118
```

### Async Task System

Start Celery workers for background processing:
```bash
# Start worker
celery -A utils.async_tasks worker --loglevel=info

# Start beat scheduler for periodic updates
celery -A utils.async_tasks beat --loglevel=info

# Monitor tasks
celery -A utils.async_tasks flower
```

### Python API Usage

```python
from official_profiler.main import OfficialProfiler
import asyncio

async def example_usage():
    profiler = OfficialProfiler()
    await profiler.initialize()

    try:
        # Generate profile
        filename = await profiler.generate_profile(
            bioguide_id="A000374",
            output_format="html"
        )
        print(f"Profile saved to: {filename}")

        # Run SWOT analysis
        swot = await profiler.run_swot_analysis(bioguide_id="A000374")
        print(f"Overall rating: {swot['overall_assessment']['competitiveness_rating']}")

        # List officials
        officials = await profiler.list_officials(state="Virginia")
        for official in officials:
            print(f"{official['name']} - {official['party']}")

    finally:
        await profiler.cleanup()

# Run the example
asyncio.run(example_usage())
```

## Architecture

### Core Components

#### 1. Data Models (`models/`)
- **Official**: Core official information and relationships
- **Position**: Career history and committee assignments
- **Statement**: Public statements with NLP analysis
- **Vote**: Legislative voting records
- **Issue**: Policy issues with geographic classification
- **PositionEvolution**: Tracking of view changes over time
- **SwotAnalysis**: Strategic assessment results
- **FinancialDisclosure**: Campaign finance and personal finances

#### 2. Data Collection (`apis/`, `collectors/`)
- **CongressAPI**: Congress.gov API client
- **FECAPI**: Federal Election Commission data
- **SocialMediaAPI**: Twitter/X and Facebook integration
- **WebScraper**: Government website scraping
- **CSpanScraper**: C-SPAN transcript extraction

#### 3. Analysis Engines (`analyzers/`)
- **SWOTAnalyzer**: Comprehensive political assessment
- **IssueTracker**: Position evolution and consistency analysis
- **TranscriptProcessor**: NLP analysis of speeches and statements

#### 4. Async Processing (`utils/`)
- **AsyncTasks**: Celery-based background processing
- **TaskMonitor**: Task management and monitoring

#### 5. Reporting (`reporting/`)
- **ProfileGenerator**: Comprehensive report generation
- **Visualizations**: Interactive charts and graphs
- **Template System**: Customizable HTML/PDF output

### Geographic Hierarchy

The system analyzes issues across multiple geographic levels:

- **National**: Federal legislation, foreign policy
- **Regional**: Multi-state concerns (e.g., water rights)
- **State**: State-specific legislation and policies
- **County**: Richmond-specific concerns (configurable)
- **City**: Municipal issues and local politics
- **District**: Congressional/legislative district priorities

### Issue Categories

Major policy areas tracked:
- Healthcare (Medicare, Medicaid, insurance)
- Economy (jobs, wages, inflation, trade)
- Education (K-12, higher education, student loans)
- Environment (climate change, clean energy)
- Defense (military, veterans, national security)
- Immigration (border security, reform, asylum)
- Infrastructure (transportation, broadband)
- Social Issues (civil rights, criminal justice)
- Foreign Policy (international relations, trade)
- Technology (AI, privacy, cybersecurity)

## SWOT Analysis Framework

### Strengths Assessment
- Legislative effectiveness and bill passage rates
- Committee leadership positions and influence
- Fundraising capability and financial resources
- Constituency engagement and approval ratings
- Coalition building and bipartisan relationships
- Media presence and communication effectiveness
- Experience and institutional knowledge

### Weaknesses Identification
- Poor legislative effectiveness or controversial votes
- Fundraising challenges or financial vulnerabilities
- Low constituency engagement or approval
- Extreme partisanship limiting coalition building
- Negative media coverage or scandal exposure
- Limited committee influence or leadership
- Age, health, or electability concerns

### Opportunities Recognition
- Emerging issues for leadership positioning
- Committee advancement possibilities
- Coalition building potential
- Media profile enhancement opportunities
- Fundraising growth potential
- Demographic shifts in district/state
- Electoral cycle timing advantages

### Threats Analysis
- Primary challenge risk assessment
- General election vulnerability
- Scandal or ethical exposure potential
- Party disfavor or base alienation
- Demographic changes threatening support
- National political environment headwinds
- Age, health, or fitness questions

## Data Security and Ethics

### Privacy Protections
- Only public records and statements are analyzed
- No private communications or confidential data
- Compliance with API terms of service
- Transparent methodology and data sources

### Ethical Guidelines
- Defensive security research only
- No assistance with malicious activities
- Factual, objective analysis without bias
- Clear attribution of sources and limitations

### Data Handling
- Secure storage of API keys and credentials
- Encrypted database connections
- Regular security updates and monitoring
- Audit trails for data collection activities

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include comprehensive docstrings
- Write unit tests for new functionality
- Update documentation for changes

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=official_profiler

# Run specific test categories
pytest tests/test_analyzers.py
```

## API Documentation

When running with FastAPI integration (future enhancement):
- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json
- ReDoc documentation: http://localhost:8000/redoc

## Performance Optimization

### Database Optimization
- Indexed bioguide_id, date fields, and foreign keys
- TimescaleDB for efficient time-series queries
- Connection pooling for concurrent access
- Query optimization for large datasets

### Async Processing
- Background data collection to avoid blocking
- Rate limiting for API compliance
- Parallel processing where possible
- Intelligent caching to reduce redundant requests

### Memory Management
- Streaming processing for large datasets
- Cleanup of temporary files and objects
- Efficient data structures for analysis
- Garbage collection optimization

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Check connection string in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/db_name
```

#### API Rate Limits
- Reduce SCRAPE_DELAY and MAX_CONCURRENT_REQUESTS
- Check API key quotas and usage limits
- Implement exponential backoff for retries

#### Memory Issues with Large Profiles
- Process data in smaller batches
- Use streaming for large transcript files
- Clear caches periodically during processing

#### Missing Dependencies
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check for system dependencies
sudo apt-get install postgresql-dev libpq-dev
```

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include system information and error logs

## Changelog

### Version 1.0.0 (Initial Release)
- Complete data collection pipeline
- SWOT analysis framework
- Issue tracking and position evolution
- HTML/JSON/PDF report generation
- Async task processing
- Comprehensive documentation