import os
import openai

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

With more time, I'd add three things:
1. Interactive refinement - let parents say "make it shorter" or "less scary" and regenerate with that context
2. Story memory - save successful stories with their themes so we can learn their patterns over time
3. Parent guidance notes - after each story, suggest conversation starters ("You could ask your child: 'How do you think Bella felt when...'")

My goal is to generate stories,that make bedtime a moment where technology supports human connection
"""

def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    
    openai.api_key = "ADD API KEY"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]


def call_with_system_message(system_msg, user_msg, temperature=0.7, max_tokens=800):
    """
    I am using system messages for better prompt control.
    """
    openai.api_key = "ADD API KEY"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},   #rules for the sytem
            {"role": "user", "content": user_msg} #user msg can change based on request
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message["content"] #extracting the answer 


def detect_medical_theme(request):  
    """
    Plum's theme classifier. Uses an LLM to decide if the child's request contains a medical/health theme.
    - to catch any sort of medical references (e.g., "scared of the white coat")
    - that understands context (e.g., "shot" as vaccine vs. basketball shot)
    - More reliable for kids who experience unusual experiences, make it helpful for pediatric patients
    This LLM acts as a binary classifier and seperates into medical or general theme.
    """
    system_msg = """You are a theme classifier for children's bedtime stories.

    Your job: Determine if a story request involves medical, health, or healthcare themes.
    Medical themes include, but not limited to:
    - Doctor, dentist, hospital, or clinic visits
    - Medical procedures (shots, vaccines, checkups, surgery, x-rays)
    - Illness, injury, or pain
    - Taking medicine or treatment
    - Medical equipment, tools, or settings
    - Health-related fears or anxiety
    - Body health and wellness

    Respond with ONLY one word: MEDICAL or GENERAL

    Some Examples:
    "a bunny scared of the dentist" → MEDICAL
    "a dragon learning to fly" → GENERAL
    "a girl who doesn't like vegetables" → GENERAL (unless it's about health)
    "a boy worried about his doctor visit" → MEDICAL"""

    user_msg = f"""Classify this story request: "{request}"

Is this MEDICAL or GENERAL?"""

    response = call_with_system_message(system_msg, user_msg, temperature=0.2, max_tokens=50)
    
    # Check if response contains "MEDICAL"
    is_medical = "MEDICAL" in response.upper()
    
    return is_medical


def generate_story(request, age, is_medical): 
    """
    Plum's story writer. Turns the child's idea into a gentle, age-appropriate bedtime story.
    The prompt is designed to work for ANY story request - no restrictions.
    """
    # Base storytelling principles for all stories
    system_msg = f"""You are a bedtime storyteller for children around {age} years old.

    Your stories should:
    - Use simple, clear language (similiar to: read-aloud books for young children)
    - Have short sentences that flow naturally and make sense when spoken aloud
    - Be around 300-500 words (keep the length about 3 minutes to read)
    - Follow a gentle arc: comfort, followed by small challenge, the resolution, peaceful and calm ending
    - End peacefully - we want the child ready for sleep, not wound up
    - Work with ANY topic the user requests - be creative and adaptive"""

    # Add medical-specific guidance if needed
    if is_medical:
        system_msg += """

    This story touches on medical or health themes. Important principles to remember and follow :

    EMOTIONAL HONESTY: Don't minimize feelings. If a character is nervous, say so. 
    Make the Kid trust stories that validate to their experience.

    SHOW COPING: Have the character do something - take deep breaths, ask a question,
    hold someone's hand. Give the child watching a model to copy.

    INCLUDE SAFETY: There should be a caring adult (parent, doctor, nurse) who helps.
    Kids should know they won't face scary things alone.

    AGENCY MATTERS: Let the character make choices or ask questions. This helps kids
    feel less powerless about medical experiences. Make the kid feel more in control of his choices.

    END WITH PRIDE: The character should feel proud of their bravery, even if they
    were scared. Show that courage means acting even when you are scared. Have a learning associated with the story.

    KEEP IT GENTLE: Keep medical details simple, calm, and matter-of-fact, never graphic.
    The story should prepare and reassure, not shock or overwhelm.
    """

    user_msg = f"Tell a bedtime story about: {request}"
    
    return call_with_system_message(system_msg, user_msg, temperature=0.7, max_tokens=800)


def judge_story(story, age, is_medical):
    """
    Plum's story judge: checks story safety, tone, and age-fit.
    Returns structured scores + targeted feedback.
    """
    system_msg = """You are a children's story evaluator. Your job is to assess bedtime stories
    for safety and quality before they reach the kid.

    Think like a parent, a teacher, and a child psychologist all at once.
    Be honest but constructive in your evaluation."""

    criteria_text = """
    Evaluate this story on THREE criteria:

    1. AGE MATCH (Is the language and content right for this age?)
    - Too simple or boring
    - Too complex or frustrating or scary
    - Just right but make it engaging but accessible

    2. EMOTIONAL SAFETY (Will this help or hurt bedtime?)
    - no scary images, no unresolved anxiety  
    - helps bedtime, not heightens stress 

    3. BEDTIME TONE (Is this sleep-ready?)
    - avoid high energy, ending should feel calm and complete 
    - Calm, peaceful, complete endings help sleep
    - We want satisfied, not stimulated
    """

    if is_medical:
        criteria_text += """
    Since this story has medical themes, also consider:

    4. EMOTIONAL HONESTY (Does it validate feelings or dismiss them?)
    - "You'll be fine!" = dismissive OR  "It's okay to feel nervous" = validating
    -avoid dismissive tone, be more accepting and validate what they may feel

    5. HELPFUL MODELING (Does it show good coping?)
    - Does the character do something that a real child could try?
    - Deep breaths, questions, asking for help - these are real tools
    """

    user_msg = f"""Story to evaluate (for a {age} year old):

    {story}

    {criteria_text}

    Respond in this EXACT format:
    AGE_MATCH: [score 1-10]
    EMOTIONAL_SAFETY: [score 1-10]
    BEDTIME_TONE: [score 1-10]
    OVERALL: [average score as a number]

    SPECIFIC FEEDBACK: [Tell me 2-3 concrete things - what works well, what doesn't, what to change specifically]
    """

    return call_with_system_message(system_msg, user_msg, temperature=0.2, max_tokens=600)


def parse_score(judge_output):
    """
    Extract the overall score so we can decide whether to refine.
    
    Being defensive here - if parsing fails, you return 7.0 (middle ground)
    so we don't accidentally throw away a good story OR accept a bad one.
    """
    try:
        for line in judge_output.split('\n'):
            line_upper = line.upper()
            if 'OVERALL:' in line_upper or 'OVERALL SCORE:' in line_upper:
                # Handle formats like "OVERALL: 8.5" or "OVERALL: 8.5/10"
                parts = line.split(':')[1].strip()
                # Remove any /10 suffix
                number = parts.split('/')[0].strip()
                return float(number)
    except:
        pass
    return 7.0


def refine_story(original, judge_feedback, age):
    """
    Agent 3 – Plum's story polisher.
    Revises the story using the judge’s feedback while preserving characters and core plot.
    This function gets called in a loop until we reach a score of 8.0 or higher.
    Each iteration should address the specific issues raised by the judge.
    """
    
    system_msg = f"""You are revising a bedtime story for a {age} year old based on specific feedback.

    Fix ONLY what the evaluator flagged, and keep everything that already works.
    Your goal is to make the story safer, calmer, clearer, and more age-appropriate.

    The judge has identified specific issues. When revising:
    - Simplify vocabulary if it's too advanced
    - Soften any frightening or tense moments
    - Calm down endings that feel too exciting
    - Add emotional validation if feelings were ignored
    - Add gentle coping actions (deep breaths, asking questions, holding a hand)
    - Maintain a peaceful, sleep-ready tone throughout
    Give child a story that's both engaging AND safe."""

    user_msg = f"""Original story:
    {original}

    Feedback from evaluator:
    {judge_feedback}

    Rewrite this story to address the specific issues raised in the feedback. 
    Keep the same basic characters and plot idea, but fix the problems mentioned.
    Still aim for 300-500 words and a peaceful, sleep-ready ending."""

    return call_with_system_message(system_msg, user_msg, temperature=0.6, max_tokens=800)


def main():
    """
    Main function with refinement loop until quality score reaches 8.0.
    The system will try up to 3 times to refine the story. If it still can't
    reach a score of 8.0, it offers the user a chance to try a completely
    different story request.
    This approach handles ANY story request - there are no restrictions on topics.
    """
    print("\n" + "="*70)
    print("WELCOME TO LITTLE PLUM 💕: YOUR BEDTIME STORY FRIEND")
    print("="*70)
    print()
    print("I Create age-appropriate bedtime stories for your children")
    print("I can work with any topic - medical, adventure, fantasy, or everyday life.")
    print()
    
    # Get age - this matters for vocabulary and concepts
    while True:
        age_input = input("Child's age (5-10): ").strip()
        try:
            age = int(age_input)
            if 5 <= age <= 10:
                break
            print("Please enter an age between 5 and 10.")
        except ValueError:
            print("Please enter a number.")
    
    # Get the story request - ANY topic is welcome
    print("\nWhat kind of story would you like?")
    print("(I can work with any topic like: animals, space, medical visits, friendship, magic, etc.)")
    print()
    request = input("Your story idea: ").strip()
    
    if not request:
        request = "a small bear learning to be brave"
        print(f"(No input - using default: {request})")
    
    print("\n" + "-"*70)
    
    # Step 1: Classify the theme using LLM
    print("→ Analyzing story theme...")
    is_medical = detect_medical_theme(request)
    
    if is_medical:
        print("→ Medical theme detected - using supportive storytelling approach")
    else:
        print("→ General theme detected - creating gentle, imaginative bedtime story")
    
    # Step 2: Generate the initial story
    print(" Generating story...")
    story = generate_story(request, age, is_medical)
    print(" Initial story created!")
    
    # Step 3: Quality check with refinement loop
    # We keep refining until we hit a score of 8.0 or higher
    # Maximum 3 attempts to avoid taking too long
    print("\n→ Running quality and safety evaluation...")
    
    MAX_ATTEMPTS = 3
    attempt = 1
    score = 0.0
    feedback = ""
    
    while attempt <= MAX_ATTEMPTS:
        print(f" Evaluation attempt {attempt}...")
        feedback = judge_story(story, age, is_medical)
        score = parse_score(feedback)
        
        print(f"   Quality score: {score}/10")
        
        # If we've reached our target score, we're done!
        if score >= 8.0:
            print("    Quality standard met!")
            break
        
        # If we haven't maxed out attempts, refine the story
        if attempt < MAX_ATTEMPTS:
            print(f"    Score below 8.0 - refining based on feedback...")
            story = refine_story(story, feedback, age)
        
        attempt += 1
    
    # If we couldn't reach 8.0 after max attempts, offer to try a different approach
    if score < 8.0:
        print("\n" + "!"*70)
        print("I'm having trouble getting this particular story just right.")
        print(f"Current score: {score}/10 (target: 8.0/10)")
        print()
        print("Would you like to try a different story idea?")
        print("Sometimes a slight change in approach helps!")
        print()
        
        try_again = input("Start over with a new story idea? (y/n): ").strip().lower()
        if try_again == 'y':
            print("\nLet's try again with a fresh start!\n")
            return main()  # Recursive call to start over
        else:
            print("\nOkay! Here's the best version I created:")
    
    # Output the final story
    print("\n" + "="*70)
    print("YOUR BEDTIME STORY")
    print("="*70)
    print()
    print(story)
    print()
    print("="*70)
    print(f"Final quality score: {score}/10")
    print("="*70)
    print("\nSweet dreams, Little Plum! 🌙")
    print()
    
    # Show detailed evaluation feedback - Good if I try to involve Parents for the next 2 hours
    show_feedback = input("Want to see the detailed quality evaluation? (y/n): ").strip().lower()
    if show_feedback == 'y':
        print("\n" + "-"*70)
        print("DETAILED QUALITY EVALUATION")
        print("-"*70)
        print(feedback)
        print("-"*70)
        print()


if __name__ == "__main__":
    main()