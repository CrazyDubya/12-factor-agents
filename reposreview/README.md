# Repository Dashboard V5 - AI-Powered Repository Analysis & Deployment

Complete repository analysis and deployment platform with 128K context AI models, GitHub CLI integration, and Cloudflare deployment capabilities.

## 🚀 Quick Start

```bash
./start-dashboard.sh
```

This starts:

- API server on port 3000 (GitHub + Cloudflare integration)
- Web server on port 8899 (dashboard interface)
- Opens browser at http://localhost:8899/dashboard-v5.html

## ✨ Features

### 🧠 AI Analysis (128K Context Models)

- **5 Expanded Models**: qwen-128k, llama3-32k, gemma2-32k, llama32-long, mistral-32k
- **Real-time Streaming**: See analysis progress as it generates
- **Deep Repository Analysis**: Comprehensive code quality, architecture, and recommendations
- **One-Click Re-Analysis**: Update any repository analysis instantly

### ☁️ Smart Deployment

- **Cloudflare Pages**: Deploy static sites with one click
- **Cloudflare Containers**: Deploy Dockerized applications automatically (NEW 2025)
- **Smart Detection**: Automatically detects Dockerfile vs static content
- **Clone & Deploy**: Direct from GitHub to Cloudflare in one operation

### 🐙 GitHub Integration

- **📥 Load Repos**: Fetch repositories directly from GitHub CLI
- **➕ Create Repos**: Create new repositories with templates
- **🐛 Issues**: List, view, create, and manage GitHub issues
- **🔀 Pull Requests**: View, create, and merge pull requests
- **📊 Live Data**: All operations use GitHub CLI for real-time accuracy

### 📊 Repository Statistics

- **199 Repositories Analyzed**
- **95 AI/ML Projects** (48%)
- **92 Programming Languages**
- **18.6 GB Total Code**

## 🏗️ Project Structure

```
reposreview/
├── 📄 Core Files
│   ├── dashboard-v5.html          # Main dashboard interface
│   ├── api-server.js              # Express API server (refactored)
│   ├── start-dashboard.sh         # One-command startup
│   ├── package.json               # Dependencies & scripts
│   └── package-lock.json
│
├── 🔌 API Routes (Modular)
│   └── routes/
│       ├── github.js              # GitHub CLI operations
│       ├── cloudflare.js          # Cloudflare Wrangler operations
│       └── combined.js            # Combined GitHub + Cloudflare workflows
│
├── 🎨 Dashboard Assets
│   └── v5/
│       ├── repo-detail.html       # Deep analysis view
│       └── js/
│           ├── ollama_client.js   # AI integration
│           ├── github_fetcher.js  # GitHub API client
│           └── utils/             # Reusable utilities (NEW)
│               ├── api_helpers.js     # API request utilities
│               ├── dom_helpers.js     # DOM manipulation utilities
│               └── repo_helpers.js    # Repository data utilities
│
├── 📊 Data
│   └── data/
│       └── crazydubya_repositories_aiml_deep.json  # 199 analyzed repos
│
├── 🤖 Ollama Models
│   ├── Modelfile.qwen-128k        # Qwen 128K context
│   ├── Modelfile.llama3-32k       # Llama 3 32K context
│   ├── Modelfile.gemma2-32k       # Gemma 2 32K context
│   ├── Modelfile.llama32-long     # Llama 3.2 long context
│   └── Modelfile.mistral-32k      # Mistral 32K context
│
└── ⚙️ Configuration
    ├── eslint.config.js           # ESLint 9 flat config
    ├── .prettierrc                # Prettier config
    ├── .editorconfig              # Editor config
    └── .gitignore                 # Git ignore patterns
```

## 📋 Prerequisites

### Required Tools

**GitHub CLI**:

```bash
brew install gh
gh auth login
```

**Cloudflare Wrangler**:

```bash
npm install -g wrangler
wrangler login
```

**Ollama** (for AI analysis):

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull expanded context models
ollama create qwen-128k -f Modelfile.qwen-128k
ollama create llama3-32k -f Modelfile.llama3-32k
ollama create gemma2-32k -f Modelfile.gemma2-32k
ollama create llama32-long -f Modelfile.llama32-long
ollama create mistral-32k -f Modelfile.mistral-32k
```

## 🔧 Development

### Install Dependencies

```bash
npm install
```

### Available Scripts

```bash
npm run start       # Start API server
npm run dev         # Development mode
npm run lint        # Check code quality
npm run lint:fix    # Fix linting issues
npm run format      # Format code with Prettier
npm run format:check # Check formatting
```

### Code Quality

- **ESLint**: JavaScript linting with recommended rules
- **Prettier**: Consistent code formatting
- **EditorConfig**: Cross-editor consistency

## 🔌 API Endpoints

The API server (`http://localhost:3000`) provides:

### GitHub Operations

- `GET /api/github/repos` - List repositories
- `GET /api/github/repo/:owner/:name` - View repository
- `POST /api/github/repo/create` - Create repository
- `POST /api/github/repo/clone` - Clone repository

### GitHub Issues

- `GET /api/github/issue/list` - List issues
- `GET /api/github/issue/view/:number` - View issue
- `POST /api/github/issue/create` - Create issue
- `POST /api/github/issue/close` - Close issue
- `POST /api/github/issue/comment` - Comment on issue

### GitHub Pull Requests

- `GET /api/github/pr/list` - List pull requests
- `POST /api/github/pr/create` - Create pull request
- `POST /api/github/pr/merge` - Merge pull request
- `GET /api/github/pr/checks/:number` - View PR checks

