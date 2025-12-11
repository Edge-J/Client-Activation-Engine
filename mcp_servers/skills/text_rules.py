"""
Text processing rules and utilities.

This module provides rule-based text processing capabilities
for pattern matching, extraction, and transformation.
"""

import logging
import re
from typing import Any, Union, Optional, Pattern
from collections import defaultdict

logger = logging.getLogger(__name__)

# Common text patterns
BUSINESS_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"),
    "url": re.compile(r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?"),
    "currency": re.compile(r"\$[\d,]+\.?\d*|\b\d+\.\d{2}\b"),
    "date": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b"),
    "time": re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "zip_code": re.compile(r"\b\d{5}(?:-\d{4})?\b"),
}

# Business-specific vocabulary
BUSINESS_VOCABULARIES = {
    "healthcare": {
        "positive": ["patient", "treatment", "diagnosis", "medical", "health", "care", "therapy", "medication"],
        "negative": ["violation", "malpractice", "error", "neglect", "lawsuit"],
        "entities": ["hospital", "clinic", "physician", "nurse", "EMR", "HIPAA"],
    },
    "fintech": {
        "positive": ["payment", "transaction", "account", "balance", "investment", "portfolio", "profit"],
        "negative": ["fraud", "loss", "decline", "chargeback", "default", "risk"],
        "entities": ["bank", "credit", "debit", "ACH", "wire", "SEC", "FDIC"],
    },
    "ecommerce": {
        "positive": ["purchase", "order", "product", "customer", "sale", "revenue", "conversion"],
        "negative": ["refund", "return", "complaint", "abandoned", "cancelled"],
        "entities": ["cart", "checkout", "inventory", "shipping", "SKU", "PCI"],
    },
    "education": {
        "positive": ["student", "learning", "course", "education", "achievement", "progress", "grade"],
        "negative": ["failure", "dropout", "violation", "misconduct"],
        "entities": ["school", "university", "teacher", "curriculum", "FERPA"],
    },
}

