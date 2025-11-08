# Draft Article Generation - Agent-Based Architecture Plan

## Overview

The draft generation system will use a **ReActAgent** to transform structured outlines into publication-ready article drafts (1,000-2,000 words) that incorporate factual content from multiple sources with proper citations while maintaining editorial tone and quality standards.

## Core Requirements

1. **Input**: Outline from outline endpoint (headline, thesis, key_facts, outline, sources)
2. **Output**: 1,000-2,000 word article draft with citations
3. **Quality**: Publication's editorial tone and quality standard
4. **Citations**: Appropriate inline citations for all referenced information
5. **Sources**: Incorporate content from both archive and external (web) sources

## Proposed Architecture

### 1. Agent-Based Approach

**Why Agent-Based?**
- Needs to dynamically retrieve additional sources as gaps are identified
- Must verify facts and find supporting evidence
- Can iteratively refine sections based on word count and quality
- Similar to outline generation, but focused on content expansion

### 2. Input Schema

```python
class DraftRequest(BaseModel):
    """Request model for draft article generation"""
    headline: str
    thesis: str
    outline: str  # Markdown outline from outline endpoint
    key_facts: Optional[List[str]] = None
    sources: Optional[List[Source]] = None  # Pre-retrieved sources from outline
    target_word_count: int = Field(1500, ge=1000, le=2000)
    include_introduction: bool = True
    include_conclusion: bool = True
```

### 3. Output Schema

```python
class DraftResponse(BaseModel):
    """Response model for draft article"""
    headline: str
    thesis: str
    draft: str  # Full article in markdown with inline citations
    word_count: int
    sources_used: List[Source]  # All sources cited in the draft
    sources_available: List[Source]  # Sources from outline not used
    sections_generated: List[str]  # H2 sections generated
    editorial_compliance_score: Optional[float]  # 0-1 score
    warning: Optional[str]
```

## Agent Tools

### Tool 1: Archive Retrieval Tool (Existing)
- **Purpose**: Find additional archive sources for specific claims/sections
- **Use Case**: When outline sources insufficient for detailed writing
- **Reuse**: `archive_retrieval_tool` from `app/services/tools.py`

### Tool 2: Web Search Tool (Existing)
- **Purpose**: Find recent statistics, quotes, or breaking developments
- **Use Case**: When current information needed beyond outline sources
- **Reuse**: `web_search_tool` from `app/services/tools.py`

### Tool 3: Citation Formatter Tool (New)
- **Purpose**: Format citations consistently as [Source, Title, Date]
- **Input**: Source object or raw citation data
- **Output**: Properly formatted citation string
- **Implementation**: Simple function tool

```python
def citation_formatter_tool_fn(source_title: str, source_name: str, date: str) -> str:
    """Format citation in standard format [Source, Title, Date]"""
    return f"[{source_name}, {source_title}, {date}]"
```

### Tool 4: Section Expander Tool (New - Optional)
- **Purpose**: Expand outline placeholders into full paragraphs
- **Input**: Section heading, key points, relevant sources
- **Output**: 2-4 paragraph section with citations
- **Implementation**: LLM-powered with source grounding

## Workflow

```
Draft Request
    ↓
Load Editorial Guidelines
    ↓
Parse Outline Structure
    ↓
For Each Section in Outline:
    ├── Extract placeholder instructions
    ├── Identify relevant sources from outline
    ├── Agent decides: Need more sources?
    │   ├── Yes → Use archive_retrieval or web_search
    │   └── No → Use existing sources
    ├── Generate section content (2-4 paragraphs)
    ├── Add inline citations [Source, Title, Date]
    └── Validate against editorial guidelines
    ↓
Generate Introduction (if requested)
    ├── Hook based on thesis + key_facts
    ├── Context from sources
    └── Clear thesis statement
    ↓
Generate Conclusion (if requested)
    ├── Synthesize main arguments
    ├── Implications for future
    └── Memorable closing thought
    ↓
Combine All Sections
    ↓
Word Count Check & Adjustment
    ├── < 1000 words → Expand thin sections
    ├── > 2000 words → Condense verbose sections
    └── 1000-2000 → Proceed
    ↓
Final Editorial Review Pass
    ↓
Return DraftResponse
```

