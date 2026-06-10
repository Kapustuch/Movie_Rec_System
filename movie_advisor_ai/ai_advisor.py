import os
from openai import OpenAI
from dotenv import load_dotenv
from database import init_db, get_cached_recommendation, save_to_cache

# Load environment variables from the .env configuration file (API keys, tokens)
load_dotenv()

# Primary database structure initialization (creates tables if they do not exist)
init_db()

def get_movie_recommendation(movie_name, age_group="adult", interest="general", force_refresh=False):
    """
    Generates a personalized movie description using AI.
    Takes into account the target age group (persona) and user interests.
    The force_refresh parameter allows bypassing the cache for forced regeneration.
    """
    
    # Check for an existing description in the local database cache.
    # If forced refresh is disabled, return the previously saved result.
    if not force_refresh:
        cached_result = get_cached_recommendation(movie_name, age_group, interest)
        if cached_result:
            return cached_result
    
    # System role templates (system prompts) depending on the client's age category
    age_personas = {
        "teen": "You are a dynamic youth blogger, speaking in slang, full of energy.",
        "adult": "You are a reserved movie critic, focusing on ideas and plot quality.",
        "senior": "You are a wise viewer, appreciating classics, emotional depth, and details."
    }

    # Definition of the semantic focus for text generation according to user preferences
    interest_focus = {
        "action": "emphasize dynamics, epic scenes, and pure drive.",
        "drama": "emphasize the internal conflicts of the characters and their emotions.",
        "general": "describe the general atmosphere and interesting facts about the movie."
    }

    # Safely retrieving prompt configurations with default values in case of incorrect arguments
    persona = age_personas.get(age_group, age_personas['adult'])
    focus = interest_focus.get(interest, interest_focus['general'])
    
    # Combining style and focus into a single main system instruction for the AI
    system_instruction = f"{persona} {focus}"

    try:
        # Initializing the OpenAI client to interact with the Hugging Face API via a compatible router
        client = OpenAI(
            base_url="https://router.huggingface.co/v1/", 
            api_key=os.getenv("HF_TOKEN")
        )

        # Sending a request to the deployed Llama 3 model, passing context and generation rules
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            messages=[
                {
                    "role": "system", 
                    "content": f"""{system_instruction}
                    Your task is to provide an engaging summary of the plot.
                    RULES:
                    1. CHECK CHARACTER NAMES: the main character of 'The Maze Runner' is Thomas, 'Interstellar' is Cooper.
                    2. Do not invent magic or new characters.
                    3. Write exactly 3-4 complete sentences.
                    4. AVOID TEMPLATES: do not write 'This movie is about...', start directly with the core substance.
                    5. ПИШИ ВИКЛЮЧНО УКРАЇНСЬКОЮ МОВОЮ."""
                },
                {
                    "role": "user", 
                    "content": f"Describe the setup of the plot for the movie '{movie_name}' to make people want to watch it. Be original."
                }
            ],
            max_tokens=300,  # Optimal limit on output tokens to control text length
            temperature=0.1  # Low randomness for stable and consistent results
        )
        
        # Validation and cleaning of the text content received from the model
        content = response.choices[0].message.content.strip()
        clean_content = content.strip(' "') # Removing accidental quotation marks from the edges of the string
        
        # Updating the local database cache with the newly generated text
        save_to_cache(movie_name, age_group, interest, clean_content)
        
        return clean_content

    except Exception as e:
        # Handling exceptions (network issues, API limits) to prevent the web app from crashing
        print(f"AI Model or API Error: {e}")
        
        # Returning a pre-configured default text (fallback) in case of a generation server failure
        return f"Check out {movie_name}, it is a wonderful choice for your evening."