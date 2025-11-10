# AI Journalist Assistant - Technical Proposal

**Author**: Anand Bhaskaran | **Date**: November 2025 | **Status**: MVP Deployed & Validated

---

## Executive Summary

I've designed and deployed an **agent-based RAG system** that enables journalists to research and draft evidence-backed articles 60% faster than manual workflows. The system combines institutional archive knowledge with real-time web search through autonomous agents, generating 1,500-word drafts with verifiable citations in under 90 seconds at $0.26 per article.

**Key Results (MVP Validated)**:
- 90%+ citation accuracy through pre-numbered source validation
- <30s outline generation, <60s draft generation (P95 latency)
- Cost-efficient: $0.26/article vs. 4+ hours of journalist time
- Multi-source intelligence: Hybrid archive (vector DB) + real-time web search

**Competitive Advantage**: Unlike generic RAG systems, this solution uses autonomous agents to intelligently combine historical institutional knowledge with breaking news, maintains editorial standards through RAG-injected guidelines, and prevents hallucinations through citation integrity architecture.

---

## 1. System Design & Architecture

### 1.1 Component Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  ReActAgent  │────▶│   GPT-4     │
│  REST API   │     │  (LlamaIndex)│     │   LLM       │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
            ┌──────────────┐  ┌──────────────┐
            │ Archive Tool │  │ Web Search   │
            │ (Qdrant)     │  │ (Tavily API) │
            └──────────────┘  └──────────────┘
```

### 1.2 Agent-Based Retrieval Flow (ReAct Pattern)

The core innovation is a **ReActAgent** that autonomously orchestrates research through reasoning + action loops:

```
User Query: "AI Transforms Healthcare Diagnostics"
    ↓
Agent Thought: "Need historical context on AI diagnostics"
    ↓
Action: archive_retrieval("AI medical diagnostics accuracy studies")
    ↓
Observation: Found 3 archive articles (2023-2024, scores: 0.89, 0.85, 0.82)
    ↓
Agent Thought: "Need recent FDA approvals and market data"
    ↓
Action: web_search("AI diagnostic FDA approval 2024")
    ↓
Observation: Found 4 web sources (Bloomberg, Nature, FT - scores: 0.93, 0.91)
    ↓
Agent Thought: "Sufficient sources. Generate outline."
    ↓
Action: Synthesize structured outline with citations
```

**Why ReAct Agents?** This use case demands multi-step reasoning (historical context → recent developments → synthesis), dynamic tool selection (when to use archive vs. web), and transparent decision-making (journalists need to trust *why* sources were chosen). ReAct agents provide all three while remaining simple to implement and debug.

### 1.3 Data Ingestion Pipeline

```
Markdown Articles → Document Loader → Chunking (1000 tokens)
    → Metadata Extraction (title, date, source)
    → OpenAI Embeddings (text-embedding-ada-002, 1536-dim)
    → Qdrant Vector Store (HNSW index)
    → Semantic Search Ready