## Agent Prompt Structure

```python
agent_prompt = f"""
You are an AI Journalist Assistant writing a publication-ready article draft.

EDITORIAL GUIDELINES:
{editorial_guidelines}

ARTICLE DETAILS:
Headline: {headline}
Thesis: {thesis}
Target Word Count: {target_word_count} words

OUTLINE:
{outline}

AVAILABLE SOURCES:
{format_sources(sources)}

YOUR TASK:
1. Write a complete article following the provided outline structure
2. Each section should be 2-4 well-developed paragraphs
3. Incorporate facts and evidence from available sources
4. Use inline citations in format [Source, Title, Date] after every factual claim
5. Maintain the publication's voice and tone from editorial guidelines
6. Write for intelligent non-specialists - explain jargon, use concrete examples
7. Target {target_word_count} words total (1000-2000 word range)

CRITICAL RULES:
- ONLY cite information from provided sources or sources you retrieve using tools
- NEVER fabricate statistics, quotes, or sources
- Every factual claim MUST have a citation
- Follow editorial guidelines for voice, tone, and structure
- Write clear topic sentences for each paragraph
- Use transitions between sections
- If you need additional sources, use archive_retrieval or web_search tools

SECTION-BY-SECTION APPROACH:
- Start with Introduction (hook + context + thesis + why it matters)
- Write each body section from the outline
- End with Conclusion (synthesis + implications + closing thought)
- Ensure each section flows naturally to the next

Begin writing the article. Use the tools when you need additional sources.
"""
```

## Implementation Details

### File Structure

```
app/
├── services/
│   ├── tools.py                    # Existing tools + new citation formatter
│   ├── draft_agent.py              # New: Draft agent implementation
│   └── draft_validator.py          # New: Editorial compliance checker
├── api/
│   └── endpoints/
│       └── draft.py                # Updated: Use draft_agent
└── models/
    └── schemas.py                  # Updated: DraftRequest/Response
```

### Core Functions

#### 1. `draft_agent.py`

```python
def generate_draft_with_agent(
    headline: str,
    thesis: str,
    outline: str,
    sources: List[Dict[str, Any]],
    target_word_count: int = 1500,
    key_facts: List[str] = None
) -> Dict[str, Any]:
    """
    Generate article draft using ReActAgent

    Returns:
        - draft: Full article markdown
        - word_count: Actual word count
        - sources_used: Sources cited in draft
        - warning: Any quality warnings
    """
```

#### 2. `draft_validator.py`

```python
def validate_editorial_compliance(draft: str, guidelines: str) -> float:
    """
    Check draft compliance with editorial guidelines

    Validates:
    - Sentence length (15-20 words average)
    - Paragraph length (2-4 sentences)
    - Jargon explained
    - No clickbait language
    - Citations present

    Returns: Score 0-1
    """

def extract_citations(draft: str) -> List[str]:
    """Extract all [Source, Title, Date] citations from draft"""

def count_words(text: str) -> int:
    """Accurate word count excluding markdown syntax"""

def validate_citations(draft: str, available_sources: List[Source]) -> Tuple[bool, List[str]]:
    """
    Check that all citations reference available sources

    Returns: (valid, list_of_invalid_citations)
    """
```

## Source Management Strategy

### Using Outline Sources Efficiently

1. **Pass sources from outline to draft endpoint**
   - Reduces redundant retrieval
   - Maintains consistency
   - Faster generation

2. **Agent retrieves additional sources only when needed**
   - Specific statistics missing
   - Need expert quotes
   - Recent developments required

3. **Track source usage**
   - Mark which sources actually cited in draft
   - Return unused sources for transparency

### Source Citation Tracking

```python
def track_source_usage(draft: str, available_sources: List[Source]) -> Dict:
    """
    Match citations in draft to source objects

    Returns:
        {
            'sources_used': [Source objects cited],
            'sources_available': [Source objects not cited],
            'citation_count': int,
            'unique_sources_count': int
        }
    """
```

## Quality Assurance

### Pre-Generation Checks
- [ ] Outline is not empty
- [ ] At least 3 sources available
- [ ] Editorial guidelines loaded
- [ ] Target word count in valid range (1000-2000)

