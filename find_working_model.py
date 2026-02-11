import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

for m_name in models_to_test:
    print(f"Testing {m_name}...")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content("Hi")
        print(f"  SUCCESS: {response.text[:20]}...")
    except Exception as e:
        print(f"  FAILED: {str(e)[:100]}")
