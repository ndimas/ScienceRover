import os

# Groq API configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # Initial delay in seconds