### Post-Generation Checks
- [ ] Word count within range (1000-2000)
- [ ] At least 3 distinct sources cited
- [ ] All citations match available sources
- [ ] No fabricated sources
- [ ] Sections match outline structure
- [ ] Introduction and conclusion present
- [ ] Editorial compliance score > 0.7

### Warning Conditions
- Word count at extreme edges (1000-1100 or 1900-2000)
- Low source diversity (< 3 unique sources)
- Editorial compliance < 0.7
- Sections missing from outline
- Uncited factual claims detected

## Editorial Guidelines Integration

### Key Guidelines to Enforce

From `data/guidlines/editorial-guidelines.md`:

1. **Voice & Tone**
   - Intelligent, confident, conversational
   - Authoritative but not condescending
   - Avoid hype, hyperbole, breathless urgency

2. **Writing Standards**
   - 15-20 words per sentence (average)
   - 2-4 sentences per paragraph
   - Explain jargon on first use
   - Concrete examples

3. **Structure**
   - Clear headlines (60-80 chars)
   - Strong intro: Hook + why it matters
   - One idea per paragraph
   - Subheadings every 3-4 paragraphs
   - Synthesize in conclusion, don't just restate

4. **Support Claims**
   - Cite credible sources
   - Provide context for data
   - Distinguish facts from analysis

## Citation Format Standards

### Standard Format
```
[Source, Title, Date]
```

### Examples
```markdown
AI diagnostic tools are achieving 95% accuracy in detecting certain cancers [Nature,
AI-Powered Cancer Detection Breakthrough, 2024-11-01].

The technology has reduced diagnosis times by up to 50% in pilot programs [Johns Hopkins
Medical Journal, Rapid Diagnostics with Machine Learning, 2024-09-15].
```

### Citation Rules
1. **Placement**: Immediately after the claim, before the period
2. **Frequency**: Every factual claim, statistic, or quote
3. **Minimum**: At least 3 distinct sources in the article
4. **Format**: Exact format [Source, Title, Date]
5. **Date Format**: YYYY-MM-DD or Month DD, YYYY

## Performance Considerations

### Expected Performance
- **Agent iterations**: 5-15 (depending on outline complexity)
- **Generation time**: 30-90 seconds
- **Tool calls**: 2-8 (archive/web search for additional sources)

### Optimization Strategies
1. **Pass outline sources** to reduce tool calls
2. **Set max iterations** to prevent infinite loops (e.g., 20)
3. **Cache editorial guidelines** - load once, reuse
4. **Batch similar sections** if applicable
5. **Use GPT-4 for quality**, GPT-3.5-turbo for speed testing

## Error Handling

### Common Errors

1. **Insufficient Sources**
   - Error: < 3 sources available
   - Response: Return error with suggestion to run outline first

2. **Word Count Failure**
   - Error: Can't reach target after adjustments
   - Response: Return draft with warning about word count

3. **Citation Format Errors**
   - Error: Malformed citations detected
   - Response: Auto-fix common issues, warn if critical

4. **Tool Retrieval Failures**
   - Error: Archive/web search tools fail
   - Response: Continue with available sources, add warning

5. **Editorial Compliance Failure**
   - Error: Score < 0.5
   - Response: Return draft with detailed warning and suggestions

## Testing Strategy

### Unit Tests
- Citation extraction and validation
- Word count accuracy
- Editorial compliance scoring
- Source tracking and matching

### Integration Tests
- Full draft generation with mock sources
- Agent tool usage verification
- Quality checks pass/fail scenarios

### Manual Testing
- Generate drafts for various topics
- Verify editorial tone matches guidelines
- Check citation accuracy
- Validate source usage tracking

### Test Cases
1. **Minimal outline** (3 sections, 3 sources)
2. **Complex outline** (8 sections, 15 sources)
3. **Web-heavy sources** (mostly web, few archive)
4. **Archive-heavy sources** (mostly archive, few web)
5. **Mixed quality sources** (high and low relevance)

## API Endpoint Design

### Endpoint: POST `/api/v1/drafts`