# Content classification rules
CONTENT_CLASSIFIERS = {
    "priority": {
        "urgent": ["urgent", "asap", "immediate", "emergency", "critical", "now"],
        "high": ["important", "priority", "soon", "quickly", "deadline"],
        "medium": ["normal", "regular", "standard", "when possible"],
        "low": ["later", "eventually", "low priority", "whenever"],
    },
    "sentiment": {
        "positive": ["good", "great", "excellent", "happy", "satisfied", "pleased", "love"],
        "negative": ["bad", "terrible", "awful", "unhappy", "disappointed", "hate", "angry"],
        "neutral": ["okay", "fine", "average", "normal", "standard"],
    },
    "intent": {
        "request": ["need", "want", "require", "request", "asking", "looking for"],
        "complaint": ["problem", "issue", "wrong", "error", "broken", "not working"],
        "question": ["how", "what", "when", "where", "why", "who", "?"],
        "information": ["tell", "explain", "describe", "inform", "details"],
    },
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the text rules utilities."""
    return {
        "name": "text_rules",
        "description": "Text processing rules and pattern matching utilities",
        "version": "1.0.0",
        "category": "skills",
        "functions": [
            "extract_patterns",
            "classify_content",
            "match_business_terms",
            "clean_and_normalize",
            "extract_entities",
            "score_relevance",
        ],
    }


def extract_patterns(text: str, pattern_types: Optional[list[str]] = None) -> dict[str, list[str]]:
    """
    Extract common patterns from text.
    
    Args:
        text: Input text to analyze
        pattern_types: List of pattern types to extract (default: all)
        
    Returns:
        Dictionary of extracted patterns by type
    """
    if not isinstance(text, str):
        return {}
    
    if pattern_types is None:
        pattern_types = list(BUSINESS_PATTERNS.keys())
    
    results = {}
    
    for pattern_type in pattern_types:
        if pattern_type in BUSINESS_PATTERNS:
            pattern = BUSINESS_PATTERNS[pattern_type]
            matches = pattern.findall(text)
            
            # Handle different match types
            if pattern_type == "phone":
                # Phone pattern returns tuples
                results[pattern_type] = [f"({match[0]}) {match[1]}-{match[2]}" for match in matches if len(match) == 3]
            else:
                results[pattern_type] = matches
        else:
            results[pattern_type] = []
    
    return results


def classify_content(text: str, classification_type: str = "all") -> dict[str, Any]:
    """
    Classify text content based on predefined rules.
    
    Args:
        text: Input text to classify
        classification_type: Type of classification ("priority", "sentiment", "intent", "all")
        
    Returns:
        Classification results with scores
    """
    if not isinstance(text, str):
        return {}
    
    text_lower = text.lower()
    results = {}
    
    classification_types = [classification_type] if classification_type != "all" else list(CONTENT_CLASSIFIERS.keys())
    
    for cls_type in classification_types:
        if cls_type not in CONTENT_CLASSIFIERS:
            continue
            
        scores = {}
        rules = CONTENT_CLASSIFIERS[cls_type]
        
        for category, keywords in rules.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                # Count occurrences with word boundaries
                pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
                matches = len(pattern.findall(text))
                if matches > 0:
                    score += matches
                    matched_keywords.append(keyword)
            
            scores[category] = {
                "score": score,
                "matched_keywords": matched_keywords,
            }
        
        # Determine top classification
        top_category = max(scores.keys(), key=lambda k: scores[k]["score"])
        confidence = _calculate_confidence(scores, top_category)
        
        results[cls_type] = {
            "classification": top_category if scores[top_category]["score"] > 0 else "unknown",
            "confidence": confidence,
            "all_scores": scores,
        }
    
    return results


def match_business_terms(text: str, business_type: str) -> dict[str, Any]:
    """
    Match business-specific terminology in text.
    
    Args:
        text: Input text to analyze
        business_type: Type of business vocabulary to use
        
    Returns:
        Matched terms and relevance scores
    """
    if not isinstance(text, str) or business_type not in BUSINESS_VOCABULARIES:
        return {"matches": {}, "relevance_score": 0.0, "business_type": business_type}
    
    text_lower = text.lower()
    vocabulary = BUSINESS_VOCABULARIES[business_type]
    matches = {}
    total_matches = 0
    
    for category, terms in vocabulary.items():
        category_matches = []
        
        for term in terms:
            pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            term_matches = pattern.findall(text)
            
            if term_matches:
                category_matches.extend(term_matches)
                total_matches += len(term_matches)
        
        matches[category] = list(set(category_matches))  # Remove duplicates
    
    # Calculate relevance score
    word_count = len(text.split())
    relevance_score = min(total_matches / max(word_count, 1), 1.0) if word_count > 0 else 0.0
    
    return {
        "matches": matches,
        "relevance_score": relevance_score,
        "business_type": business_type,
        "total_matches": total_matches,
    }


def clean_and_normalize(text: str, options: Optional[dict[str, Any]] = None) -> str:
    """
    Clean and normalize text using rule-based processing.
    
    Args:
        text: Input text to clean
        options: Cleaning options
        
    Returns:
        Cleaned and normalized text
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    if options is None:
        options = {}
    
    cleaned = text
    
    # Remove extra whitespace
    if options.get("normalize_whitespace", True):
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.strip()
    
    # Remove special characters
    if options.get("remove_special_chars", False):
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
    
    # Normalize case
    case_option = options.get("case", "preserve")
    if case_option == "lower":
        cleaned = cleaned.lower()
    elif case_option == "upper":
        cleaned = cleaned.upper()
    elif case_option == "title":
        cleaned = cleaned.title()
    
    # Remove HTML tags
    if options.get("remove_html", False):
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
    
    # Remove URLs
    if options.get("remove_urls", False):
        cleaned = re.sub(BUSINESS_PATTERNS["url"], "", cleaned)
    
    # Remove email addresses
    if options.get("remove_emails", False):
        cleaned = re.sub(BUSINESS_PATTERNS["email"], "", cleaned)
    
    # Final cleanup
    if options.get("normalize_whitespace", True):
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned


def extract_entities(text: str, entity_types: Optional[list[str]] = None) -> dict[str, list[str]]:
    """
    Extract named entities using rule-based patterns.
    
    Args:
        text: Input text to analyze
        entity_types: Types of entities to extract
        
    Returns:
        Extracted entities by type
    """
    if not isinstance(text, str):
        return {}
    
    entities = defaultdict(list)
    
    # Extract contact information
    if not entity_types or "contact" in entity_types:
        emails = BUSINESS_PATTERNS["email"].findall(text)
        phones = extract_patterns(text, ["phone"])["phone"]
        
        entities["email"].extend(emails)
        entities["phone"].extend(phones)
    
    # Extract financial information
    if not entity_types or "financial" in entity_types:
        currencies = BUSINESS_PATTERNS["currency"].findall(text)
        entities["currency"].extend(currencies)
    
    # Extract dates and times
    if not entity_types or "temporal" in entity_types:
        dates = BUSINESS_PATTERNS["date"].findall(text)
        times = BUSINESS_PATTERNS["time"].findall(text)
        
        entities["date"].extend(dates)
        entities["time"].extend(times)
    
    # Extract locations (basic patterns)
    if not entity_types or "location" in entity_types:
        zip_codes = BUSINESS_PATTERNS["zip_code"].findall(text)
        entities["zip_code"].extend(zip_codes)
        
        # State abbreviations
        state_pattern = re.compile(r"\b[A-Z]{2}\b")
        states = state_pattern.findall(text)
        entities["state"].extend(states)
    
    # Extract identifiers
    if not entity_types or "identifier" in entity_types:
        ssns = BUSINESS_PATTERNS["ssn"].findall(text)
        entities["ssn"].extend(ssns)
        
        # Account numbers (basic pattern)
        account_pattern = re.compile(r"\b\d{8,16}\b")
        accounts = account_pattern.findall(text)
        entities["account_number"].extend(accounts)
    
    # Remove duplicates and return as regular dict
    return {k: list(set(v)) for k, v in entities.items() if v}


def score_relevance(text: str, keywords: list[str], method: str = "weighted") -> dict[str, Any]:
    """
    Score text relevance based on keyword matching.
    
    Args:
        text: Input text to score
        keywords: List of keywords to match
        method: Scoring method ("simple", "weighted", "tfidf")
        
    Returns:
        Relevance score and details
    """
    if not isinstance(text, str) or not keywords:
        return {"score": 0.0, "method": method, "matches": {}}
    
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)
    word_count = len(words)
    
    matches = {}
    total_score = 0.0
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Count exact matches
        exact_matches = len(re.findall(r"\b" + re.escape(keyword_lower) + r"\b", text_lower))
        
        # Count partial matches
        partial_matches = text_lower.count(keyword_lower) - exact_matches
        
        if method == "simple":
            score = exact_matches + (partial_matches * 0.5)
        elif method == "weighted":
            # Weight by keyword length and position
            score = exact_matches * len(keyword) + (partial_matches * len(keyword) * 0.5)
            
            # Bonus for matches near the beginning
            if text_lower.startswith(keyword_lower):
                score *= 1.5
        else:  # tfidf-like
            # Simple TF-IDF approximation
            tf = (exact_matches + partial_matches) / max(word_count, 1)
            # Assume IDF of 1 for simplicity
            score = tf
        
        if exact_matches > 0 or partial_matches > 0:
            matches[keyword] = {
                "exact_matches": exact_matches,
                "partial_matches": partial_matches,
                "score": score,
            }
            total_score += score
    
    # Normalize score
    if method in ["simple", "weighted"]:
        max_possible_score = sum(len(kw) for kw in keywords) if method == "weighted" else len(keywords)
        normalized_score = min(total_score / max(max_possible_score, 1), 1.0)
    else:
        normalized_score = min(total_score, 1.0)
    
    return {
        "score": normalized_score,
        "raw_score": total_score,
        "method": method,
        "matches": matches,
        "keywords_matched": len(matches),
        "total_keywords": len(keywords),
    }


