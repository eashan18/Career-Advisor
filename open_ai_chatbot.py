import requests
import json

# API details
API_KEY = "API KEY"  
API_URL = "https://api.groq.com/openai/v1/chat/completions"  

# Function schema for career info extraction
functions = [
    {
        "name": "log_career_info",
        "description": "Extract user's career preferences and skills",
        "parameters": {
            "type": "object",
            "properties": {
                "skills": {"type": "array", "items": {"type": "string"}},
                "career_goal": {"type": "string"},
                "experience_level": {"type": "string"},
                "preferred_industry": {"type": "string"},
                "preferred_location": {"type": "string"}
            },
            "required": ["skills", "career_goal", "experience_level", "preferred_location"]
        }
    }
]

# Function to extract career info using LLaMA 3
def extract_career_info(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",  
        "messages": [
            {"role": "system", "content": "You are a helpful AI career advisor that extracts a user's skills, career goals, experience level, preferred industry, and preferred location from their input."},
            {"role": "user", "content": user_input}
        ],
        "functions": functions,
        "function_call": {"name": "log_career_info"},  
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()

    arguments = response.json()["choices"][0]["message"]["function_call"]["arguments"]
    return json.loads(arguments)
