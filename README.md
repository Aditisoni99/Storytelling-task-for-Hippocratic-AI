Built for Hippocratic AI by Aditi Soni

# LITTLE PLUM : YOUR BEDTIME STORY FRIEND" 
An AI-powered storytelling system for children aged 5 to 10, featuring built-in quality control and adaptive handling of medical content.

# What I Built
A story generator that works with any topic a child might request, but pays special attention to two things:
- Detecting medical themes and adapting the storytelling approach accordingly
- Evaluating every story before it reaches a child, refining until it meets quality standards
THIS IS TO ENSURE stories are appropriate, safe, and effective for their intended purpose.

# My APPROACH
When I thought about bedtime stories, the obvious needs were clear: age-appropriate language, a calming tone, and a complete narrative arc. But that isn't enough.
A story about a dragon learning to fly has only one purpose and that isn't enough. A story about a bunny going to the dentist serves a distinct purpose: mental preparation combined with relaxation.
The question came up: should these be generated in the same way?

# 1. Decision 1: Adaptive Generation
I built an LLM classifier to detect medical themes in story requests. When detected, the system adds specific guidance to the story generation:
These strategies are a part of pediatric coping mechanisms, evidence-based and scientifically proven, so I wanted to introduce them through stories:
- Validate the character's feelings (fear is normal)
- Model concrete coping behaviors (deep breaths, asking questions) or resemble what the character does
- Include a supportive adult (parent, doctor, nurse)
- Show control (character makes choices, isn't passive)
- End with pride in courage, not just relief

# 2. Decision 2: Quality Loop with Clear Standards
Every story goes through an LLM judge that evaluates three dimensions:
- Age Match - Is the vocabulary and complexity right for this child?
- Emotional Safety - Are there scary elements that don't resolve? Anything that might disrupt sleep?
- Bedtime Tone - Does it end calm and complete, or stimulating and open-ended?
The judge returns a score and specific, actionable feedback.
If the score is below 8/10, the system refines the story based on that feedback and re-evaluates. This continues for up to three attempts.
If the system can't reach 8 after three tries, it offers the user a chance to start fresh with a different story idea.

# SYSTEM ARCHITECTURE/ WORKFLOW (ATTACHED)

# MY VERSION 2.0 NEXT STEPS
- Interactive refinement: Let parents request specific changes. "Make it shorter" or "add more about being brave" with context-aware regeneration.
- Story memory: Save successful stories with metadata (theme, age, score, whether refined). Over time, identify patterns.
- Parent guidance: After each story, suggest conversation starters. "You might ask: 'How do you think Bella felt when she first saw the dentist's chair?'" 
  The goal is to CREATE BETTER parent-child connection

## 4 LLM AGENTS:

| Agent | Function Name | What It Does | Makes LLM Call? |
|-------|--------------|--------------|----------------|
| **Agent 1** | `detect_medical_theme()` | Classifies theme | Medical or General
| **Agent 2** | `generate_story()` | Writes story | 
| **Agent 3** | `judge_story()` | Evaluates story | 
| **Agent 4** | `refine_story()` | Improves story | 

## Installation & Usage
### Setup

1. **Install dependencies:**
   pip3 install -r requirements.txt

2. **Set your API key:**
```bash
   export OPENAI_API_KEY="your-api-key-here"
```

3. **Run the program:**
```bash
   python3 main.py
```