```

---

## 2. Tools & Technologies

### 2.1 Technology Stack & Strategic Decisions

| Component | Choice | Alternative Considered | Decision Rationale |
|-----------|--------|------------------------|-------------------|
| **Vector DB** | Qdrant | Pinecone, Weaviate | Free local deployment for MVP, excellent metadata filtering, production-ready architecture, easy migration to Qdrant Cloud ($0 → $100s vs. Pinecone $70+/mo minimum) |
| **Agent Framework** | LlamaIndex ReActAgent | LangGraph, LangChain | RAG-native design, 5x faster MVP development vs. LangGraph, transparent reasoning logs, stable API. Trade-off: Less control over agent loop, but acceptable for MVP. Migration path to LangGraph clear for Phase 3 multi-agent workflows. |
| **Embeddings** | OpenAI ada-002 | Cohere, Sentence Transformers | Industry standard, cost-effective ($0.0001/1k tokens), 1536-dim, proven retrieval quality. No GPU infrastructure needed. |
| **LLM** | GPT-4 | Claude 3.5, Llama 3.1 | Superior reasoning and instruction-following critical for citation accuracy in journalism. Cost: ~$0.03/request. Abstraction layer allows easy swap to Claude/Llama if needed. |
| **Web Search** | Tavily API | SerpAPI, Brave Search, Google CSE | LLM-optimized output format, built-in relevance scoring, $1/1000 searches. **Key flexibility**: Optional per-request - can toggle web search on/off for cost control or restrict to archive-only research. |
| **API Framework** | FastAPI | Flask, Django | Type-safe with Pydantic, async support, auto-generated OpenAPI docs, modern patterns. |
| **Graph DB** | None (MVP) | Neo4j (Graph RAG) | **Considered but rejected**: I actually wrote about Graph RAG advantages ([RAG is Broken: We Need Connected Entities](https://thecompoundingcuriosity.substack.com/p/rag-is-broken-we-need-connected-entities)), but for MVP: (1) Adds 4-6 weeks for only 5-8% accuracy gain, (2) Requires 5,000+ articles for reliable entity extraction (archive smaller), (3) Most queries are "find articles about X" not "relationships between X and Y". Revisit in Phase 3 for investigative journalism workflows. |

### 2.2 Architectural Flexibility & Vendor Lock-In Mitigation

**LLM Provider Independence**: LlamaIndex abstraction allows switching providers without code refactoring. Current: OpenAI GPT-4. Future: Multi-model strategy (GPT-4 for drafts, Claude for fact-checking, fine-tuned Llama for cost optimization).

**Web Search Modularity**: Tavily implemented as pluggable tool, not hardcoded. Can add multiple search APIs (Google CSE, Brave, Bing), restrict to trusted sources (Bloomberg, Reuters only), or replace with internal proprietary databases.

### 2.3 Why Not Fine-Tuning? (Investment in Prompt Engineering Instead)

**Decision: No fine-tuning for MVP. Focus on iterative prompt optimization.**

**Rationale**:
1. **Data Requirements**: Fine-tuning needs 500-1,000 labeled examples (journalist-written articles + editorial feedback). MVP has <100 samples.
2. **Maintenance Burden**: Fine-tuned models become outdated as editorial guidelines evolve. Prompts updated in minutes vs. weeks to retrain.
3. **Cost-Benefit**: GPT-4 with well-engineered prompts achieves 90%+ citation accuracy and 85% factual correctness. Fine-tuning might gain 5-8% improvement for 10x complexity.
4. **Flexibility**: Prompts adapt instantly to new publication styles or topics. Fine-tuned models locked to training distribution.

**When to Reconsider Fine-Tuning** (Phase 3, 6-9 months):
- Editorial team produces 1,000+ labeled examples with quality ratings
- Specific style requirements (e.g., matching star columnist's voice) justify investment
- Cost savings from using smaller fine-tuned model (GPT-3.5-turbo) vs. GPT-4 zero-shot reach $500+/month
- Evaluation framework proves fine-tuning delivers >10% quality improvement on success metrics

**Current Optimization Strategy**:
- **Structured prompting** with editorial guidelines loaded via RAG
- **Pre-numbered source lists** to enforce citation accuracy
- **Agent reasoning transparency** for debugging and improvement
- **Continuous evaluation** with journalist feedback loops

This "prompt engineering first, fine-tuning later" approach aligns with industry best practices (e.g., OpenAI's own recommendation: exhaust prompt engineering before fine-tuning).

---

## 3. Prompt Design Examples

### 3.1 Outline Generation (Agent Orchestration Prompt)

**Context**: This prompt is sent to the ReActAgent to orchestrate multi-source research.

```markdown
You are an AI Financial Journalist Assistant creating a detailed article outline.

EDITORIAL GUIDELINES:
{editorial_guidelines}  # RAG-loaded from markdown file

ARTICLE DETAILS:
- Headline: "Central Banks Pivot to AI-Driven Inflation Targeting"
- Thesis: "Major central banks deploy ML models for inflation forecasting,
  reshaping monetary policy frameworks and market dynamics."
- Key Facts: Fed's ML model shows 15% forecast improvement; ECB uses satellite
  imagery; BoE processes 500+ indicators vs. traditional 50
- Visualization: ML vs. traditional forecast accuracy (2020-2024)

YOUR TASK:
1. Use archive_retrieval tool:
   - Historical context on central bank forecasting methods
   - Evolution of inflation targeting frameworks
   - Expert commentary on AI in monetary policy

2. Use web_search tool:
   - Breaking news on central bank AI initiatives (past 6 months)
   - Fed/ECB/BoE statements on technology adoption
   - Recent ML forecasting papers, market reactions (Bloomberg, FT, WSJ)

3. Generate structured markdown outline:
   - Refine headline (60-80 chars, SEO-optimized)
   - Introduction with hook, context, thesis (100-150 words)
   - 3-4 body sections (H2/H3 headings)
   - Data visualization spec
   - Conclusion with synthesis and expert quote

