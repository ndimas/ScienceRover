import os
from groq import Groq
import time
from config import MAX_RETRIES, RETRY_DELAY

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

def make_api_call(prompt):
    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{'role': 'user', 'content': prompt}],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )

            response = ''
            for chunk in completion:
                response += chunk.choices[0].delta.content or ''

            return response
        
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                return f"Error in API call: {str(e)}"
            else:
                print(f"Attempt {attempt + 1} failed. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff

    return "Error: Max retries reached for API call"