def apply_text_rules(text: str, rules: dict[str, Any]) -> dict[str, Any]:
    """
    Apply a set of custom text processing rules.
    
    Args:
        text: Input text to process
        rules: Dictionary of rules to apply
        
    Returns:
        Results of applying all rules
    """
    if not isinstance(text, str) or not isinstance(rules, dict):
        return {"error": "Invalid input parameters"}
    
    results = {}
    
    for rule_name, rule_config in rules.items():
        try:
            rule_type = rule_config.get("type", "pattern")
            
            if rule_type == "pattern":
                pattern = rule_config.get("pattern", "")
                flags = rule_config.get("flags", 0)
                
                if pattern:
                    compiled_pattern = re.compile(pattern, flags)
                    matches = compiled_pattern.findall(text)
                    results[rule_name] = {"matches": matches, "count": len(matches)}
            
            elif rule_type == "keyword":
                keywords = rule_config.get("keywords", [])
                case_sensitive = rule_config.get("case_sensitive", False)
                
                search_text = text if case_sensitive else text.lower()
                search_keywords = keywords if case_sensitive else [kw.lower() for kw in keywords]
                
                matches = []
                for keyword in search_keywords:
                    if keyword in search_text:
                        matches.append(keyword)
                
                results[rule_name] = {"matches": matches, "count": len(matches)}
            
            elif rule_type == "classification":
                classification_result = classify_content(text, rule_config.get("classifier", "sentiment"))
                results[rule_name] = classification_result
            
            elif rule_type == "entity":
                entity_result = extract_entities(text, rule_config.get("entity_types"))
                results[rule_name] = entity_result
            
        except Exception as e:
            results[rule_name] = {"error": str(e)}
    
    return results


# Helper functions

def _calculate_confidence(scores: dict[str, dict[str, Any]], top_category: str) -> float:
    """Calculate confidence score for classification."""
    total_score = sum(s["score"] for s in scores.values())
    
    if total_score == 0:
        return 0.0
    
    top_score = scores[top_category]["score"]
    confidence = top_score / total_score
    
    # Adjust confidence based on absolute score
    if top_score < 2:
        confidence *= 0.5  # Lower confidence for very few matches
    
    return round(confidence, 3)


def create_custom_pattern(name: str, pattern: str, flags: int = 0) -> Pattern[str]:
    """
    Create a custom regex pattern for text processing.
    
    Args:
        name: Name for the pattern
        pattern: Regex pattern string
        flags: Regex flags
        
    Returns:
        Compiled regex pattern
    """
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        logger.error(f"Invalid regex pattern '{name}': {e}")
        return re.compile(r"(?!)")  # Pattern that never matches


def build_vocabulary_from_text(text: str, min_frequency: int = 2) -> dict[str, int]:
    """
    Build vocabulary from text with frequency counts.
    
    Args:
        text: Input text to analyze
        min_frequency: Minimum frequency for inclusion
        
    Returns:
        Dictionary of words and their frequencies
    """
    if not isinstance(text, str):
        return {}
    
    # Extract words (letters only, 3+ chars)
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    
    # Count frequencies
    frequency = defaultdict(int)
    for word in words:
        frequency[word] += 1
    
    # Filter by minimum frequency
    return {word: count for word, count in frequency.items() if count >= min_frequency}