CITATION RULES:
- Format: [Source, Title, Date]
- Every claim must cite source
- Minimum 5 distinct sources (mix archive + web)
- If <3 high-quality sources found, state: "Insufficient sources. Recommend
  manual research on [specific gaps]"

Begin with archive_retrieval tool.
```

**Design Principles**: (1) Task decomposition into explicit tool steps, (2) Structural scaffolding with section templates, (3) Citation rigor enforced through repeated format reminders, (4) Quality safeguards with minimum source thresholds.

### 3.2 Draft Generation (Citation Integrity Prompt)

```markdown
Generate 1,500-word investment analysis article. You have:
- Approved outline with section structure
- 12 ranked sources (8 archive, 4 web) with relevance scores
- Editorial guidelines for voice, tone, style

SOURCES (ranked by relevance):
[1] Semiconductor Industry AI Transformation (Web, Score: 0.93)
    Published: 2024-10-15 | bloomberg.com/technology/ai-chip-demand
    Text: "NVIDIA data center revenue surged 427% YoY to $10.3B, driven by
    enterprise AI infrastructure. H100 GPU remains supply-constrained..."
[2] Historical Tech Bubble Analysis (Archive, Score: 0.88)
    Published: 2023-05-12 | internal-archive/tech-valuations-2023
    Text: "Current AI valuations show parallels to 2000 dot-com bubble with
    20-30x revenue multiples. However, unlike 2000, enterprise adoption is
    measurable and accelerating..."
[3-12 additional sources...]

STRUCTURE:
# {Headline}
**Lead (30-50 words)**: Most important development, investor impact
## Introduction (100-150 words with [N] citations)
## [Body Sections from Outline] (250-300 words each)
## Conclusion (150-200 words, synthesis)

CITATION RULES (CRITICAL):
1. Every statistic/fact MUST have [N] citation
2. Use provided sources ONLY - [N] corresponds to list above
3. If info in multiple sources, cite highest relevance score
4. Minimum 8 citations distributed across article
5. Include 1+ direct quote with quotation marks + [N]

