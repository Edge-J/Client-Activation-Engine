"""
Data cleaning and preprocessing utilities.

This module provides deterministic data cleaning functions
for standardizing and normalizing various data types.
"""

import logging
import re
from typing import Any, Union

logger = logging.getLogger(__name__)

# Common cleaning patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
URL_PATTERN = re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$')

# Text normalization patterns
WHITESPACE_PATTERN = re.compile(r'\s+')
SPECIAL_CHARS_PATTERN = re.compile(r'[^\w\s-]')
MULTIPLE_SPACES_PATTERN = re.compile(r' {2,}')


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the cleaning utilities."""
    return {
        "name": "cleaning",
        "description": "Data cleaning and preprocessing utilities",
        "version": "1.0.0",
        "category": "skills",
        "functions": [
            "clean_text",
            "normalize_email",
            "normalize_phone",
            "clean_whitespace",
            "sanitize_filename",
            "extract_numbers",
            "standardize_case",
        ],
    }


def clean_text(text: str, options: dict[str, bool] = None) -> str:
    """
    Clean and normalize text data.
    
    Args:
        text: Input text to clean
        options: Cleaning options dict
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    if options is None:
        options = {}
    
    cleaned = text
    
    # Remove extra whitespace (default: True)
    if options.get("remove_extra_whitespace", True):
        cleaned = WHITESPACE_PATTERN.sub(' ', cleaned)
        cleaned = cleaned.strip()
    
    # Remove special characters
    if options.get("remove_special_chars", False):
        cleaned = SPECIAL_CHARS_PATTERN.sub('', cleaned)
    
    # Normalize case
    case_option = options.get("case", None)
    if case_option == "lower":
        cleaned = cleaned.lower()
    elif case_option == "upper":
        cleaned = cleaned.upper()
    elif case_option == "title":
        cleaned = cleaned.title()
    
    # Remove multiple spaces
    if options.get("remove_multiple_spaces", True):
        cleaned = MULTIPLE_SPACES_PATTERN.sub(' ', cleaned)
    
    return cleaned.strip()


def normalize_email(email: str) -> dict[str, Union[str, bool]]:
    """
    Normalize and validate email addresses.
    
    Args:
        email: Input email string
        
    Returns:
        Dictionary with normalized email and validation status
    """
    if not isinstance(email, str):
        return {"email": "", "is_valid": False, "error": "Invalid input type"}
    
    # Basic cleaning
    cleaned = email.strip().lower()
    
    # Validate format
    if EMAIL_PATTERN.match(cleaned):
        # Additional normalization
        local, domain = cleaned.split('@')
        
        # Gmail-specific normalization (remove dots and plus aliases)
        if domain in ['gmail.com', 'googlemail.com']:
            local = local.split('+')[0]  # Remove plus aliases
            local = local.replace('.', '')  # Remove dots
            domain = 'gmail.com'  # Standardize to gmail.com
        
        normalized = f"{local}@{domain}"
        
        return {
            "email": normalized,
            "is_valid": True,
            "original": email,
            "local_part": local,
            "domain": domain,
        }
    else:
        return {
            "email": cleaned,
            "is_valid": False,
            "error": "Invalid email format",
            "original": email,
        }


def normalize_phone(phone: str, country_code: str = "US") -> dict[str, Union[str, bool]]:
    """
    Normalize phone numbers to standard format.
    
    Args:
        phone: Input phone number string
        country_code: Country code for formatting
        
    Returns:
        Dictionary with normalized phone and validation status
    """
    if not isinstance(phone, str):
        return {"phone": "", "is_valid": False, "error": "Invalid input type"}
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    if country_code == "US":
        # US phone number normalization
        # Remove country code if present
        if cleaned.startswith('+1'):
            cleaned = cleaned[2:]
        elif cleaned.startswith('1') and len(cleaned) == 11:
            cleaned = cleaned[1:]
        
        # Validate US format (10 digits)
        if len(cleaned) == 10 and cleaned.isdigit():
            # Format as (XXX) XXX-XXXX
            formatted = f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
            
            return {
                "phone": formatted,
                "digits_only": cleaned,
                "is_valid": True,
                "country": "US",
                "original": phone,
            }
    
    # Generic international format
    if cleaned.startswith('+') and len(cleaned) > 7:
        return {
            "phone": cleaned,
            "is_valid": True,
            "country": "international",
            "original": phone,
        }
    
    return {
        "phone": cleaned,
        "is_valid": False,
        "error": "Invalid phone number format",
        "original": phone,
    }


