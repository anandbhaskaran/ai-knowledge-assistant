"""
Enhanced metadata extraction for article ingestion.

This module provides functions to extract rich metadata from article content,
improving retrieval performance through better context.
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Set, Optional


def extract_date_from_file(file_path: str) -> str:
    """
    Extract date from filename or file metadata.

    Args:
        file_path: Path to the file

    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    # For demonstration, use file modification time
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        # Default to today if we can't get the date
        return datetime.now().strftime("%Y-%m-%d")


def extract_title_from_content(content: str) -> Optional[str]:
    """
    Extract title from article content.

    Attempts to find a markdown or text title in the content.

    Args:
        content: Article text content

    Returns:
        Title string or None if not found
    """
    # Look for markdown title (# Title)
    md_title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if md_title_match:
        return md_title_match.group(1).strip()

    # Look for first non-empty line as fallback
    lines = content.strip().split('\n')
    for line in lines:
        if line.strip():
            return line.strip()

    return None


def extract_sections_from_content(content: str) -> List[str]:
    """
    Extract section headings from article content.

    Args:
        content: Article text content

    Returns:
        List of section headings
    """
    # Look for markdown section titles (## Section)
    section_matches = re.findall(r'^##\s+(.+?)$', content, re.MULTILINE)
    return [section.strip() for section in section_matches if section.strip()]


def extract_keywords_from_content(content: str) -> List[str]:
    """
    Extract potential keywords from article content.

    Args:
        content: Article text content

    Returns:
        List of extracted keywords
    """
    # Common stop words to filter out
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
        "at", "from", "by", "to", "for", "with", "in", "on", "of", "as",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "not", "can", "will", "should", "would",
        "could", "may", "might", "must", "shall"
    }

    # Extract words, clean them, and filter out stop words
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b', content.lower())
    filtered_words = [word for word in words if word not in stop_words]

    # Count word occurrences
    word_counts = {}
    for word in filtered_words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    # Get top keywords (most frequent words)
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [word for word, count in sorted_words[:20]]

    return top_keywords


def extract_entities_from_content(content: str) -> Dict[str, Set[str]]:
    """
    Extract named entities from article content.

    This is a simplified version that looks for:
    - Years (YYYY)
    - Percentages
    - Organizations (simple pattern matching for common suffixes)

    Args:
        content: Article text content

    Returns:
        Dictionary mapping entity types to sets of entities
    """
    entities = {
        "years": set(),
        "percentages": set(),
        "organizations": set()
    }

    # Extract years
    years = re.findall(r'\b(19\d\d|20\d\d)\b', content)
    entities["years"] = set(years)

    # Extract percentages
    percentages = re.findall(r'(\d+(?:\.\d+)?\s*%)', content)
    entities["percentages"] = set(percentages)

    # Simple organization detection
    org_patterns = [
        r'(?:[A-Z][a-z]+\s+)+(?:Agency|Association|Council|Organization|Authority|Institute|Department)',
        r'(?:[A-Z][a-z]+\s+)+(?:Ltd|Inc|Corp|LLC|GmbH|Co)'
    ]

    organizations = set()
    for pattern in org_patterns:
        orgs = re.findall(pattern, content)
        organizations.update(orgs)

    entities["organizations"] = organizations

    return entities


def extract_enhanced_metadata(file_path: str, content: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a file and its content.

    Args:
        file_path: Path to the file
        content: Text content of the file

    Returns:
        Dictionary of enhanced metadata
    """
    # Basic metadata
    basename = os.path.basename(file_path)
    file_ext = os.path.splitext(basename)[1]
    file_date = extract_date_from_file(file_path)

    # Extract content-based metadata
    title = extract_title_from_content(content) or os.path.splitext(basename)[0].replace("_", " ").title()
    sections = extract_sections_from_content(content)
    keywords = extract_keywords_from_content(content)
    entities = extract_entities_from_content(content)

    # Structured metadata
    metadata = {
        # File metadata
        "source": basename,
        "file_path": file_path,
        "file_type": f"text/{file_ext.lstrip('.')}",
        "file_size": len(content),
        "creation_date": file_date,
        "last_modified_date": file_date,

        # Content metadata
        "title": title,
        "date": file_date,
        "sections": sections,
        "keywords": keywords[:10],  # Top 10 keywords
        "years_mentioned": list(entities["years"]),
        "percentages": list(entities["percentages"]),
        "organizations": list(entities["organizations"]),

        # Summary metadata
        "section_count": len(sections),
        "keyword_count": len(keywords),
        "content_length": len(content.split())
    }

    return metadata