import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
print(f"Testing key: ...{key[-4:]}")

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello")
    print("API SUCCESS:", response.text)
except Exception as e:
    print("API FAILURE:", e)
