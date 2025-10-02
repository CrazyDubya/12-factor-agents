# Repository Dashboard V5 - Quick Reference

## 🚀 Start Services

```bash
# All-in-one startup (recommended)
./start-dashboard.sh

# Or start individually:
npm start                        # API server (port 3000)
python3 -m http.server 8899     # Web server (port 8899)
```

## 🌐 Access URLs

- **Dashboard**: http://localhost:8899/dashboard-v5.html
- **Repository Detail**: http://localhost:8899/v5/repo-detail.html
- **API Health**: http://localhost:3000/health
- **API Docs**: See README.md for endpoint list

## 🔧 Development Commands

```bash
# Code Quality
npm run lint              # Check linting
npm run lint:fix          # Auto-fix linting issues
npm run format            # Format all files with Prettier
npm run format:check      # Check formatting without changes

# Server Management
npm start                 # Start API server
npm run dev               # Start API server (same as start)
```

## 📁 File Structure Cheat Sheet

### Backend (Node.js)

| File                   | Purpose                        | Lines |
| ---------------------- | ------------------------------ | ----- |
| `api-server.js`        | Main Express server            | 80    |
| `routes/github.js`     | GitHub CLI operations          | 178   |
| `routes/cloudflare.js` | Cloudflare Wrangler operations | 120   |
| `routes/combined.js`   | GitHub + Cloudflare combined   | 70    |

### Frontend (JavaScript)

| File                          | Purpose               | Lines |
| ----------------------------- | --------------------- | ----- |
| `v5/js/ollama_client.js`      | AI model integration  | 419   |
| `v5/js/github_fetcher.js`     | GitHub API client     | 291   |
| `v5/js/utils/api_helpers.js`  | API request utilities | 74    |
| `v5/js/utils/dom_helpers.js`  | DOM manipulation      | 143   |
| `v5/js/utils/repo_helpers.js` | Repository data utils | 180   |

### Configuration

| File               | Purpose                  |
| ------------------ | ------------------------ |
| `eslint.config.js` | ESLint 9 flat config     |
| `.prettierrc`      | Prettier formatting      |
| `.editorconfig`    | Cross-editor consistency |
| `.gitignore`       | Git ignore patterns      |

## 🔌 API Endpoints

### GitHub

```bash
# Repositories
GET  /api/github/repos                    # List repos
GET  /api/github/repo/:owner/:name        # View repo
POST /api/github/repo/create              # Create repo
POST /api/github/repo/clone               # Clone repo

# Issues
GET  /api/github/issue/list               # List issues
GET  /api/github/issue/view/:number       # View issue
POST /api/github/issue/create             # Create issue
POST /api/github/issue/close              # Close issue
POST /api/github/issue/comment            # Comment on issue

# Pull Requests
GET  /api/github/pr/list                  # List PRs
POST /api/github/pr/create                # Create PR
POST /api/github/pr/merge                 # Merge PR
GET  /api/github/pr/checks/:number        # View PR checks
```

### Cloudflare

```bash
# Pages
GET  /api/cloudflare/projects             # List projects
POST /api/cloudflare/project/create       # Create project
POST /api/cloudflare/deploy               # Deploy to Pages

# Containers (NEW 2025)
POST /api/cloudflare/container/deploy     # Deploy container
GET  /api/cloudflare/container/list       # List containers
```

### Combined

```bash
POST /api/combined/clone-and-deploy       # Clone GitHub → Deploy Cloudflare
```

## 🤖 AI Models (Ollama)

### Context Sizes

| Model        | Context | Best For             |
| ------------ | ------- | -------------------- |
| qwen-128k    | 128K    | Large repos/files    |
| llama3-32k   | 32K     | Code analysis        |
| gemma2-32k   | 32K     | Quality analysis     |
| llama32-long | 32K     | Long context         |
| mistral-32k  | 32K     | Documentation/README |
| qwen2.5:1.5b | 8K      | Quick tasks          |
| llama3.2:3b  | 8K      | Fast responses       |

### Smart Model Selection

The system automatically selects the best model based on task:

```javascript
const { model, settings } = await ollama.selectBestModel('readme');
// Returns: { model: 'mistral-32k', settings: { num_predict: 16384, ... }}
```

## 🛠️ Utility Functions

### API Helpers (`v5/js/utils/api_helpers.js`)

