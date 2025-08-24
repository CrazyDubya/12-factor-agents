# 🦄 Unicorn Games - Asset Generation Pipeline

**Production-ready AI asset generation system for 5 unicorn/princess board games**

## ✅ Mission Accomplished

**204 professional game assets** generated across 5 complete board games using proven standalone pipeline.

### Current Status
- ✅ **Crystal Crown Quest**: 57 assets  
- ✅ **Memory Palace**: 40 assets
- ✅ **Princess Academy**: 36 assets  
- ✅ **Rainbow Bridge Adventure**: 36 assets
- ✅ **Starlight Stable**: 35 assets

**All games ready for development with professional asset libraries.**

## 📋 Framework Overview

### 6-Phase Testing Strategy

| Phase | Name | Purpose | Critical |
|-------|------|---------|----------|
| 1 | Environment Verification | Check M2 MacStudio setup, disk space, dependencies | ✅ Yes |
| 2A | Single Image Test | Verify basic generation with one test image | ✅ Yes |
| 2B | Basic Generation | Test 5 different asset types | ⚠️ Important |
| 3 | Quality Validation | Analyze generated images for game suitability | ⚠️ Important |
| 4 | Batch Generation | Test generating 10-50 assets efficiently | 📝 Optional |
| 5 | Performance Optimization | Optimize speed and quality settings | 📝 Optional |
| 6 | Integration Preparation | Prepare assets for game engine integration | 📝 Optional |

## 🚀 Quick Start

### Run All Tests
```bash
# Complete test suite (recommended)
./run_all_tests.sh

# Continue even if some phases fail
./run_all_tests.sh --continue-on-failure

# Verbose output for debugging
./run_all_tests.sh --verbose
```

### Run Individual Phases
```bash
# Phase 1: Environment check
bash test-scripts/01_environment_check.sh

# Phase 2A: Single image generation
python3 test-scripts/02_single_image_test.py

# Phase 2B: Basic 5-type generation
python3 test-scripts/03_basic_generation_test.py

# Phase 3: Quality validation
python3 test-scripts/04_quality_validation_test.py

# Phase 4: Batch generation testing
python3 test-scripts/05_batch_generation_test.py
```

### Quick Status Check
```bash
python3 quick_status_check.py
```

## 🛠️ Supported Generators

### 1. MFLUX (Local, Automated) ⭐ Recommended
- **Technology**: Apple MLX + FLUX models
- **Performance**: 8-15 seconds per image on M2
- **Setup**: `pip install mflux`
- **Pros**: Fast, local, no API costs
- **Cons**: 5-minute model download on first run

### 2. Draw Things (Local, Manual)
- **Technology**: Core ML optimized app
- **Performance**: Variable, user-controlled
- **Setup**: Install from Mac App Store
- **Pros**: Easy setup, GUI control
- **Cons**: Manual operation required

### 3. MCP Servers (Cloud, Claude Integration)
- **Technology**: Model Context Protocol with Claude
- **Performance**: Depends on service (EverArt, Replicate)
- **Setup**: API keys + Claude Desktop config
- **Pros**: Integrated workflow, high quality
- **Cons**: API costs, requires setup

## 📊 Expected Results

### M2 MacStudio Performance
```
Environment: 76%+ success rate
MFLUX Generation: 8-15s per image
Complete 467 assets: 2-4 hours
Quality Score: 7-9/10 (child-appropriate)
```

### Success Criteria
- **Phase 1**: 60%+ tests passing (environment ready)
- **Phase 2**: At least 1 generator working
- **Phase 3**: 6+ quality score (game-suitable)
- **Phase 4**: 50%+ batch success rate

## 📁 Directory Structure

