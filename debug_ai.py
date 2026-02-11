import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

query = "iPhone 15"
prompt = f"""
Act as CartScribe AI. 
User input: "{query}"
Suggest a product based on this query.

Generate a detailed JSON response:
1. "name": Specific product name.
2. "description": A short premium summary.
3. "category": Broad category name.
4. "specifications": Array of 4 technical specs.
5. "features": Array of 3-4 key features or "whats in the box".
6. "uses": Array of 2-3 primary use cases for this product.
7. "rating_value": Overall rating (e.g. "4.2"). If unknown, suggest a realistic market rating.
8. "rating_count": Number of people who rated it (e.g. "15,230").
9. "platforms": Array of 4 objects with "name", "price" (INR), and "deal".

Return ONLY valid JSON.
"""

try:
    response = model.generate_content(prompt)
    print("AI RAW OUTPUT:", response.text)
    content = response.text.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    data = json.loads(content)
    print("PARSED SUCCESS:", json.dumps(data, indent=2))
except Exception as e:
    print("ERROR:", e)