### Cloudflare Operations

- `GET /api/cloudflare/projects` - List Pages projects
- `POST /api/cloudflare/project/create` - Create project
- `POST /api/cloudflare/deploy` - Deploy to Pages
- `POST /api/cloudflare/container/deploy` - Deploy container (NEW)
- `GET /api/cloudflare/container/list` - List containers

### Combined Operations

- `POST /api/combined/clone-and-deploy` - Clone from GitHub & deploy to Cloudflare

## 🎯 Usage Examples

### Deploy Repository to Cloudflare

1. Click **☁️ Deploy** on any repository card
2. Choose deployment type:
   - **Pages**: For static sites (HTML, React, Vue, etc.)
   - **Container**: For Dockerized applications
3. Enter project name (or use default)
4. Wait for deployment to complete
5. Get live URL!

### Create GitHub Repository

1. Click **➕ Create Repo** in header
2. Enter name and description
3. Choose public/private
4. Repository created with README, .gitignore, and license

### AI Repository Analysis

1. Click **🔬 Deep Dive** on any repository
2. Select AI model (128K context recommended)
3. Enter custom analysis prompt (optional)
4. Watch streaming analysis in real-time
5. Results saved to repository data

### View GitHub Issues & PRs

1. Click **🐛 Issues** to see open issues
2. Click **🔀 PRs** to see pull requests
3. Create new issues or PRs directly from dashboard
4. All changes sync immediately with GitHub

## 📊 Repository Categories

### AI/ML Projects (95 repos)

- Agent frameworks (AutoGPT, autogen, agent-squad)
- LLM experiments (Claude, GPT, Llama)
- ML tools and libraries
- AI research projects

### Web Development (26 repos)

- Frontend frameworks (React, Vue, Svelte)
- Backend APIs (FastAPI, Express)
- Full-stack applications

### Data Science (16 repos)

- Jupyter notebooks
- Analysis tools
- Visualization libraries

### System Tools (31 repos)

- CLI utilities
- Automation scripts
- DevOps tools

## 🔧 Troubleshooting

### API Server Won't Start

```bash
# Check if port 3000 is in use
lsof -ti:3000

# Kill existing process
kill -9 $(lsof -ti:3000)

# Check logs
tail -f /tmp/api-server.log
```

### GitHub CLI Issues

```bash
# Re-authenticate
gh auth login

# Check status
gh auth status
```

### Cloudflare Deployment Fails

```bash
# Re-authenticate
wrangler login

# Check auth
wrangler whoami

# Set account ID
export CLOUDFLARE_ACCOUNT_ID=your_account_id
```

### Ollama Analysis Hangs

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama
ollama serve

# Check models
ollama list
```

## 📈 Repository Statistics

### Overall Metrics

- **Total Repositories**: 199
- **Original**: 66 (33%)
- **Forked**: 133 (67%)
- **Total Size**: 18.6 GB
- **Languages**: 92

### Top Languages

1. **TypeScript**: 129.6 MB (39 repos)
2. **Python**: 124.9 MB (145 repos)
3. **C**: 101.6 MB (14 repos)
4. **Jupyter Notebook**: 93.2 MB (22 repos)
5. **JavaScript**: 73.3 MB (79 repos)

### Timeline

- **2025**: 185 repositories (93%)
- **2024**: 14 repositories (7%)

## 🔧 Code Quality & Architecture

### Refactored Modular Design

The codebase has been fully refactored for maintainability and scalability:

- **Modular API Routes**: Separated GitHub, Cloudflare, and combined operations into dedicated modules
- **Utility Libraries**: Reusable functions for API calls, DOM manipulation, and repository data processing
- **100% JSDoc Coverage**: All functions fully documented with type annotations
- **ESLint + Prettier**: Code quality enforced with modern tooling (0 errors, 6 acceptable warnings)

### Development Workflow

```bash
# Install dependencies
npm install

# Run linting
npm run lint        # Check for issues
npm run lint:fix    # Auto-fix issues

# Run formatting
npm run format      # Format all files
npm run format:check # Check formatting
```

See [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for complete refactoring details.

## 🔮 Future Enhancements

- [ ] **Unit Tests**: Vitest for utility functions
- [ ] **Integration Tests**: Playwright for E2E testing
- [ ] **Performance Bundle**: Minify and bundle JavaScript
- [ ] **Batch Deployment**: Deploy multiple repos at once
- [ ] **GitHub Actions Integration**: Auto-deploy on push
- [ ] **Cloudflare Workers**: Deploy serverless functions
- [ ] **Database Integration**: Store deployment history
- [ ] **Analytics Dashboard**: Track deployment metrics
- [ ] **Team Collaboration**: Multi-user support

## 🛠️ Built With

- **Express.js**: API server
- **GitHub CLI** (`gh`): GitHub operations
- **Cloudflare Wrangler**: Cloudflare deployments
- **Ollama**: Local AI with 128K context models
- **Vanilla JavaScript**: Dashboard frontend

## 📝 License

See individual repository licenses for specific projects.

## 👤 Author

**CrazyDubya (Puppuccino)**

- GitHub: [@CrazyDubya](https://github.com/CrazyDubya)
- Twitter: [@RubberDucky_AI](https://twitter.com/RubberDucky_AI)
- Blog: [claudexml.com](https://claudexml.com)

---

**Last Updated**: October 2, 2025
**Dashboard Version**: V5
**Total Repositories Analyzed**: 199
**Space Optimized**: 11.6MB saved
