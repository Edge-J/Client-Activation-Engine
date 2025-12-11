"""
Deterministic industry/business type normalization tool.

This tool normalizes various business type descriptions into standardized
categories using rule-based matching instead of LLM calls.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Industry mapping constants
INDUSTRY_KEYWORDS = {
    "healthcare": {
        "primary": ["medical", "health", "hospital", "clinic", "doctor", "physician", 
                   "dental", "pharmacy", "healthcare", "wellness", "therapy"],
        "secondary": ["patient", "diagnosis", "treatment", "medicine", "hipaa", 
                     "insurance", "medicare", "medicaid"],
        "aliases": ["medical", "health", "wellness", "clinical"]
    },
    "ecommerce": {
        "primary": ["ecommerce", "e-commerce", "retail", "shop", "store", "marketplace", 
                   "shopping", "sales", "merchant"],
        "secondary": ["product", "inventory", "cart", "checkout", "payment", 
                     "shipping", "fulfillment", "customer"],
        "aliases": ["retail", "online_store", "marketplace"]
    },
    "fintech": {
        "primary": ["financial", "finance", "banking", "investment", "trading", 
                   "fintech", "payments", "crypto", "blockchain"],
        "secondary": ["money", "currency", "loan", "credit", "mortgage", "insurance", 
                     "wealth", "portfolio", "transaction"],
        "aliases": ["financial", "banking", "payments", "investment"]
    },
    "education": {
        "primary": ["education", "school", "university", "college", "academy", 
                   "learning", "training", "teaching"],
        "secondary": ["student", "teacher", "course", "curriculum", "degree", 
                     "certification", "tuition", "enrollment"],
        "aliases": ["educational", "academic", "learning"]
    },
    "technology": {
        "primary": ["technology", "tech", "software", "saas", "platform", 
                   "development", "programming", "it"],
        "secondary": ["app", "application", "system", "database", "cloud", 
                     "api", "integration", "automation"],
        "aliases": ["tech", "software", "saas", "it"]
    },
    "manufacturing": {
        "primary": ["manufacturing", "factory", "production", "industrial", 
                   "assembly", "fabrication"],
        "secondary": ["supply", "logistics", "warehouse", "inventory", 
                     "quality", "equipment", "machinery"],
        "aliases": ["industrial", "production", "factory"]
    },
    "consulting": {
        "primary": ["consulting", "advisory", "strategy", "management", 
                   "professional", "services"],
        "secondary": ["consultant", "advisor", "expertise", "guidance", 
                     "analysis", "optimization", "improvement"],
        "aliases": ["advisory", "professional_services", "strategy"]
    },
    "nonprofit": {
        "primary": ["nonprofit", "non-profit", "charity", "foundation", 
                   "ngo", "volunteer", "donation"],
        "secondary": ["community", "social", "humanitarian", "cause", 
                     "fundraising", "grant", "mission"],
        "aliases": ["charity", "ngo", "foundation", "social"]
    },
    "real_estate": {
        "primary": ["real estate", "property", "realty", "housing", "residential", 
                   "commercial", "land"],
        "secondary": ["buyer", "seller", "agent", "broker", "listing", 
                     "mortgage", "rental", "lease"],
        "aliases": ["property", "realty", "housing"]
    },
    "legal": {
        "primary": ["legal", "law", "attorney", "lawyer", "court", "litigation", 
                   "compliance"],
        "secondary": ["contract", "agreement", "regulation", "statute", 
                     "case", "client", "representation"],
        "aliases": ["law", "attorney", "compliance"]
    },
    "media": {
        "primary": ["media", "news", "publishing", "journalism", "broadcast", 
                   "content", "entertainment"],
        "secondary": ["article", "story", "reporter", "editor", "audience", 
                     "advertising", "marketing"],
        "aliases": ["publishing", "news", "content", "entertainment"]
    },
    "food": {
        "primary": ["food", "restaurant", "catering", "culinary", "dining", 
                   "hospitality", "beverage"],
        "secondary": ["menu", "recipe", "kitchen", "chef", "nutrition", 
                     "delivery", "takeout"],
        "aliases": ["restaurant", "hospitality", "culinary"]
    }
}

CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the industry normalization tool."""
    return {
        "name": "normalize_industry",
        "description": "Normalize business type descriptions into standardized industry categories",
        "version": "1.0.0", 
        "category": "intake",
        "parameters": {
            "type": "object",
            "properties": {
                "business_description": {
                    "type": "string",
                    "description": "Raw business description or industry text",
                },
                "context_data": {
                    "type": "object", 
                    "description": "Additional context like requirements or company info",
                    "default": {},
                },
                "confidence_threshold": {
                    "type": "number",
                    "description": "Minimum confidence score for classification",
                    "default": 0.6,
                },
            },
            "required": ["business_description"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "normalized_industry": {
                    "type": "string",
                    "description": "Standardized industry category",
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Confidence in classification (0-1)",
                },
                "alternative_matches": {
                    "type": "array",
                    "description": "Other possible industry matches",
                },
                "classification_evidence": {
                    "type": "object",
                    "description": "Keywords and patterns that led to classification",
                },
            },
        },
        "dependencies": [],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize business description into standardized industry category.
    
    Args:
        parameters: Tool execution parameters with business description
        
    Returns:
        Dictionary with normalized industry and confidence metrics
    """
    business_description = parameters.get("business_description", "")
    context_data = parameters.get("context_data", {})
    confidence_threshold = parameters.get("confidence_threshold", 0.6)
    
    if not business_description.strip():
        return {
            "normalized_industry": "general",
            "confidence_score": 0.0,
            "alternative_matches": [],
            "classification_evidence": {},
            "error": "Empty business description provided",
        }
    
    logger.info("Normalizing industry for: %s", business_description[:50])
    
    # Combine description with context for richer analysis
    full_text = _combine_text_sources(business_description, context_data)
    
    # Calculate scores for each industry
    industry_scores = _calculate_industry_scores(full_text)
    
    # Determine primary classification
    primary_industry, primary_score = _get_primary_classification(industry_scores)
    
    # Get alternative matches above threshold
    alternatives = _get_alternative_matches(industry_scores, primary_industry, confidence_threshold)
    
    # Generate evidence for classification
    evidence = _generate_classification_evidence(full_text, primary_industry)
    
    # Determine confidence level
    confidence_level = _get_confidence_level(primary_score)
    
    return {
        "normalized_industry": primary_industry,
        "confidence_score": primary_score,
        "confidence_level": confidence_level,
        "alternative_matches": alternatives,
        "classification_evidence": evidence,
        "processing_metadata": {
            "tool": "normalize_industry",
            "version": "1.0.0",
            "text_length": len(full_text),
            "industries_evaluated": len(industry_scores),
        },
    }


def _combine_text_sources(description: str, context: dict[str, Any]) -> str:
    """Combine business description with context data for analysis."""
    text_parts = [description.lower()]
    
    # Add relevant context fields
    for field in ["requirements", "services", "products", "company_name", "project_title"]:
        if field in context and context[field]:
            if isinstance(context[field], str):
                text_parts.append(context[field].lower())
            elif isinstance(context[field], list):
                text_parts.extend([str(item).lower() for item in context[field]])
    
    return " ".join(text_parts)


def _calculate_industry_scores(text: str) -> dict[str, float]:
    """Calculate matching scores for each industry category."""
    scores = {}
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        primary_matches = _count_keyword_matches(text, keywords["primary"])
        secondary_matches = _count_keyword_matches(text, keywords["secondary"])
        
        # Weight primary matches more heavily
        raw_score = (primary_matches * 2) + (secondary_matches * 1)
        
        # Normalize by total keywords to get percentage
        total_keywords = len(keywords["primary"]) + len(keywords["secondary"])
        normalized_score = min(1.0, raw_score / (total_keywords * 0.3))  # 30% match = 1.0
        
        scores[industry] = normalized_score
    
    return scores


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    """Count how many keywords from the list appear in the text."""
    matches = 0
    for keyword in keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword.replace(' ', r'\s+')) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            matches += 1
    return matches


def _get_primary_classification(scores: dict[str, float]) -> tuple[str, float]:
    """Get the industry with the highest score."""
    if not scores:
        return "general", 0.0
    
    # Sort by score descending
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    top_industry, top_score = sorted_scores[0]
    
    # If top score is very low, classify as general
    if top_score < 0.2:
        return "general", top_score
    
    return top_industry, top_score


def _get_alternative_matches(scores: dict[str, float], primary: str, threshold: float) -> list[dict[str, Any]]:
    """Get alternative industry matches above the confidence threshold."""
    alternatives = []
    
    for industry, score in scores.items():
        if industry != primary and score >= threshold:
            alternatives.append({
                "industry": industry,
                "confidence_score": score,
                "aliases": INDUSTRY_KEYWORDS[industry]["aliases"]
            })
    
    # Sort by score descending
    alternatives.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    return alternatives[:3]  # Return top 3 alternatives


def _generate_classification_evidence(text: str, industry: str) -> dict[str, Any]:
    """Generate evidence showing why the classification was made."""
    if industry not in INDUSTRY_KEYWORDS:
        return {"matched_keywords": [], "reasoning": "No specific keywords matched"}
    
    keywords = INDUSTRY_KEYWORDS[industry]
    matched_primary = []
    matched_secondary = []
    
    # Find which keywords actually matched
    for keyword in keywords["primary"]:
        pattern = r'\b' + re.escape(keyword.replace(' ', r'\s+')) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            matched_primary.append(keyword)
    
    for keyword in keywords["secondary"]:
        pattern = r'\b' + re.escape(keyword.replace(' ', r'\s+')) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            matched_secondary.append(keyword)
    
    return {
        "matched_primary_keywords": matched_primary,
        "matched_secondary_keywords": matched_secondary,
        "total_matches": len(matched_primary) + len(matched_secondary),
        "industry_aliases": keywords["aliases"],
        "reasoning": f"Matched {len(matched_primary)} primary and {len(matched_secondary)} secondary keywords"
    }


def _get_confidence_level(score: float) -> str:
    """Convert numeric confidence score to categorical level."""
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    if score >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    if score >= CONFIDENCE_THRESHOLDS["low"]:
        return "low"
    return "very_low"


# Utility functions for external use
def get_supported_industries() -> list[str]:
    """Get list of all supported industry categories."""
    return list(INDUSTRY_KEYWORDS.keys())


def get_industry_aliases(industry: str) -> list[str]:
    """Get alternative names/aliases for an industry."""
    if industry in INDUSTRY_KEYWORDS:
        return INDUSTRY_KEYWORDS[industry]["aliases"]
    return []


def validate_industry(industry: str) -> bool:
    """Check if an industry is in the supported list."""
    return industry in INDUSTRY_KEYWORDS or industry == "general"
