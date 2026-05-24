from google import genai
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API key not found")
    exit()

# Create Gemini client
client = genai.Client(api_key=api_key)

# Generate response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello to Ram and motivate him for his AI journey."
)

print(response.text)