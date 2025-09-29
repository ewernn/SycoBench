# Documentation Update Guidelines for SycoBench

## Core Principles
- **Delete first, add second** - remove outdated content before adding new
- **Present tense only** - document what IS, not what WAS
- **Concise and actionable** - every sentence should help the reader DO something
- **Zero history** - no changelogs, migration notes, or "previously" references
- **YAGNI for docs** - delete unused files and sections immediately; they create confusion

## Before You Update
Ask yourself:
1. **Why this doc?** - What specific problem are you solving?
2. **What else breaks?** - Which other docs reference this one?
3. **Is it salvageable?** - Should you rewrite instead of patch?

## Update Rules
1. **Delete anything that references:**
   - Old model versions that are deprecated
   - Fixed bugs or resolved issues
   - Previous API implementations
   - Historical benchmark results
   - Unused batch processing methods

2. **Keep only:**
   - Current API endpoints and models
   - Active configuration options
   - Working code examples
   - Current cost rates and limits
   - Essential safety patterns

3. **File management:**
   - Delete entire unused documentation files
   - Remove orphaned sections that no longer apply
   - Clean up broken internal links to deleted content
   - Remove references to deprecated tools in /tools directory

4. **Test every:**
   - Code example
   - API call pattern
   - CLI command
   - File path reference
   - Model identifier

## SycoBench-Specific Guidelines

### Model Documentation
- When a model is deprecated, remove ALL references immediately
- Update cost rates as soon as they change
- Delete examples using unavailable models
- Keep model configs in sync with `src/config.py`

### Batch Processing
- Document only active batch formats
- Remove references to deprecated batch APIs
- Update cost savings percentages when they change
- Delete outdated batch file examples

### Safety Patterns
- Keep only patterns actively used in `src/core/evaluation.py`
- Remove theoretical patterns not implemented
- Update flip detection logic when algorithm changes
- Delete outdated scoring interpretations

### Results & Analysis
- Never keep old benchmark results in docs
- Update scoring thresholds when changed
- Remove references to deleted analysis reports
- Keep only current result JSON structure

## Related Documentation
When updating one doc, check these for consistency:
- `main.md` - central documentation, must reflect all changes
- `README.md` - public-facing intro, keep minimal and current
- `docs/architecture.md` - if component structure changed
- `docs/batch_processing.md` - if batch system updated
- `docs/provider_api_guide_2025.md` - if API integrations changed
- Model files in `src/models/` - if API patterns documented

## Red Flags for Full Rewrite
- More than 50% needs deletion
- Core purpose has changed (e.g., from sync to batch processing)
- Structure doesn't match current code organization
- Multiple broken code examples
- References to more than 3 deprecated features

## Quick Checklist for Common Updates

### Adding a New Model
1. Add to `main.md` model support section
2. Add configuration example
3. Add usage example
4. Delete any "coming soon" references to this model
5. Update cost comparison if relevant

### Deprecating a Model
1. Remove from ALL documentation immediately
2. Delete configuration examples
3. Remove from model lists
4. Delete cost references
5. Remove from quick start guides

### Changing API Pattern
1. Update every code example using old pattern
2. Delete explanation of old pattern
3. Update error handling examples
4. Verify all CLI command examples
5. Check batch creation examples

### Updating Costs
1. Update all cost tables
2. Update example calculations
3. Update batch savings percentages
4. Delete outdated cost comparisons
5. Update "typical costs" section

## Documentation Hierarchy
```
main.md (source of truth)
├── README.md (derives key points)
├── docs/architecture.md (expands on structure)
├── docs/batch_processing.md (details batch system)
└── docs/provider_api_guide_2025.md (API specifics)
```

When in doubt about where something belongs:
- Core functionality → main.md
- Public introduction → README.md
- Implementation details → docs/ subdocs
- Never duplicate - link instead

## The Final Rules

**When in doubt, delete.**
Wrong documentation is worse than no documentation.

**If it's not testable, it's not documentable.**
Every documented feature must be verifiable.

**Present tense, active voice, second person.**
"You run the benchmark" not "The benchmark can be run"

Remember: Good documentation is like good code - it's not done when there's nothing left to add, but when there's nothing left to remove.