```javascript
await apiGet('/api/github/repos', { limit: 100 });
await apiPost('/api/github/repo/create', { name: 'test', description: '...' });
const healthy = await checkAPIHealth();
const errorMsg = formatError(error);
```

### DOM Helpers (`v5/js/utils/dom_helpers.js`)

```javascript
showLoading(element, 'Loading repositories...');
showError(element, 'Failed to load data');
showSuccess(element, 'Repository created!');
const card = createCard({ title: 'Repo Name', content: '...', actions: [...] });
formatFileSize(1024 * 1024); // "1 MB"
formatDate('2025-10-02'); // "Oct 2, 2025"
debounce(searchFunction, 300); // Debounced search
```

### Repository Helpers (`v5/js/utils/repo_helpers.js`)

```javascript
const stats = calculateStats(repos);
const filtered = filterRepos(repos, { language: 'TypeScript', minStars: 10 });
const sorted = sortRepos(repos, 'stars', 'desc');
const top10 = getTopRepos(repos, 'stars', 10);
const languages = getUniqueLanguages(repos);
const grouped = groupByLanguage(repos);
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8899
lsof -ti:8899 | xargs kill -9
```

### Check Server Logs

```bash
tail -f /tmp/api-server.log   # API server logs
tail -f /tmp/server.log        # Web server logs
```

### Restart Everything

```bash
# Kill all services
lsof -ti:3000,8899 | xargs kill -9

# Start fresh
./start-dashboard.sh
```

### GitHub CLI Issues

```bash
gh auth status               # Check authentication
gh auth login                # Re-authenticate
gh auth refresh              # Refresh token
```

### Cloudflare Wrangler Issues

```bash
wrangler whoami              # Check authentication
wrangler login               # Re-authenticate
```

### Ollama Not Responding

```bash
curl http://localhost:11434/api/version  # Check Ollama
ollama list                              # List installed models
ollama serve                             # Restart Ollama
```

## 📊 Repository Statistics

- **Total Repos**: 199
- **AI/ML Projects**: 95 (48%)
- **Languages**: 92
- **Total Size**: 18.6 GB

### Top Languages

1. TypeScript (129.6 MB) - 39 repos
2. Python (124.9 MB) - 145 repos
3. C (101.6 MB) - 14 repos
4. Jupyter Notebook (93.2 MB) - 22 repos
5. JavaScript (73.3 MB) - 79 repos

## 🎯 Common Tasks

### Create a New Repository

1. Click **➕ Create Repo** in dashboard header
2. Enter name and description
3. Choose public/private
4. Repository created with README, .gitignore, license

### Deploy to Cloudflare

1. Click **☁️ Deploy** on repository card
2. Choose deployment type:
   - **Pages** for static sites
   - **Container** for Docker apps
3. Enter project name
4. Wait for deployment
5. Get live URL

### AI Repository Analysis

1. Click **🔬 Deep Dive** on repository
2. Select AI model (128K context recommended for large repos)
3. Enter custom analysis prompt (optional)
4. Watch streaming analysis in real-time
5. Results saved to repository data

### View Issues & PRs

1. Click **🐛 Issues** to see open issues
2. Click **🔀 PRs** to see pull requests
3. Create new issues or PRs from dashboard
4. Changes sync immediately with GitHub

## 📚 Documentation

- **README.md** - Full project documentation
- **REFACTORING_SUMMARY.md** - Refactoring details
- **STATUS.md** - Current system status
- **CLEANUP_COMPLETE.md** - Cleanup summary
- **QUICK_REFERENCE.md** - This file

## 🔐 Security Notes

**Development Mode**:

- No authentication required (localhost only)
- Uses your GitHub CLI credentials
- Uses your Cloudflare Wrangler credentials

**Production Deployment** (Future):

- Add JWT authentication
- Implement rate limiting
- Configure HTTPS/SSL
- Secure environment variables

## 📈 Performance Tips

1. **Large Repos**: Use `qwen-128k` model (128K context)
2. **Quick Tasks**: Use `qwen2.5:1.5b` model (fast)
3. **Batch Operations**: Use combined endpoints
4. **Caching**: GitHub/Cloudflare data cached for 5 minutes

---

**Version**: V5
**Last Updated**: October 2, 2025
**Status**: Production Ready ✅
