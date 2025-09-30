# 🧠 SycoBench Main Template - Central Routing & Architecture Guide

> **⚠️ CRITICAL: This document is the central brain of the SycoBench codebase. It MUST be updated after ANY significant changes to maintain accuracy and usefulness.**

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start Routes](#quick-start-routes)
3. [Architecture Map](#architecture-map)
4. [Core Components](#core-components)
5. [API Routes](#api-routes)
6. [Batch Processing Routes](#batch-processing-routes)
7. [Data Flow](#data-flow)
8. [Configuration Routes](#configuration-routes)
9. [Results & Analysis Routes](#results-analysis-routes)
10. [Development Routes](#development-routes)
11. [Maintenance Checklist](#maintenance-checklist)

---

## 🎯 Overview

SycoBench is a safety benchmark for evaluating LLM responses to potentially harmful questions. This document serves as the central routing guide for navigating and understanding the entire codebase.

**Primary Entry Points:**
- `sycobench.py` - Main CLI interface
- `run_benchmark_sample.py` - Quick testing with sample questions
- `src/cli.py` - Command-line argument parsing

> **📝 UPDATE NOTICE: When adding new entry points or scripts, update this section immediately.**

---

## 🚀 Quick Start Routes

### For First-Time Users
1. **Installation**: `pip install -e .` → Installs package in development mode
2. **Test Installation**: `python test_installation.py` → Verifies setup
3. **Quick Demo**: `python run_benchmark_sample.py` → Tests 5 questions with GPT-4-mini

### For Regular Testing
```bash
# Standard benchmark run
python sycobench.py --questions 100 --models gpt-4o-mini claude-3-haiku

# Batch processing (cost-effective)
python sycobench.py --questions 1000 --models gemini-2.0-flash-exp --batch
```

### For Analysis
```bash
# Visualize results
python visualize_existing_results.py

# View results
cat results/sycobench_results_*.json
```

> **📝 UPDATE NOTICE: Add new common workflows here as they are developed.**

---

## 🏗️ Architecture Map

```
SycoBench/
│
├── 🎯 Entry Points
│   ├── sycobench.py                 # Main CLI interface
│   ├── run_benchmark_sample.py      # Quick testing script
│   └── test_installation.py         # Setup verification
│
├── 📦 Core Package (src/)
│   ├── cli.py                       # CLI argument parsing
│   ├── config.py                    # Central configuration
│   │
│   ├── 🧠 core/                     # Core logic
│   │   ├── sycobench.py            # Main benchmark class
│   │   ├── conversation_manager.py  # Manages LLM conversations
│   │   └── evaluation.py           # Safety evaluation logic
│   │
│   ├── 🤖 models/                   # Model implementations
│   │   ├── openai_models.py        # OpenAI API (GPT-4, etc.)
│   │   ├── claude.py               # Anthropic Claude API
│   │   ├── gemini.py               # Google Gemini API
│   │   └── grok.py                 # xAI Grok API
│   │
│   └── 🛠️ utils/                    # Utilities
│       ├── logging_config.py       # Logging setup
│       ├── rate_limiter.py         # API rate limiting
│       └── error_handler.py        # Error handling
│
├── 📊 Data & Results
│   ├── dataset/                     # Question datasets
│   ├── results/                     # Benchmark results
│   └── benchmark_results/           # Analysis outputs
│
└── 📚 Documentation
    ├── README.md                    # Main documentation
    ├── BATCH_GUIDE.md              # Batch processing guide
    └── COST_COMPARISON.md          # Cost analysis
```

> **📝 UPDATE NOTICE: Update this tree when adding new directories or reorganizing structure.**

---

## 🔧 Core Components

### 1. SycoBench Class (`src/core/sycobench.py`)
**Purpose**: Main orchestrator for benchmark execution
**Key Methods**:
- `run_benchmark()` - Main execution loop
- `evaluate_model()` - Evaluates single model
- `save_results()` - Persists results to JSON

**Data Flow**:
```
Questions → ConversationManager → Model API → Evaluation → Results
```

### 2. ConversationManager (`src/core/conversation_manager.py`)
**Purpose**: Manages multi-turn conversations with models
**Key Features**:
- Handles refusal detection
- Manages follow-up attempts
- Tracks conversation history

### 3. Evaluation Module (`src/core/evaluation.py`)
**Purpose**: Determines if responses are compliant or refusing
**Key Functions**:
- `is_refusal()` - Detects safety refusals
- `evaluate_response()` - Scores responses

> **📝 UPDATE NOTICE: Document new core components or significant method changes here.**

---

## 🌐 API Routes

### Regular API Processing
**Route**: `sycobench.py` (without `--batch` flag)
**Flow**:
1. Load questions from dataset
2. Initialize model clients
3. Process questions sequentially
4. Apply rate limiting
5. Save results incrementally

### Supported Models & Their Routes:
| Model | File | API Endpoint |
|-------|------|--------------|
| GPT-4/3.5 | `models/openai_models.py` | OpenAI API |
| Claude | `models/claude.py` | Anthropic API |
| Gemini | `models/gemini.py` | Google AI API |
| Grok | `models/grok.py` | xAI API |

> **📝 UPDATE NOTICE: Add new models and their routes to this table.**

---

## 📦 Batch Processing Routes

### Batch API Processing
**Route**: `sycobench.py --batch`
**Supported Models**:
- OpenAI: GPT-4o-mini, GPT-3.5-turbo
- Gemini: All Gemini models

**Flow**:
1. Create batch request file (JSONL)
2. Submit batch job
3. Poll for completion
4. Download and process results
5. Convert to standard format

**Key Files**:
- Batch creation: Model-specific `create_batch()` methods
- Batch monitoring: Model-specific `poll_batch()` methods
- Results processing: Model-specific `process_batch_results()` methods

> **📝 UPDATE NOTICE: Update when adding batch support for new models.**

---

## 📊 Data Flow

### Question Processing Pipeline
```
1. Dataset Loading
   └─> dataset/safety_questions.txt or safety_questions_1000.txt

2. Model Selection
   └─> CLI args → config.py → model initialization

3. Processing
   ├─> Regular: Sequential API calls with rate limiting
   └─> Batch: Bulk submission → async processing

4. Evaluation
   └─> evaluation.py → compliance/refusal detection

5. Results Storage
   └─> results/sycobench_results_[timestamp].json

6. Analysis
   └─> visualize_existing_results.py → charts & summaries
```

> **📝 UPDATE NOTICE: Update this flow when changing the processing pipeline.**

---

## ⚙️ Configuration Routes

### Environment Variables
**File**: `.env` (create from `.env.example` if needed)
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
XAI_API_KEY=your_key
```

### Configuration Settings
**File**: `src/config.py`
- Model configurations
- Rate limits
- Batch settings
- Default parameters

### Adding New Models
1. Create model file in `src/models/`
2. Update `SUPPORTED_MODELS` in `config.py`
3. Add to model factory in `sycobench.py`
4. Update this documentation

> **📝 UPDATE NOTICE: Document configuration changes and new settings here.**

---

## 📈 Results & Analysis Routes

### Results Storage
**Location**: `results/`
**Format**: JSON with structure:
```json
{
  "metadata": {...},
  "results": [
    {
      "question_id": "001",
      "question": "...",
      "responses": {...},
      "compliance_scores": {...}
    }
  ],
  "summary": {...}
}
```

### Analysis Tools
1. **Basic Visualization**: `python visualize_existing_results.py`
2. **Custom Analysis**: Load JSON files and analyze
3. **Batch Results**: Check `benchmark_results/` for batch-specific analysis

> **📝 UPDATE NOTICE: Add new analysis tools and visualization scripts here.**

---

## 🛠️ Development Routes

### Adding New Features

#### New Model Support
1. Create `src/models/new_model.py`
2. Implement required interface methods
3. Add to `config.py`
4. Update model factory
5. Test with sample questions
6. **UPDATE THIS DOCUMENTATION**

#### New Evaluation Metrics
1. Modify `src/core/evaluation.py`
2. Update result structure
3. Adjust visualization scripts
4. **UPDATE THIS DOCUMENTATION**

#### New Batch Provider
1. Implement batch methods in model class
2. Update batch detection logic
3. Add to BATCH_GUIDE.md
4. **UPDATE THIS DOCUMENTATION**

### Testing Routes
```bash
# Unit tests (when implemented)
pytest tests/

# Integration test
python test_installation.py

# Quick functionality test
python run_benchmark_sample.py
```

> **📝 UPDATE NOTICE: Add new development workflows and testing procedures here.**

---

## ✅ Maintenance Checklist

### After ANY Significant Changes:

- [ ] **Update this main_template.md** with new routes/components
- [ ] Update README.md if user-facing features changed
- [ ] Update BATCH_GUIDE.md if batch processing changed
- [ ] Update docstrings in modified files
- [ ] Run test_installation.py to verify nothing broke
- [ ] Test with run_benchmark_sample.py
- [ ] Commit with clear message describing changes

### Weekly Maintenance:
- [ ] Review and update cost estimates in COST_COMPARISON.md
- [ ] Check for new model API updates
- [ ] Verify all documentation links still work
- [ ] Run full test suite

### Before Major Releases:
- [ ] Full documentation review
- [ ] Update all version numbers
- [ ] Test all example commands
- [ ] Verify batch processing works
- [ ] **Ensure this main_template.md is fully up-to-date**

---

## 🚨 Critical Reminders

1. **This document is the source of truth** - Keep it updated!
2. **Documentation debt compounds** - Update immediately after changes
3. **New developers depend on this** - Be thorough and clear
4. **Automation helps** - Consider adding pre-commit hooks for doc updates

---

> **Last Updated**: [Auto-update this date when modifying]
> 
> **Maintainer Notes**: This document should be the FIRST thing updated after any architectural changes. It serves as the central nervous system of the SycoBench project.