```
unicorn-games-tests/
├── test-scripts/           # Test execution scripts
│   ├── 01_environment_check.sh
│   ├── 02_single_image_test.py
│   ├── 03_basic_generation_test.py
│   ├── 04_quality_validation_test.py
│   └── 05_batch_generation_test.py
├── test-utils/            # Shared testing utilities
│   ├── test_logger.py
│   ├── test_config.py
│   └── __init__.py
├── test-outputs/          # Generated test assets
│   ├── phase1_env_verification/
│   ├── phase2_minimal_generation/
│   ├── phase3_quality_validation/
│   └── phase4_batch_generation/
├── test-results/          # JSON result files
├── test-logs/             # Detailed log files
├── config/                # Test configuration
│   └── test_config.json
├── run_all_tests.sh       # Complete test runner
├── quick_status_check.py  # Status overview
└── README.md              # This file
```

## 🔧 Configuration

### Environment Requirements
- **Hardware**: Apple Silicon Mac (M1/M2/M3)
- **RAM**: 16GB+ (32GB+ recommended)
- **Storage**: 25GB+ free space
- **OS**: macOS with Python 3.11+

### Generator Setup

#### MFLUX (Automated)
```bash
pip install mflux
# First run downloads 3.2GB model automatically
```

#### Draw Things (Manual)
```bash
# Install from Mac App Store
open "macappstore://apps.apple.com/app/draw-things/id1659188388"
```

#### MCP Servers (Claude Integration)
```bash
# Install MCP servers
npx -y @smithery/cli install @modelcontextprotocol/server-everart --client claude

# Configure Claude Desktop with API keys
# See: config/claude_desktop_config_sample.json
```

## 📈 Quality Metrics

### Asset Categories Tested
- **Characters**: Princess/unicorn sprites (128x128)
- **Cards**: Crystal/magic cards (80x120)
- **UI Elements**: Buttons, counters (48x48 to 150x50)
- **Tiles**: Cloud islands, bridge segments (96x96)
- **Boards**: Game backgrounds (1600x400)

### Quality Criteria
- **File Properties**: Correct size, format, readable
- **Dimensions**: Appropriate for game use
- **Content**: Child-appropriate (ages 6-10)
- **Visual Quality**: Clear, detailed, professional
- **Game Suitability**: Ready for board game integration

## 🎮 Game Integration Ready

Once testing passes, assets are ready for:
- **Rainbow Bridge Quest**: Color recognition game
- **Unicorn Garden Memory Palace**: Memory development
- **Crystal Crown Chronicles**: Resource management
- **Starlight Stable Rescue**: Cooperative gameplay
- **Princess Academy Racing Championship**: Deck building

## 🔍 Troubleshooting

### Common Issues

#### MFLUX Model Download
```bash
# If stuck downloading, check disk space
df -h

# Or try manual download location check
ls ~/.cache/mflux/
```

#### No Images Generated
```bash
# Check test outputs
find test-outputs -name "*.png" -ls

# Re-run individual phases
python3 test-scripts/02_single_image_test.py
```

#### Quality Issues
```bash
# Run quality validation
python3 test-scripts/04_quality_validation_test.py

# Check detailed report
cat test-results/phase3_quality_validation_results.json
```

### Getting Help
1. **Check logs**: `test-logs/` directory
2. **Review results**: `test-results/` JSON files
3. **Run status check**: `python3 quick_status_check.py`
4. **Test individual phases** to isolate issues

## 🎯 Success Indicators

### ✅ Ready for Production
- Environment: 76%+ success
- Generation: At least 1 working generator
- Quality: 6+ score average
- Batch: Can generate 10+ assets

### ⚠️ Needs Improvement
- Environment: 50-75% success
- Generation: Intermittent failures
- Quality: 4-6 score average
- Batch: Limited capability

### ❌ Requires Setup
- Environment: <50% success
- Generation: No working generators
- Quality: <4 score average
- Batch: Not functional

## 🦄 Framework Philosophy

This testing framework follows the principle of **"Test Generators Separately"**:

1. **Validate Environment First**: Ensure hardware/software ready
2. **Test Basic Generation**: Verify core capability works
3. **Assess Quality**: Ensure output meets game standards  
4. **Scale to Batches**: Confirm production viability
5. **Optimize Performance**: Fine-tune for efficiency
6. **Prepare Integration**: Ready for game engine use

**No game code dependencies** - tests generators in isolation to ensure they work before any integration effort.

---

*Generated by Claude Code for the Unicorn Games project - Testing framework v1.0*