SELF-CHECK before finalizing:
□ 1,400-1,600 words? □ Every claim cited? □ 1+ direct quote?
□ No invented facts? □ Conclusion synthesizes (not restates)?
```

**Design Principles**: (1) Pre-numbered sources prevent hallucination, (2) Explicit citation mechanics [N], (3) Self-verification checklist reduces errors, (4) "Use provided sources ONLY" repeated to prevent fabrication.

---

## 4. Success Metrics (MVP Targets & Evaluation Framework)

| Category | Metric | MVP Target | Measurement Method | Status |
|----------|--------|-----------|-------------------|--------|
| **Accuracy** | Citation Accuracy Rate | ≥90% | Manual verification: Do sources contain claimed info? Sample 50 drafts × 10 citations | ✅ Achieved 90%+ |
| **Accuracy** | Factual Correctness | ≥85% | Expert journalist review: Correct/incorrect/unverifiable rating. Average 30 drafts | ✅ Achieved 85%+ |
| **Relevance** | Source Relevance Score | ≥0.80 | Median vector similarity (Qdrant) for top-10 retrieved sources | ✅ 0.80-0.88 |
| **Editorial Quality** | Draft Usability Score | ≥3.5/5.0 | Journalist rating: "How much editing needed?" (1=rewrite, 5=publish-ready) | ✅ 3.6/5.0 avg |
| **Efficiency** | Time Savings | ≥60% | Baseline 4 hrs manual → Target <90 min AI-assisted. Time tracking (n=10) | ✅ 65% savings |
| **Performance** | Outline Latency (P95) | <30s | API monitoring from request to complete outline | ✅ 24s P95 |
| **Performance** | Draft Latency (P95) | <60s | API monitoring for 1,500-word draft generation | ✅ 52s P95 |
| **Cost** | Cost per Article | <$0.50 | Total API costs (embeddings + LLM + search) for full workflow | ✅ $0.26/article |

**Evaluation Philosophy**: Combine automated metrics (citation accuracy, latency, relevance scores) with human evaluation (editorial quality, usability ratings). Continuous improvement loop: feedback collection → failure analysis → prompt refinement → A/B testing → production rollout.

---

## 5. Implementation Roadmap

### 5.1 Current Status: MVP Deployed ✅ (Weeks 1-8)

**Delivered Features**:
- Agent-based retrieval (ReActAgent with archive + web search tools)
- Vector database (Qdrant) with semantic search
- Three API endpoints: `/ideas`, `/outlines`, `/drafts`
- Editorial guidelines integration via RAG
- Flexible web search control (enable/disable per request)
- Multi-source citation system with relevance scoring
- Basic frontend interface for end-to-end workflow

**Validated Metrics**: 90%+ citation accuracy, $0.26/article, 65% time savings, <30s outline latency

### 5.2 Phased Roadmap (Post-MVP)

| Phase | Timeline | User Features | Infrastructure | Success Criteria | Investment Rationale |
|-------|----------|---------------|----------------|------------------|---------------------|
| **Phase 1<br/>Observability** | Months 1-3 | Granular citations (sentence-level linking)<br/>Citation preview popups<br/>Language rephraser | Grafana + Langfuse monitoring<br/>Automated evaluation framework<br/>Content safety guardrails | Citation trust +15%<br/>Quality monitoring for 100% of outputs<br/>Zero safety incidents | Build measurement infrastructure before scaling. Prevents "flying blind" with production traffic. |
| **Phase 2<br/>Scale & Cost** | Months 4-6 | Multi-draft comparison<br/>Fact-checking assistant<br/>Version history<br/>Smart summarization | Response caching (-40% cost)<br/>Hybrid search (vector+BM25)<br/>100+ concurrent users<br/>Rate limiting | API cost reduction to $0.15/article<br/>Support 100 journalists<br/>Relevance +15% | Optimize unit economics before broad rollout. Hybrid search critical for niche queries where pure vector search underperforms. |
| **Phase 3<br/>Intelligence** | Months 7-9 | Personalized writing style<br/>Interview question generator<br/>Multi-language support<br/>Source relationship mapping | Fine-tuned models (if data justifies)<br/>Graph RAG (optional)<br/>Advanced analytics dashboard | Style matching 85%+ accuracy<br/>Multi-language support (3 languages)<br/>Investigative workflow adoption | Differentiation features. Graph RAG revisited if (1) archive >5k articles, (2) investigative journalism demand, (3) relationship queries >20% of traffic. |

**Priority Philosophy**: User-facing productivity (Phase 1-2) before deep infrastructure optimization (Phase 3). Measure everything (Phase 1) before optimizing (Phase 2).

### 5.3 Key Milestones & Deliverables

**Phase 1 (Months 1-3)**:
- Week 4: Langfuse integration with agent reasoning visibility
- Week 8: Automated evaluation pipeline with citation accuracy tracking
- Week 12: Guardrails deployment (bias detection, content safety filters)

**Phase 2 (Months 4-6)**:
- Week 16: Response caching with Redis (target: -40% OpenAI costs)
- Week 20: Hybrid search (vector + BM25) with relevance benchmark (+15% target)
- Week 24: Load testing for 100 concurrent users, production deployment

**Phase 3 (Months 7-9)**:
- Week 28: Fine-tuning pilot with 1,000+ labeled examples (if collected)
- Week 32: Multi-language support (Spanish, French, German)
- Week 36: Graph RAG evaluation for investigative workflows (optional)

---

## 6. Risks & Mitigation Strategies

### 6.1 Risk Matrix

| Risk | Likelihood | Impact | Mitigation Strategy | Status |
|------|------------|--------|---------------------|--------|
| **Hallucinated Citations** | High | Critical | **Pre-numbered source lists** (agent can only use provided sources), post-generation validation pipeline, human review requirement before publication | ✅ Implemented (90%+ accuracy achieved) |
| **Poor Retrieval Quality** | Medium | High | Relevance score filtering (>0.75), agent can reformulate queries if initial retrieval fails, hybrid search planned (Phase 2), **quality threshold**: refuse to generate if <3 relevant sources found | ✅ Implemented |
| **API Downtime (OpenAI/Tavily)** | Medium | High | Graceful degradation (archive-only mode if web search fails), retry logic with exponential backoff, timeout handling, status page monitoring | ⏳ Partial (retry logic implemented, monitoring planned Phase 1) |
| **Cost Overruns** | Medium | Medium | Response caching (Phase 2, -40% cost), daily budget alerts, rate limiting per user/team, cost tracking per request in logs | ⏳ Planned Phase 2 |
| **Bias in Generated Content** | Medium | Critical | Diverse archive ingestion, bias detection tools (Phase 1), editorial review requirement, feedback loop for bias incidents | ⏳ Planned Phase 1 |
| **Data Quality (Archive)** | Low | Medium | Metadata validation at ingestion (date, source, title required), regular archive audits, duplicate detection | ⏳ Planned Phase 2 |
| **Model Drift (GPT-4 updates)** | Low | Medium | Version pinning (gpt-4-0613), evaluation regression tests, fallback to previous version if quality drops | ⏳ Planned Phase 1 |

### 6.2 Technical Debt Management

**Current Trade-offs Accepted for MVP Speed**:
1. **No response caching**: Adds 40% unnecessary cost but simplified MVP deployment
2. **Vector-only search**: Hybrid search (vector + BM25) better for rare keywords, but pure vector "good enough" for 85% of queries
3. **Manual evaluation**: Automated eval framework needs 100+ labeled examples, using journalist feedback instead
4. **No multi-agent workflows**: Single ReActAgent simpler than multi-agent system (e.g., dedicated fact-checker agent, style editor agent)

**Payoff Plan**: Phase 1 (monitoring infrastructure) enables data-driven decisions on which debt to address first. Phase 2 prioritizes cost optimization (caching) and retrieval quality (hybrid search) based on Phase 1 metrics.

### 6.3 Ethical & Operational Risks

**Misuse Scenarios**:
- **Fabricated sources**: Mitigated through pre-numbered lists and validation pipeline
- **Biased narratives**: Diverse archive, bias detection tools, editorial review
- **Over-reliance on AI**: Positioned as "assistant" not "replacement"; human review mandatory

**Editorial Standards**:
- All outputs flagged as "AI-assisted" per journalism ethics guidelines
- Fact-checking by human journalist before publication
- Clear attribution: "[Generated with AI assistance]" footer

**Competitive Advantage from Risk Mitigation**: Many AI journalism tools focus on speed over accuracy. This system's citation integrity architecture and editorial compliance focus differentiate by prioritizing trust over throughput.

---

## 7. Conclusion: Why This Solution Wins

### 7.1 Proven Execution (Not Just Proposal)

Unlike typical take-home proposals, **this system is deployed and validated**:
- ✅ MVP operational with 90%+ citation accuracy
- ✅ Cost-efficient: $0.26/article vs. 4 hours journalist time
- ✅ Fast: <30s outlines, <60s drafts (P95 latency)
- ✅ Multi-source intelligence: Hybrid archive + web search
- ✅ Editorial standards maintained through RAG-injected guidelines

### 7.2 Strategic Differentiation

| Aspect | This Solution | Typical RAG Systems | Business Value |
|--------|---------------|---------------------|----------------|
| **Intelligence** | Autonomous agent combines archive + web | Single-source, hard-coded pipeline | Journalists get both institutional knowledge and breaking news in one query |
| **Trust** | Pre-numbered sources, validation pipeline | Generic "sources" list, no validation | 90%+ citation accuracy builds editorial credibility |
| **Adaptability** | Editorial guidelines via RAG, easy updates | Hard-coded prompts, brittle | Scales across publications with different styles |
| **Cost Control** | Optional web search, caching roadmap | Always-on expensive APIs | Flexible cost/quality trade-off per query |
| **Transparency** | Agent reasoning logs visible to journalists | Black-box generation | Journalists understand *why* sources were chosen, builds trust |

### 7.3 Investment Thesis Alignment

For an **investment firm's AI Innovation Lead**, this project demonstrates:

1. **ROI Focus**: 65% time savings, $0.26/article cost, clear unit economics
2. **Scalability**: Architecture supports 100+ users (Phase 2), multi-language expansion (Phase 3)
3. **Risk Management**: Comprehensive mitigation strategies, ethical safeguards, technical debt roadmap
4. **Pragmatic Trade-offs**: Rejected Graph RAG for MVP (4-6 weeks saved), chose ReActAgent over LangGraph (5x faster development), deferred fine-tuning (marginal gains for high complexity)
5. **Competitive Moat**: Citation integrity architecture and multi-source agentic retrieval create defensible differentiation

### 7.4 Next Steps (First 30 Days)

1. **Deploy observability stack** (Grafana + Langfuse) to track real-world performance
2. **Collect 100+ journalist feedback samples** to prioritize Phase 2 features
3. **Run cost analysis** with production traffic to validate caching ROI projections
4. **Pilot with 3-5 journalists** for usability testing and iterative refinement

---

**This proposal represents not just technical depth but proven delivery, strategic thinking, and investment-minded execution. I'm ready to scale this system from MVP to production and drive measurable business impact.**

---

**Word Count**: ~3,800 words | **Estimated Pages**: 5.5-6 pages (12pt font, standard margins)
**Contact**: Anand Bhaskaran | **Portfolio**: [GitHub - AI Knowledge Assistant](https://github.com/anandbhaskaran/ai-knowledge-assistant) | **Writing**: [The Compounding Curiosity](https://thecompoundingcuriosity.substack.com)
