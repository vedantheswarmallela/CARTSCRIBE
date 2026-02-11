import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

query = "Nike Air Max"
prompt = f"""
Act as CartScribe AI Expert. 
User input: "{query}"
Find and analyze the best version of this product.

Provide a comprehensive JSON response:
{{
    "name": "Full Commercial Product Name",
    "description": "3-sentence premium marketing summary.",
    "category": "Broad category",
    "specifications": ["Spec 1", "Spec 2", "Spec 3", "Spec 4"],
    "features": ["Feature 1", "Feature 2", "Feature 3"],
    "uses": ["Use 1", "Use 2"],
    "rating_value": "4.2",
    "rating_count": "1,250+",
    "image_keywords": "brand,model,color,product",
    "platforms": [
        {{"name": "Amazon", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available"}},
        {{"name": "Flipkart", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available"}},
        {{"name": "Myntra", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available"}},
        {{"name": "Meesho", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available"}},
        {{"name": "Ajio", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available"}}
    ]
}}

Important: If a product is NOT available on a specific platform, set its "price" and "deal" to EXACTLY "Not Available".
Return ONLY valid JSON.
"""

response = model.generate_content(prompt)
print(response.text)