def clean_whitespace(text: str) -> str:
    """
    Clean various types of whitespace from text.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Replace various whitespace characters with regular spaces
    cleaned = text.replace('\t', ' ')  # Replace tabs
    cleaned = cleaned.replace('\r\n', '\n')  # Normalize line endings
    cleaned = cleaned.replace('\r', '\n')  # Mac line endings
    
    # Remove extra spaces but preserve line breaks
    lines = cleaned.split('\n')
    cleaned_lines = [MULTIPLE_SPACES_PATTERN.sub(' ', line.strip()) for line in lines]
    
    # Remove empty lines at start/end, but keep internal empty lines
    while cleaned_lines and not cleaned_lines[0]:
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop()
    
    return '\n'.join(cleaned_lines)


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename: Input filename
        replacement: Character to replace invalid chars with
        
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return str(filename) if filename is not None else "file"
    
    # Remove/replace invalid characters
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, replacement)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = "file"
    
    # Truncate if too long
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 250 - len(ext)
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename


def extract_numbers(text: str, number_type: str = "all") -> list[Union[int, float]]:
    """
    Extract numbers from text.
    
    Args:
        text: Input text
        number_type: Type of numbers to extract ("int", "float", "all")
        
    Returns:
        List of extracted numbers
    """
    if not isinstance(text, str):
        return []
    
    numbers = []
    
    if number_type in ["float", "all"]:
        # Extract floating point numbers
        float_pattern = re.compile(r'-?\d+\.\d+')
        floats = [float(match) for match in float_pattern.findall(text)]
        numbers.extend(floats)
    
    if number_type in ["int", "all"]:
        # Extract integers (excluding those that are part of floats)
        text_without_floats = re.sub(r'-?\d+\.\d+', '', text)
        int_pattern = re.compile(r'-?\d+')
        integers = [int(match) for match in int_pattern.findall(text_without_floats)]
        numbers.extend(integers)
    
    return numbers


def standardize_case(text: str, case_type: str = "sentence") -> str:
    """
    Standardize text case formatting.
    
    Args:
        text: Input text
        case_type: Type of case formatting
        
    Returns:
        Text with standardized case
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    if case_type == "lower":
        return text.lower()
    elif case_type == "upper":
        return text.upper()
    elif case_type == "title":
        return text.title()
    elif case_type == "sentence":
        # Capitalize first letter of each sentence
        sentences = re.split(r'([.!?]+)', text)
        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0:  # Text part (not punctuation)
                part = part.strip()
                if part:
                    part = part[0].upper() + part[1:].lower()
            result.append(part)
        return ''.join(result)
    elif case_type == "camel":
        # Convert to camelCase
        words = re.findall(r'\w+', text.lower())
        if words:
            return words[0] + ''.join(word.capitalize() for word in words[1:])
        return text
    elif case_type == "snake":
        # Convert to snake_case
        words = re.findall(r'\w+', text.lower())
        return '_'.join(words)
    elif case_type == "kebab":
        # Convert to kebab-case
        words = re.findall(r'\w+', text.lower())
        return '-'.join(words)
    
    return text


def remove_duplicates(items: list[Any], key_func=None) -> list[Any]:
    """
    Remove duplicates from a list while preserving order.
    
    Args:
        items: List of items
        key_func: Optional function to generate comparison key
        
    Returns:
        List with duplicates removed
    """
    if not isinstance(items, list):
        return []
    
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item) if key_func else item
        
        # Handle unhashable types
        try:
            if key not in seen:
                seen.add(key)
                result.append(item)
        except TypeError:
            # For unhashable types, do linear search
            if key not in [key_func(x) if key_func else x for x in result]:
                result.append(item)
    
    return result


def normalize_url(url: str) -> dict[str, Union[str, bool]]:
    """
    Normalize and validate URLs.
    
    Args:
        url: Input URL string
        
    Returns:
        Dictionary with normalized URL and validation status
    """
    if not isinstance(url, str):
        return {"url": "", "is_valid": False, "error": "Invalid input type"}
    
    # Basic cleaning
    cleaned = url.strip()
    
    # Add protocol if missing
    if not cleaned.startswith(('http://', 'https://', 'ftp://')):
        cleaned = 'https://' + cleaned
    
    # Validate format
    if URL_PATTERN.match(cleaned):
        # Additional normalization
        cleaned = cleaned.lower()
        
        # Remove trailing slash for root domains
        if cleaned.endswith('/') and cleaned.count('/') == 3:
            cleaned = cleaned[:-1]
        
        return {
            "url": cleaned,
            "is_valid": True,
            "original": url,
        }
    else:
        return {
            "url": cleaned,
            "is_valid": False,
            "error": "Invalid URL format",
            "original": url,
        }


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string for parsing.
    
    Args:
        json_str: Input JSON string
        
    Returns:
        Cleaned JSON string
    """
    if not isinstance(json_str, str):
        return "{}"
    
    # Remove BOM if present
    if json_str.startswith('\ufeff'):
        json_str = json_str[1:]
    
    # Basic cleanup
    cleaned = json_str.strip()
    
    # Fix common JSON issues
    # Remove trailing commas before closing brackets
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Fix single quotes to double quotes (basic)
    # This is a simple fix and may not work for all cases
    cleaned = re.sub(r"'([^']*)':", r'"\1":', cleaned)
    
    return cleaned
