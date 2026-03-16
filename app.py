import asyncio
from flask import Flask, request, jsonify, render_template

# Try to import scraper safely
try:
    from scraper import GhostScraper
except ImportError:
    GhostScraper = None

from ml_models.feature_extract import extract_behavioral_features
from ml_models.hybrid_model import HybridModelSystem
from ml_models.explainability import XAIExplainer

app = Flask(__name__)

ml_system = HybridModelSystem()
xai_explainer = XAIExplainer()


# --- Routes ---

@app.route("/", methods=["GET"])
def index():
    """Render the main web interface."""
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Endpoint that accepts a URL, scrapes reviews, extracts features,
    runs the ML models, and returns explainable trust scores.
    """
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL parameter is required."}), 400
        
    # Clean URL in case users accidentally copy-paste trailing punctuation (like parenthesis or quotes)
    url = url.strip(")'\"] ")
        
    if GhostScraper is None:
        return jsonify({"error": "GhostScraper module is not loaded correctly."}), 500

    # 1. Data Acquisition
    try:
        # Use asyncio.run directly - it creates a brand new isolated loop thread-safely
        # and cleans up perfectly, preventing Werkzeug Flask thread collisions.
        async def run_scraper():
            scraper = GhostScraper(headless=True)
            return await scraper.scrape_url(url)
            
        reviews = asyncio.run(run_scraper())
    except Exception as e:
        print(f"Scraper thread crash: {e}")
        error_msg = str(e)
        if "WAF_BLOCK" in error_msg:
            return jsonify({"error": "WAF_BLOCK", "message": "Enterprise Firewall (Datadome/Akamai) actively intercepted the scraper. Bypassing requires a residential proxy network."}), 403
        return jsonify({"error": f"Scraping failed: {e}", "url": url}), 500
        
    if not reviews:
        return jsonify({"message": "No reviews found or failed to scrape.", "url": url}), 404

    # 2. Extract Behavioral & Linguistic Features for the entire batch
    processed_reviews = extract_behavioral_features(reviews)

    # 3 & 4. Feature Extraction, Machine Learning, and XAI Loop
    results = []
    for review in processed_reviews:
        text = review.get("text", "")
        if not text:
            continue
            
        features = review.get("features", {})
        ml_prediction = ml_system.evaluate(text, features)
        xai_evidence = xai_explainer.explain(text, ml_prediction, features)
        
        result_item = {
            "review_id": review.get("id"),
            "original_text": text,
            "metadata": {
                "rating": review.get("rating_raw"),
                "timestamp": review.get("timestamp")
            },
            "analysis": ml_prediction,
            "explainable_evidence": xai_evidence
        }
        results.append(result_item)
        
    return jsonify({
        "source_url": url,
        "total_analyzed": len(results),
        "results": results
    })

@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """
    Endpoint that accepts raw text, runs the ML models in text-only mode,
    and returns explainable trust scores.
    """
    data = request.json
    text = data.get("text")
    
    if not text:
        return jsonify({"error": "Text parameter is required."}), 400
        
    # ML Logic for Text-Only Mode
    ml_prediction = ml_system.evaluate_text_only(text)
    
    # XAI evidence
    xai_evidence = xai_explainer.explain(text, ml_prediction, {})
    
    result_item = {
        "review_id": "manual_0",
        "original_text": text,
        "metadata": {
            "rating": "N/A",
            "timestamp": "Manual Input"
        },
        "analysis": ml_prediction,
        "explainable_evidence": xai_evidence
    }
    
    return jsonify({
        "source": "manual_text",
        "total_analyzed": 1,
        "results": [result_item]
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
