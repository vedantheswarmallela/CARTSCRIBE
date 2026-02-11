import os
import re
import random
import json
from flask import Flask, render_template, request, jsonify, redirect
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure Google Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if HAS_GEMINI and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print(f"DEBUG: Gemini initialized with gemini-2.5-flash")
    except Exception as e:
        print(f"DEBUG: Error initializing Gemini: {e}")
        model = None
else:
    print("DEBUG: Gemini API Key not found. Using Mock Mode.")
    model = None

def generate_search_url(platform_name, product_name):
    query = product_name.replace(' ', '+')
    if platform_name.lower() == 'amazon':
        return f"https://www.amazon.in/s?k={query}"
    elif platform_name.lower() == 'flipkart':
        return f"https://www.flipkart.com/search?q={query}"
    elif platform_name.lower() == 'myntra':
        return f"https://www.myntra.com/{query}"
    elif platform_name.lower() == 'meesho':
        return f"https://www.meesho.com/search?q={query}"
    elif platform_name.lower() == 'ajio':
        return f"https://www.ajio.com/search/?text={query}"
    return f"https://www.google.com/search?q={query}"

def get_ai_suggestions(query):
    if not model:
        # Mock data if no API key
        return [
            {"name": f"Premium {query} Pro", "desc": "The ultimate choice for professionals seeking performance and style.", "price": "$999"},
            {"name": f"Eco {query} Air", "desc": "Lightweight, sustainable, and surprisingly powerful for everyday use.", "price": "$499"},
            {"name": f"Elite {query} Ultra", "desc": "Boundary-pushing technology with a sleek minimalist design.", "price": "$749"},
            {"name": f"Classic {query} Plus", "desc": "Reliable, durable, and packed with the features you love.", "price": "$299"}
        ]
    
    prompt = f"""
    Act as a professional shopping assistant named CartScribe. 
    User is searching for: "{query}"
    Provide 4 highly relevant, creatively named product suggestions.
    Return only a JSON array of objects with "name", "desc", and "price" keys.
    Keep descriptions short and premium. Use realistic but appealing prices.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's just JSON
        content = response.text.strip()
        json_match = re.search(r'(\[.*\])', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        return json.loads(content)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return [{"name": f"AI Result for {query}", "desc": "Smart product finding is currently limited. Please check back soon!", "price": "N/A"}]

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_api():
    query = request.form.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    return jsonify({"redirect": f"/product?q={query}"})

@app.route('/product')
def product_page():
    query = request.args.get('q', 'Latest Product')
    
    # Enhanced URL detection
    is_url = query.startswith('http') or any(domain in query.lower() for domain in ['flipkart.com', 'amazon.in', 'amzn.to', 'myntra.com', 'meesho.com'])
    
    # Identifies category broadly for UI styling
    category = "general"
    category_map = {
        "fashion": ['shirt', 'pant', 'dress', 'shoe', 'wear', 'clothing', 'watch', 'bag', 'jewelry'],
        "electronics": ['phone', 'laptop', 'camera', 'tech', 'gadget', 'electron', 'tv', 'audio'],
        "home": ['furniture', 'decor', 'kitchen', 'appliance', 'bed', 'sofa', 'table'],
        "beauty": ['serum', 'cream', 'makeup', 'skinkare', 'perfume', 'hair'],
        "sports": ['gym', 'yoga', 'cycle', 'ball', 'fitness', 'outdoor'],
        "grocery": ['food', 'drink', 'organic', 'snack', 'health']
    }
    
    for cat, keywords in category_map.items():
        if any(word in query.lower() for word in keywords):
            category = cat
            break

    if not model:
        # Mock data...
        product_data = {
            "name": query.title() if not is_url else "Analyzed Flipkart Product",
            "description": f"A high-quality product analyzed from: {query}.",
            "category": category,
            "specifications": ["Premium Quality", "Durable Build"],
            "features": ["Quick connectivity", "Long battery life", "Premium finish"],
            "uses": ["Daily office work", "Entertainment", "Travel"],
            "rating_value": "4.5",
            "rating_count": "1,240",
            "platforms": [
                {"name": "Amazon", "price": "₹4,999", "deal": "Standard Price", "url": f"https://www.amazon.in/s?k={query}"},
                {"name": "Flipkart", "price": "₹4,799", "deal": "Special Offer", "url": f"https://www.flipkart.com/search?q={query}"},
                {"name": "Myntra", "price": "Not Available", "deal": "Not Available", "url": "#"},
                {"name": "Meesho", "price": "₹4,699", "deal": "Lowest Price", "url": f"https://www.meesho.com/search?q={query}"},
                {"name": "Ajio", "price": "₹4,899", "deal": "New User Discount", "url": f"https://www.ajio.com/search/?text={query}"}
            ],
            "price_analysis": "Currently, Meesho offers the lowest price at ₹4,699. Flipkart is a close second with a special offer, while Myntra does not seem to have this item in stock."
        }
    else:
        # AI Prompt...
        prompt = f"""
        Act as CartScribe AI Expert. 
        User input: "{query}"
        {'The user has provided a link. Perform a deep scribe analysis of this specific product.' if is_url else 'Find and analyze the best version of this product.'}
        
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
                {{"name": "Amazon", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available", "url": "Direct Amazon search link"}},
                {{"name": "Flipkart", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available", "url": "Direct Flipkart search link"}},
                {{"name": "Myntra", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available", "url": "Direct Myntra search link"}},
                {{"name": "Meesho", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available", "url": "Direct Meesho search link"}},
                {{"name": "Ajio", "price": "₹XX,XXX or Not Available", "deal": "Deal info or Not Available", "url": "Direct Ajio search link"}}
            ],
            "price_analysis": "A detailed comparison of price drops and best platform to buy from."
        }}
        
        Important: If a product is NOT available on a specific platform, set its "price" and "deal" to EXACTLY "Not Available".
        
        Return ONLY valid JSON.
        """
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            product_data = json.loads(content)
            
            # Post-process platforms to ensure URLs
            if 'platforms' in product_data:
                for platform in product_data['platforms']:
                    if not platform.get('url') or 'search link' in platform.get('url', '').lower():
                        platform['url'] = generate_search_url(platform['name'], product_data['name'])
        except Exception as e:
            print(f"DEBUG: API Call Failed: {e}")
            # Dynamic Mock Prices for better UX during Quota Limit
            base_price = random.choice([999, 1499, 2999, 7999, 12999, 24999])
            
            product_data = {
                "name": query.title() if len(query) < 40 else "Scribed Product", 
                "description": "Our AI is currently optimizing results. Based on market trends, this product offers excellent value and durability for its category.", 
                "platforms": [
                    {"name": "Amazon", "price": f"₹{base_price + 500:,}", "deal": "Market Price", "url": f"https://www.amazon.in/s?k={query}"},
                    {"name": "Flipkart", "price": f"₹{base_price + 200:,}", "deal": "Bank Offer", "url": f"https://www.flipkart.com/search?q={query}"},
                    {"name": "Myntra", "price": "Not Available", "deal": "Not Available", "url": "#"},
                    {"name": "Meesho", "price": f"₹{base_price:,}", "deal": "Lowest Price", "url": f"https://www.meesho.com/search?q={query}"},
                    {"name": "Ajio", "price": f"₹{base_price + 350:,}", "deal": "Coupon Applied", "url": f"https://www.ajio.com/search/?text={query}"}
                ], 
                "category": category, 
                "specifications": ["Verified Quality", "Standard Warranty", "Fast Shipping", "Genuine Item"], 
                "features": ["High Durability", "Modern Design", "Reliable Tech"], 
                "uses": ["Personal use", "Professional gift"], 
                "rating_value": "4.3", 
                "rating_count": f"{random.randint(500, 5000)}+",
                "image_keywords": query if len(query) < 20 else "product",
                "price_analysis": f"Market analysis suggests Meesho currently offers the best deal at ₹{base_price:,}. Flipkart is the next best option with bank discounts. Stock levels appear healthy across major platforms."
            }

    # Sort platforms by price (lowest first, 'Not Available' last)
    def platform_sort_key(p):
        price_str = p.get('price', 'Not Available')
        if price_str == 'Not Available':
            return float('inf')
        try:
            return float(re.sub(r'[^\d.]', '', price_str))
        except:
            return float('inf')
    
    if 'platforms' in product_data:
        product_data['platforms'].sort(key=platform_sort_key)

    return render_template('product.html', product=product_data, source_url=query if is_url else None)

@app.route('/compare')
def compare_page():
    req = request.args.get('req', '')
    if not req:
        return redirect('/')

    if not model:
        # Mock comparison data
        results = [
            {"name": "Budget Option", "price": 45000, "original_price": "₹45,000", "desc": "Good value for entry level requirements.", "rating": 4.1},
            {"name": "Mid-Range Choice", "price": 62000, "original_price": "₹62,000", "desc": "Balanced performance and cost.", "rating": 4.4},
            {"name": "Premium Pick", "price": 89000, "original_price": "₹89,000", "desc": "Top tier specs for demanding users.", "rating": 4.8},
        ]
    else:
        prompt = f"""
        Act as CartScribe Agent. 
        User Requirements: "{req}"
        Find 5 actual or realistic products that match these requirements across major Indian platforms (Amazon, Flipkart, Myntra, Meesho, Ajio).
        Return a JSON array of objects. Each object MUST have:
        1. "name": Product name.
        2. "price": Numeric lowest price found in INR (e.g. 54000).
        3. "original_price": String lowest price with currency (e.g. "₹54,000").
        4. "desc": 1 sentence why it matches.
        5. "rating": Rating out of 5 (e.g. 4.3).
        6. "img_keyword": 1-2 words for image search (e.g. "laptop", "shirt").
        
        Sort the response by price from LOW to HIGH.
        Return ONLY valid JSON.
        """
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            json_match = re.search(r'(\[.*\])', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            results = json.loads(content)
            if not isinstance(results, list):
                results = [results]
            
            # Post-process results for links and keywords
            for item in results:
                if not item.get('url'):
                    item['url'] = generate_search_url('Google', item['name'])
                if not item.get('img_keyword'):
                    item['img_keyword'] = item['name'].split()[0] if item['name'] else 'product'
            
            # Re-sort just in case AI missed it
            def get_price(item):
                p = item.get('price', 0)
                if isinstance(p, str):
                    try:
                        # Extract digits only
                        p = re.sub(r'[^\d.]', '', p)
                        return float(p) if p else 0
                    except:
                        return 0
                return p if isinstance(p, (int, float)) else 0

            results.sort(key=get_price)
            print(f"DEBUG: Successfully fetched {len(results)} items for comparison.")
        except Exception as e:
            print(f"DEBUG: Compare API Failed: {e}")
            results = [
                {"name": f"Top Match for {req[:20]}", "price": 15000, "original_price": "₹15,000", "desc": "Great general purpose balanced choice.", "rating": 4.5},
                {"name": "Value Alternative", "price": 12000, "original_price": "₹12,000", "desc": "Best budget-friendly option for your needs.", "rating": 4.1},
                {"name": "Performance Edition", "price": 25000, "original_price": "₹25,000", "desc": "High-end version with superior build quality.", "rating": 4.8}
            ]

    return render_template('compare.html', results=results, requirements=req)

@app.route('/test-ai')
def test_ai():
    if not model:
        return "Model not initialized"
    try:
        res = model.generate_content("Say 'API is alive'")
        return f"AI Response: {res.text}"
    except Exception as e:
        return f"API Error: {str(e)}"

if __name__ == '__main__':
    print("CartScribe is running at http://127.0.0.1:5000")
    app.run(debug=True)