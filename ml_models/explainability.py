"""
Platform-Agnostic Fake Review Detection Web Application
Explainable AI (XAI) Module

Developed for Team: Akshitha, Poojitha, Zeeshan, and Manmath
"""

import re
from typing import Dict, Any

class XAIExplainer:
    """
    Provides visual evidence highlighting specifically for the UI.
    This simulates SHAP/LIME logic where models explain their decisions based
    on specific tokens or features that swayed the outcome.
    """
    def __init__(self):
        # Dictionary of tokens that highly influence the fake classifier locally (LIME style proxy)
        self.suspicious_tokens = {
            "amazing", "perfect", "terrible", "worst", 
            "100%", "guaranteed", "best", "awful", 
            "as an ai", "as an ai language model", "🤖",
            "highly recommend", "do not buy", "scam",
            "miracle", "flawless", "garbage", "waste of money"
        }

    def explain(self, text: str, analysis: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrates Explainable AI reasoning to highlight why it was flagged.
        Handles both full feature sets and 'text_only' modes.
        """
        is_fake = analysis.get("is_fake", False)
        mode = analysis.get("mode", "full")
        
        highlighted_words = []
        if is_fake:
            # Find any suspicious words in the text
            words = set(re.findall(r'\b\w+\b', text.lower()))
            # Also handle multi-word phrases loosely
            phrase_matches = [phrase for phrase in self.suspicious_tokens if phrase in text.lower()]
            highlighted_words = list(words.intersection(self.suspicious_tokens)) + phrase_matches
            # Deduplicate
            highlighted_words = list(set(highlighted_words))
            
            reasons = []
            
            if analysis.get('bert_spam_probability', 0) > 0.7:
                reasons.append("Stylometric evaluation highly matches AI-generated or repetitive generic grammar (BERT).")
                
            if mode != "text_only" and analysis.get('rf_spam_probability', 0) > 0.7:
                rf_reasons = []
                if features.get('punctuation_density', 0) > 0.05:
                     rf_reasons.append("excessive punctuation")
                if features.get('caps_density', 0) > 0.1:
                     rf_reasons.append("excessive ALL CAPS")
                ep = features.get('emotional_polarity_proxy', 0.5)
                if ep > 0.8 or ep < 0.2:
                     rf_reasons.append("extreme emotional polarity")
                if features.get('rating_deviation', 0) > 1.5:
                     rf_reasons.append("highly abnormal rating compared to average")
                     
                if rf_reasons:
                    reasons.append(f"Statistical metadata flagged: {', '.join(rf_reasons)} (Random Forest).")
                    
            rationale = " | ".join(reasons) if reasons else "Contextual model confidence threshold met for deception."
            
        else:
            rationale = "Review exhibits natural language variation and typical metadata patterns."
            if mode == "text_only":
                 rationale = "Linguistically looks genuine. (Note: Behavioral metadata unavailable for pasted text)."
            
        return {
            "suspicious_words_highlighted": highlighted_words,
            "rationale": rationale,
            "feature_contributions": features # Provide raw values to UI for a radar chart or similar
        }
