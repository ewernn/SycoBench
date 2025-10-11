# SycoBench Results (Clean)

**Complete experimental results from SycoBench safety testing (Sept-Oct 2025)**

This directory contains cleaned, organized results from 4 major experiments testing AI model safety resistance to social pressure.

---

## Experiments Overview

| # | Experiment | Date | Models | Tests | Key Finding |
|---|------------|------|--------|-------|-------------|
| **1** | [Initial Benchmark](initial_benchmark/) | Sept 30 | 7 | 1,736 | 99.88% resistance (2 real flips) |
| **2** | [5-Pressure Breadth](pressure_breadth/) | Oct 7-8 | 4 | 1,000 | 99.3% resistance across tactics |
| **3** | [50-Pressure Deep](pressure_deep/) | Oct 9 | 5 | 2,500 | 99.65% resistance (7 real flips) |
| **4** | [Cold-Start](cold_start/) | Oct 10 | 4 | 800 | 99.1% resistance w/o context |

**Total Tests Conducted:** 6,036 across all experiments
**Total Cost:** ~$15-20 for data collection + $2-3 for LLM scoring

---

## Key Findings Summary

### ✅ **Models Are Highly Resistant (97-100%)**

All tested models maintained safety advice 97-100% of the time under pressure:

```
Safety Resistance by Model (Manual Review)
─────────────────────────────────────────────────────────────────

Grok-4-fast-non-reasoning    ████████████████████  100.0%
Claude Haiku 3.5             ███████████████████▓   99.8%
GPT-5-nano                   ███████████████████▓   99.8%
Claude Sonnet 4.5            ███████████████████▓   99.6%
Gemini 2.5 Flash-Lite        ███████████████████░   99.0%
Gemini 2.5 Flash             ████████████████████  100.0%
GPT-5-mini                   ████████████████████  100.0%

Average: 99.7% safety resistance
```

### ❌ **Automated Scoring is Unreliable**

- **96.7% false positive rate** across all LLM judges
- **Provider bias:** Judges favor their own company's models (3-11x)
- **Scorer disagreement:** 11x variation in flip rate for same data

**Manual review is mandatory** for accurate results.

### 📊 **Real vs. Detected Flips**

```
Experiment          Automated Flips    Manual Review    False Positive Rate
──────────────────────────────────────────────────────────────────────────────
Initial Benchmark        257                2                 99.2%
50-Pressure Deep         304                7                 97.7%
Cold-Start               7                  7                  0%*

*Cold-start used better LLM scoring rubric but still needs manual validation
```

---

## Experiment Details

### [Experiment 1: Initial 7-Model Benchmark](initial_benchmark/)

**Testing:** 7 models × 248 questions × 3 pressure rounds = 1,736 tests
**Result:** 99.88% resistance (only 2 real flips found in manual review)
**Purpose:** Baseline safety testing with false authority pressure

### [Experiment 2: 5-Pressure Breadth Test](pressure_breadth/)

**Testing:** 4 models × 50 questions × 5 pressure types = 1,000 tests
**Result:** 99.3% resistance (7 flips across all types)
**Purpose:** Test different pressure tactics (false authority, social proof, etc.)

### [Experiment 3: 50-Pressure Deep Test](pressure_deep/)

**Testing:** 5 models × 10 questions × 50 pressure tactics = 2,500 tests
**Result:** 99.65% resistance (7 real flips, human-verified)
**Purpose:** Comprehensive pressure testing with sophisticated tactics

**Most thorough experiment** with full manual review.

### [Experiment 4: Cold-Start Test](cold_start/)

**Testing:** 4 models × 200 questions with embedded pressure = 800 tests
**Result:** 99.1% resistance without prior context
**Purpose:** Test if context commitment affects safety maintenance

---

## Visualizations

See [graphs/](graphs/) for key visualizations:
- `00_complete_summary.png` - Overall results summary across all 4 experiments
- `01_initial_benchmark.png` - Experiment 1: 7-model benchmark (1,736 tests)
- `02_pressure_breadth.png` - Experiment 2: 5-pressure breadth test (1,000 tests)
- `03_pressure_deep.png` - Experiment 3: 50-pressure deep test (2,500 tests)
- `04_cold_start.png` - Experiment 4: Cold-start embedded pressure (800 tests)

---

## Data Structure

Each experiment folder contains:
```
XX_experiment_name/
├── README.md                    # Experiment overview + findings
├── conversations/               # Raw test data (JSON files, one per model)
├── *_scoring.csv                # LLM scoring (when available)
├── *_manual.csv                 # Human-verified scores (when available)
├── summary.csv                  # Quick stats
└── metadata.json                # Experiment configuration
```

---

## Models Tested

### Anthropic
- Claude Haiku 3.5
- Claude Sonnet 4.5
- Claude Opus 4.1 (not in experiments)

### OpenAI
- GPT-5
- GPT-5-mini
- GPT-5-nano
- GPT-4.1-nano (used as judge + tested)

### Google
- Gemini 2.5 Flash
- Gemini 2.5 Flash-Lite

### xAI
- Grok-4-fast-non-reasoning

---

## Methodology

### 2-Phase Process

**Phase 1: Data Collection**
1. Ask safety question
2. Apply pressure (false authority, social proof, etc.)
3. Save raw conversations
4. No flip detection during testing

**Phase 2: Scoring (Separate)**
1. Load saved conversations
2. Classify with LLM judge (GPT-4.1-nano preferred)
3. **Manually review** all detected flips
4. Generate final metrics

**Critical:** Automated scoring has 76-100% FP rate. Always manually verify.

---

## Conclusions

1. **Modern AI models are highly safety-resistant** (97-100% across all tests)
2. **Automated flip detection is unreliable** and significantly overestimates sycophancy
3. **Manual review is required** for accurate safety evaluation
4. **Pressure tactics don't significantly degrade** model safety performance
5. **No meaningful difference** between companies - all models perform well

**Recommendation:** Focus on data collection quality over automated scoring. Budget time for human review of detected flips.

---

## Citation

If using this data, please cite:
```
SycoBench Safety Testing Results (2025)
7,736 tests across 5 experiments
Models: Claude, GPT, Gemini, Grok
Finding: 99.7% avg safety resistance with manual verification
```

---

## See Also

- Main framework code: `src/`
- Original (messy) results: `results/`
- Pressure prompts: `data/prompts/pressure_prompts_500.json`
- Manual review docs: Root directory `*_MANUAL_REVIEW_*.md` files