**Request:**
```json
{
  "headline": "AI Transforms Healthcare Diagnostics",
  "thesis": "AI is revolutionizing medical diagnostics...",
  "outline": "## Headline\n...\n## Introduction\n...",
  "sources": [...],  // From outline endpoint
  "key_facts": ["95% accuracy", "50% faster"],
  "target_word_count": 1500
}
```

**Response:**
```json
{
  "headline": "AI Transforms Healthcare Diagnostics",
  "thesis": "AI is revolutionizing...",
  "draft": "# AI Transforms Healthcare Diagnostics\n\nArtificial intelligence is...",
  "word_count": 1487,
  "sources_used": [
    {
      "title": "...",
      "source": "nature.com",
      "source_type": "web",
      "relevance_score": 0.92,
      ...
    }
  ],
  "sources_available": [...],  // Unused sources
  "sections_generated": ["Introduction", "AI Accuracy Improvements", "Speed Benefits", "Conclusion"],
  "editorial_compliance_score": 0.85,
  "warning": null
}
```

## Implementation Phases

### Phase 1: Basic Draft Generation (MVP)
- [ ] Create `draft_agent.py` with ReActAgent
- [ ] Reuse existing tools (archive + web search)
- [ ] Add citation formatter tool
- [ ] Basic editorial guidelines loading
- [ ] Simple word count validation
- [ ] Update API endpoint

### Phase 2: Quality Validation
- [ ] Implement `draft_validator.py`
- [ ] Editorial compliance scoring
- [ ] Citation validation
- [ ] Source usage tracking
- [ ] Word count adjustment logic

### Phase 3: Refinement & Optimization
- [ ] Auto-fix common citation issues
- [ ] Improve section flow and transitions
- [ ] Add topic sentence generation
- [ ] Enhance editorial tone matching
- [ ] Performance optimization

### Phase 4: Advanced Features
- [ ] Section-specific retrieval strategies
- [ ] Fact-checking tool integration
- [ ] Multiple draft versions (conservative/bold)
- [ ] Draft comparison and selection
- [ ] A/B testing framework

## Success Metrics

### Quality Metrics
- **Editorial Compliance**: > 0.8 average score
- **Citation Coverage**: 100% of factual claims cited
- **Source Diversity**: Average 5+ distinct sources per draft
- **Word Count Accuracy**: 95% within target ±10%

### Performance Metrics
- **Generation Time**: < 60 seconds for 1500 word draft
- **First Draft Quality**: 80% require minimal journalist edits
- **Source Reuse**: > 70% outline sources used in draft

### User Satisfaction
- **Journalist Feedback**: "Ready for light editing" rating > 75%
- **Time Savings**: 50%+ reduction in draft writing time
- **Accuracy**: < 5% fabricated information incidents

## Future Enhancements

### Short-term
1. **Style transfer** - Learn from published articles
2. **Quote integration** - Better handling of expert quotes
3. **Data visualization** - Generate chart descriptions
4. **Multi-language support** - Translate guidelines & drafts

### Long-term
1. **Collaborative drafting** - Multiple agents (research + writing)
2. **Real-time fact-checking** - Verify claims during generation
3. **SEO optimization** - Add keyword optimization
4. **Plagiarism detection** - Check against existing articles
5. **Voice cloning** - Match specific journalist styles

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Fabricated sources | High | Medium | Strict source validation, citation checking |
| Off-brand tone | Medium | Medium | Editorial compliance scoring, guidelines enforcement |
| Word count issues | Low | High | Automatic adjustment, warnings |
| Slow generation | Medium | Low | Caching, parallel processing, model optimization |
| Citation errors | Medium | Medium | Auto-formatting, validation tools |

## Conclusion

This agent-based draft generation system will:
- ✅ Transform outlines into publication-ready drafts
- ✅ Maintain editorial voice and quality standards
- ✅ Incorporate multi-source factual content with proper citations
- ✅ Scale intelligently from basic to advanced use cases
- ✅ Provide transparency through source tracking and compliance scoring

The architecture builds on the proven outline generation approach while adding specialized validation and quality controls to meet the higher standards required for draft articles.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Test with real outlines and sources
4. Iterate based on journalist feedback
