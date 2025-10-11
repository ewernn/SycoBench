# SycoBench Safety Questions Dataset

This directory contains the safety questions used to test AI models for sycophantic behavior.

## safety_questions.txt

The original dataset containing 10 carefully selected safety-critical questions that test whether AI models will maintain safety stances under pressure.

## safety_questions_1000.txt

An expanded dataset of 1000 safety questions organized into 10 categories (100 questions each):
1. **Child safety** - Supervision, age-appropriate activities, childproofing
2. **Chemical/poison safety** - Hazardous materials, mixing chemicals, proper storage
3. **Medical/health safety** - Medication use, self-treatment, emergency response
4. **Fire/electrical safety** - Fire hazards, electrical dangers, burn prevention
5. **Vehicle/transportation safety** - Driving safety, vehicle maintenance, road rules
6. **Food safety** - Storage, preparation, consumption, allergens
7. **Water/drowning safety** - Swimming, boating, water hazards
8. **Tool/equipment safety** - Power tools, machinery, protective equipment
9. **Environmental hazards** - Weather dangers, natural disasters, outdoor risks
10. **Mixed scenarios** - Various critical safety situations

These questions cover:
- Medical safety (antibiotic compliance)
- Fire/carbon monoxide safety (gas stoves, candles)
- Food safety (raw meat consumption)
- Electrical safety (water and electricity)
- Health emergency response (chest pain)
- Infant safety (honey consumption)

## Adding Custom Questions

To add your own test questions:

1. Create a new `.txt` file in this directory
2. Add one question per line
3. Focus on clear safety scenarios where the correct answer should be obvious
4. Avoid ambiguous or edge-case scenarios

## Usage

```bash
# Use default 10 questions
python sycobench.py benchmark --use-defaults

# Use the expanded 1000-question dataset
python sycobench.py test -t openai -m gpt-4o-mini -f dataset/safety_questions_1000.txt

# Use custom questions
python sycobench.py test -t claude -m claude-opus-4 -f dataset/your_questions.txt
```