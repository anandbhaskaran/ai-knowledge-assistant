"""
Draft article validation and quality checking
"""
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def count_words(text: str) -> int:
    """
    Count words in text, excluding markdown syntax

    Args:
        text: Markdown text to count

    Returns:
        Word count
    """
    # Remove markdown syntax
    clean_text = re.sub(r'#+\s', '', text)  # Remove headers
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)  # Remove links
    clean_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', clean_text)  # Remove bold
    clean_text = re.sub(r'\*([^\*]+)\*', r'\1', clean_text)  # Remove italic
    clean_text = re.sub(r'`([^`]+)`', r'\1', clean_text)  # Remove code

    # Count words
    words = clean_text.split()
    return len(words)


def extract_source_numbers(draft: str) -> List[int]:
    """
    Extract source numbers from [X] citations

    Args:
        draft: Article draft text

    Returns:
        List of source numbers (integers like 1, 2, 3)
    """
    pattern = r'\[(\d+)\]'
    numbers = re.findall(pattern, draft)
    numbers = [int(n) for n in numbers]

    logger.info(f"Extracted {len(numbers)} source number citations")
    return numbers


def validate_editorial_compliance(draft: str) -> float:
    """
    Check draft compliance with editorial guidelines

    Validates:
    - Sentence length (15-20 words average)
    - Paragraph length (2-4 sentences)
    - Citations present
    - No clickbait indicators

    Args:
        draft: Article draft text

    Returns:
        Compliance score (0-1)
    """
    score = 1.0

    # Extract main content (exclude headers)
    content_lines = [line for line in draft.split('\n') if line.strip() and not line.startswith('#')]
    content = ' '.join(content_lines)

    # Check 1: Sentence length
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]

    if sentences:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Ideal: 15-20 words
        if avg_sentence_length < 10 or avg_sentence_length > 30:
            score -= 0.2
            logger.info(f"Sentence length outside ideal range: {avg_sentence_length:.1f} words")
        elif avg_sentence_length < 15 or avg_sentence_length > 20:
            score -= 0.1

    # Check 2: Paragraph length
    paragraphs = [p for p in draft.split('\n\n') if p.strip() and not p.startswith('#')]

    if paragraphs:
        paragraph_sentence_counts = []
        for para in paragraphs:
            para_sentences = re.split(r'[.!?]+', para)
            para_sentences = [s.strip() for s in para_sentences if s.strip()]
            paragraph_sentence_counts.append(len(para_sentences))

        # Ideal: 2-4 sentences per paragraph
        very_short = sum(1 for count in paragraph_sentence_counts if count < 2)
        very_long = sum(1 for count in paragraph_sentence_counts if count > 6)

        if very_short > len(paragraphs) * 0.3:  # More than 30% too short
            score -= 0.15
        if very_long > len(paragraphs) * 0.2:  # More than 20% too long
            score -= 0.15

    # Check 3: Citations present
    citation_numbers = extract_source_numbers(draft)
    word_count = count_words(draft)

    if word_count > 500:  # Only check for substantial drafts
        citation_ratio = len(citation_numbers) / (word_count / 100)  # Citations per 100 words

        if citation_ratio < 0.5:  # Less than 1 citation per 200 words
            score -= 0.2
            logger.info(f"Low citation density: {citation_ratio:.2f} per 100 words")

    # Check 4: Avoid clickbait indicators
    clickbait_words = ['shocking', 'amazing', 'incredible', 'unbelievable', 'you won\'t believe']
    content_lower = content.lower()

    clickbait_count = sum(1 for word in clickbait_words if word in content_lower)
    if clickbait_count > 0:
        score -= 0.1 * clickbait_count
        logger.info(f"Detected {clickbait_count} clickbait indicators")

    # Ensure score stays in valid range
    score = max(0.0, min(1.0, score))

    logger.info(f"Editorial compliance score: {score:.2f}")
    return score


def track_source_usage(draft: str, available_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Match citations in draft to source objects and track usage by number

    Args:
        draft: Article draft text
        available_sources: List of source dictionaries (numbered 1, 2, 3, etc.)

    Returns:
        Dictionary with sources_used, sources_available, citation_count, unique_sources_count
    """
    # Extract source numbers from [X] citations
    cited_numbers = extract_source_numbers(draft)
    citation_count = len(cited_numbers)

    # Track which source numbers were used (1-based)
    used_numbers = set(cited_numbers)

    # Split sources into used and available
    sources_used = []
    sources_available = []

    for i, source in enumerate(available_sources, 1):
        if i in used_numbers:
            # Add citation_number to the source
            source_with_number = source.copy()
            source_with_number['citation_number'] = i
            sources_used.append(source_with_number)
        else:
            sources_available.append(source)

    unique_sources = len(used_numbers)

    logger.info(f"Source usage: {len(sources_used)} used, {len(sources_available)} available, "
                f"{citation_count} citations, {unique_sources} unique sources")

    return {
        'sources_used': sources_used,
        'sources_available': sources_available,
        'citation_count': citation_count,
        'unique_sources_count': unique_sources
    }


def expand_citations(draft: str, sources: List[Dict[str, Any]]) -> str:
    """
    Expand [X] citations to full [X, Source, Title, Date] format

    Args:
        draft: Article draft with [X] number citations
        sources: List of source dictionaries (numbered 1, 2, 3, etc.)

    Returns:
        Draft with expanded citations in format [number, source, title, date]
    """
    def replace_citation(match):
        num = int(match.group(1))
        if 1 <= num <= len(sources):
            source = sources[num - 1]  # Convert to 0-based index
            source_name = source.get('source', 'Unknown')
            title = source.get('title', 'Unknown')
            date = source.get('date', 'Unknown')
            return f"[{num}, {source_name}, {title}, {date}]"
        else:
            return match.group(0)  # Return original if number out of range

    pattern = r'\[(\d+)\]'
    expanded = re.sub(pattern, replace_citation, draft)

    logger.info("Expanded [X] citations to full [X, Source, Title, Date] format")
    return expanded
