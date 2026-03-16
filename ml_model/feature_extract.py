import re
from typing import Dict, Any, List

def extract_linguistic_features(text: str) -> Dict[str, float]:
    """
    Extracts surface-level linguistic features: Punctuation abuse, ALL CAPS, etc.
    A full implementation might use VADER or TextBlob for emotional polarity.
    For this prototype, we use simple rule-based heuristics to emulate it.
    """
    if not text:
        return {
            "punctuation_density": 0.0,
            "caps_density": 0.0,
            "length": 0,
            "emotional_polarity_proxy": 0.5
        }
        
    length = len(text)
    
    # Punctuation abuse: frequent '!!!!', '???', '...'
    punctuation_count = len(re.findall(r'[!?.]', text))
    punctuation_density = punctuation_count / length if length > 0 else 0
    
    # ALL CAPS density
    caps_count = sum(1 for c in text if c.isupper())
    caps_density = caps_count / length if length > 0 else 0
    
    # Extremely basic emotional polarity proxy based on word counting
    # (In a real scenario, use VADER/TextBlob)
    positive_words = {'excellent', 'amazing', 'perfect', 'best', 'love', 'great'}
    negative_words = {'terrible', 'worst', 'awful', 'hate', 'bad', 'horrible'}
    
    words = set(re.findall(r'\w+', text.lower()))
    pos_count = len(words.intersection(positive_words))
    neg_count = len(words.intersection(negative_words))
    
    # Proxy score between 0 and 1, where 1 is highly extreme polarity (suspicious)
    # and 0 is neutral. Deceptive opinion spam often has extreme polarity.
    emotional_polarity_proxy = 0.5
    if pos_count > neg_count and pos_count > 0:
        emotional_polarity_proxy = min(1.0, 0.5 + (pos_count * 0.1))
    elif neg_count > pos_count and neg_count > 0:
        emotional_polarity_proxy = max(0.0, 0.5 - (neg_count * 0.1))

    return {
        "punctuation_density": punctuation_density,
        "caps_density": caps_density,
        "length": length,
        "emotional_polarity_proxy": emotional_polarity_proxy
    }

def extract_behavioral_features(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract Behavioral Features like 'Burstiness' (high-frequency posting) and Rating Deviation.
    Normally, this would require analyzing a specific user's history or timestamp density.
    Here we append standard metadata proxies to each review.
    """
    if not reviews:
        return []

    # Try mapping ratings to float for average calculations
    ratings = []
    for r in reviews:
        try:
            # Very naïve rating extraction (e.g. from "5 stars" -> 5.0)
            if r.get("rating_raw"):
                match = re.search(r'\d+', str(r["rating_raw"]))
                if match:
                    ratings.append(float(match.group()))
        except Exception:
            pass

    avg_rating = sum(ratings) / len(ratings) if ratings else 3.0

    for review in reviews:
        # Punctuation/Linguistic features
        ling_features = extract_linguistic_features(review.get('text', ''))
        
        # Rating deviation (difference from average)
        review_rating = 3.0
        try:
            if review.get("rating_raw"):
                match = re.search(r'\d+', str(review["rating_raw"]))
                if match:
                    review_rating = float(match.group())
        except Exception:
            pass
            
        rating_deviation = abs(review_rating - avg_rating)
        
        # In a full App, we'd calculate "Burstiness" by looking at clustering of timestamps,
        # but here we'll just mock it and pack it all in.
        
        review["features"] = {
            **ling_features,
            "rating_deviation": rating_deviation,
            "burstiness_proxy": 0.1 # Placeholder: requires timeframe matching
        }
        
    return reviews
