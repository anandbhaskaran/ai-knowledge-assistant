# AI Journalist Assistant - Technical Proposal
**Anand Bhaskaran** | November 2025

---

## Executive Summary

This proposal presents an **agent-based RAG system** that transforms editorial workflows by combining institutional archive knowledge with real-time web intelligence. The system generates evidence-backed article drafts with verifiable citations, reducing research-to-draft time from 4+ hours to <90 minutes.

**Core Innovation**: Multi-source agentic retrieval with citation integrity architecture. Unlike generic RAG systems using single databases and hard-coded pipelines, this solution deploys autonomous ReAct agents that intelligently orchestrate archive search and web research, ensuring every claim traces to verifiable sources through pre-numbered validation.

**Business Value**: 60-70% time savings • <$0.50/article cost • Scalable to 100+ journalists • 240x ROI per article

**Credibility**: Built working prototype achieving 90%+ citation accuracy, <30s latency, $0.26/article cost—validating architecture before proposing full development.

---

## 1. System Design & Architecture

**Multi-Tier Architecture**:
```
User Request → FastAPI REST → ReActAgent Orchestrator
                                    ↓
                   ┌────────────────┴────────────────┐
                   ↓                                 ↓
            Archive Tool                      Web Search Tool
         (Vector Search)                   (Real-time Intelligence)
                   ↓                                 ↓
           Qdrant Vector DB                    Tavily/Google CSE
                   └────────────┬────────────────────┘
                                ↓
                    Source Ranking & Validation
                                ↓
                         GPT-4 Synthesis
                                ↓
                    Quality Assurance Pipeline
                                ↓
                    Journalist Review Interface
```

**Why ReAct Agents?** Journalism demands multi-step reasoning: historical context (archive), recent developments (web), expert commentary, and synthesis across contradictory sources. Traditional RAG hard-codes retrieval; **ReAct agents** autonomously decide which tools to use, reformulate queries if results poor, and handle contradictions.

**Example Agent Loop**:
```
Query: "AI Impact on Central Bank Policy"
→ Thought: Need historical context
→ Action: archive_retrieval("central bank forecasting methods")
→ Observation: 3 articles (relevance: 0.89, 0.85, 0.82)
→ Thought: Need recent AI adoption data
→ Action: web_search("central banks AI machine learning 2024")
→ Observation: 5 sources (0.94, 0.91, 0.88) - Fed paper, ECB announcement
→ Thought: Contradiction detected (archive: "limited" vs. web: "widespread")
→ Action: web_search("central bank AI implementation timeline")
→ Observation: Pilots 2023, production 2024 - clarified
→ Thought: Sufficient sources (8 total, avg 0.88 relevance)
→ Action: Generate outline with synthesized narrative
```

**Advantages**: (1) Adaptive retrieval with query reformulation, (2) Multi-source intelligence, (3) Transparent reasoning, (4) Contradiction handling

**Data Pipeline**: Markdown/PDF articles → semantic chunking (1000 tokens) → OpenAI embeddings (ada-002, 1536-dim) → Qdrant vector store (HNSW, <100ms retrieval) → metadata filtering (date, source, author)

---

## 2. Tools & Technologies

| Component | Choice | Rationale | Cost/Scale | Alternative |
|-----------|--------|-----------|-----------|------------|
| **LLM** | GPT-4 | Superior reasoning for citations; function calling | ~$0.03/req | Claude 3.5 (test both) |
| **Agent Framework** | LlamaIndex ReActAgent | RAG-native, 5x faster dev vs. LangGraph | Open-source | LangGraph (Phase 3 multi-agent) |
| **Vector DB** | Qdrant | Open-source, production-ready, cloud migration path | Free→$100s/mo | Pinecone ($70+/mo, vendor lock-in) |
| **Embeddings** | OpenAI ada-002 | Industry standard, $0.0001/1k tokens | Cost-effective | Cohere (test Phase 2) |
| **Web Search** | Tavily API | LLM-optimized, $1/1000 searches | $0.05-0.10/article | Google CSE (fallback) |
| **API** | FastAPI | Type-safe, async, auto-docs | Open-source | Flask |
| **Caching** | Redis | Response caching (-40% cost Phase 2) | ~$50/mo | In-memory |
| **Monitoring** | Grafana + Langfuse | Metrics + LLM observability | ~$100/mo | Next phase |

**Strategic Decisions**:

**1. No Fine-Tuning for Initial Launch (Defer to Phase 3)**
- **Rationale**: RAG architecture better suited for journalism use case - enables real-time access to latest articles and evolving news without retraining; fine-tuning captures style/patterns but can't access new information or cite specific sources; archive content change frequently, requiring constant retraining cycles; further hosting the fine-tuned model incurs additional costs and maintenance overhead
- **Reconsider when**: (1) need to embed highly specific house style that prompting can't capture, (2) cost optimization required after validating product-market fit (fine-tuned smaller models for routine tasks), (3) ≥1,000 editor-approved articles available as training data, or (4) A/B testing shows >15% quality improvement justifies maintenance overhead

**2. Graph RAG Deferred (Phase 3)**
- I've explored and even written about [Graph RAG advantages](https://thecompoundingcuriosity.substack.com/p/rag-is-broken-we-need-connected-entities) but rejected for MVP: adds 4-6 weeks, as we will be implementing an over-engineered solution for a simpler problem
- **Reconsider** when: investigative workflows, archive >10k articles, >20% queries need relationship discovery

**3. Vendor Independence**: LlamaIndex (and LangGraph) abstractions enable LLM swapping (OpenAI ↔ Claude ↔ Llama), embedding changes, multi-search APIs without refactoring

---

## 3. Training & Fine-Tuning Strategy

**Approach**: Prompt Engineering (Phases 1-2) → Conditional Fine-Tuning (Phase 3)

**Phase 1-2: ReAct Agents with Prompt Optimization** (validated in prototype)
1. ReAct agents autonomously orchestrate archive + web search tools
2. Structured prompting with editorial guidelines
3. Pre-numbered source lists (agent can ONLY cite provided sources)
4. Self-verification checklists in prompts
5. Few-shot examples (3-5) for complex reasoning tasks

**Continuous Loop**: Feedback → Failure Analysis → Prompt Refinement → A/B Test → Production

**Expected**: 85-90% editorial quality, 90%+ citation accuracy

**Optimization Techniques Beyond current solution**:

| Technique | Impact | Phase | Complexity |
|-----------|--------|-------|------------|
| Hybrid search (vector + BM25) | +15% retrieval relevance | 2 | Medium |
| Cross-encoder reranking | +10% top-3 source quality | 2 | Low |
| Response caching | -40% API costs | 2 | Low |
| Query expansion (agent) | +20% source diversity | 1 | Low |
| Semantic chunking | +10-15% context preservation | 2 | Medium |
| Citation validation pipeline | -50% hallucinations | 1 | Medium |

**Investment Thesis**: Exhaust low-hanging optimization (caching, hybrid search, prompts) before expensive fine-tuning. Follows OpenAI recommendation: prompt engineering → RAG → fine-tuning.

---

## 4. Prompt Design Examples

### Outline Generation (Agent Orchestration)

**Design**: Explicit editorial guidelines, task decomposition (archive → web → synthesis), citation rigor, quality thresholds.

```markdown
ROLE: AI Financial Journalist Assistant creating evidence-backed outlines.

EDITORIAL GUIDELINES: {editorial_guidelines}  # RAG-loaded

ARTICLE REQUEST:
- Headline: "Central Banks Embrace AI for Inflation Forecasting"
- Thesis: "Major central banks deploy ML models reshaping monetary policy."
- Key Facts: Fed ML +15% accuracy; ECB alternative data; BoE 500+ indicators

TASK:
Step 1 - Archive: Use archive_retrieval for historical forecasting methods,
         inflation frameworks, AI monetary policy commentary
Step 2 - Web: Use web_search for recent Fed/ECB/BoE announcements, ML papers,
         market reactions (Bloomberg, FT, WSJ)
Step 3 - Generate outline: headline (60-80 chars) + intro (hook, thesis,
         100-150 words) + 3-4 body sections + visualization + conclusion

CITATION RULES:
- Format: [Source, Title, Date]
- Min 6 distinct sources (archive + web mix)
- If <4 quality sources (>0.75 relevance): "INSUFFICIENT SOURCES - gaps: [X]"

SELF-CHECK:
□ Clear argument flow  □ 2+ sources per section  □ No invented facts
□ Contradictions flagged  □ Specific visualization

Begin with archive_retrieval.
```

**Principles**: (1) Task decomposition, (2) Structural scaffolding, (3) Citation enforcement, (4) Refuse-to-generate if insufficient sources

### Draft Generation (Citation Integrity)

**Innovation**: Pre-numbered source lists prevent hallucination. Agent receives ranked sources [1-N], can ONLY cite using [N]. Prototype: 90%+ accuracy vs. 60-70% generic RAG.

```markdown
TASK: Generate 1,500-word draft from outline.

SOURCES (USE ONLY THESE):
[1] "Central Bank AI Adoption" - Bloomberg, 2024-10-15 (Score: 0.94)
    Text: "Fed ML model +15% accuracy vs. traditional econometric..."
[2] "Phillips Curve Limits" - Archive, 2023-08-12 (Score: 0.89)
    Text: "Correlation dropped to 0.23 from historical 0.67..."
[3-12 additional sources...]

STRUCTURE:
# {Headline}
**Lead (30-50 words)**: Critical development, who's affected, why now
## Intro (100-150 words) [Every claim → [N]]
## Body sections (250-300 words each) [Stats, quotes → [N]]
## Conclusion (150-200 words)

CITATION RULES (CRITICAL):
1. Every claim MUST have [N] where N = source number 1-12
2. ONLY use provided sources - no external knowledge
3. Direct quotes: quotation marks + [N]
4. Min 10 citations distributed (not clustered)
5. Min 2 direct quotes

SELF-CHECK:
□ 1,400-1,600 words  □ Every claim cited  □ 2+ quotes
□ All [N] in 1-12 range  □ No invented sources
```

**Why It Works**: Constrained generation, built-in verification, format enforcement, quality gates

---

## 5. Success Metrics

| Metric | Target | Measurement | Rationale |
|--------|--------|-------------|-----------|
| **Citation Accuracy** | ≥90% | Manual verification: 50 drafts × 10 citations | Editorial credibility. |
| **Factual Correctness** | ≥85% | Expert review: 30 drafts, rate claims | Trustworthy content. <85% = too much editing. |
| **Outline-Topic Alignment** | ≥4.0/5 | Journalist rating (n=20) | User satisfaction. <4.0 = defeats purpose. |
| **Time Savings** | ≥60% | 4hr manual → <90min AI (n=10, 5 articles each) | ROI: 2.4hr × $50/hr = $120 vs. $0.50 cost. |
| **Outline Latency (P95)** | <90s | API monitoring | >90s = attention loss. |
| **Draft Latency (P95)** | <60s | API monitoring | Acceptable wait. |
| **Cost per Article** | <$0.50 | Track API costs per request | $0.50 vs. $120 labor = 240x ROI. Prototype: $0.26. |
| **Human Override** | <15% | % flagged "poor quality" and abandoned | >15% = trust breakdown. |

**Continuous Evaluation using Grafana and Langfuse**:
- **Automated**: Citation accuracy, relevance scores, latency (P50/P95/P99), cost, error rates
- **Human**: Editorial quality ratings, factual correctness, bias detection, NPS surveys
- **Loop**: Feedback → Failure Analysis → Hypothesis → Staging → A/B Test (20%) → Production

---

## 6. Implementation Roadmap

**Phase 0: Prototype (Completed)** - A demoable prototype validating architecture

**Phase 1: Production MVP**
- Authentication + Other infra (Kubernetes, CI/CD, monitoring)
- Grafana + Langfuse observability (100% tracing)
- Safety guardrails (bias detection, PII redaction)
- Granular citations, preview popups (>4.0/5 feedback)
- Automated evaluation (500 drafts baseline)
- Pilot launch (10-20 journalists, 80% weekly active, <15% override)

**Phase 2: Scale & Optimization** 

| Feature | Value | Approach | Metric |
|---------|-------|----------|--------|
| Hybrid search | +15% quality | BM25 + vector + cross-encoder | Relevance 0.85→0.95 |
| Multi-draft comparison | Better choice | 2-3 angles, journalist selects | +20% satisfaction |
| Fact-checking agent | Fewer errors | Cross-reference claims vs. sources | 85%→92% correctness |
| Version history | Collaboration | Track revisions, compare | 50% adoption |
| Chat with Archive | Better quality publication | Implement chat interface with memory | user engagement |

**Phase 3: Further enhancements** 
| Feature | Moat | Implementation | Metric |
|---------|------|----------------|--------|
| Multi-language | International expansion | 3 languages via GPT-4 | 20% non-English usage |
| Source relationships | Investigative workflows | Graph RAG (optional) | 10% use relationship queries |
| Analytics dashboard | Editorial insights | Trending topics, coverage gaps | 80% editor adoption |

---

## 7. Risks & Mitigation

| Risk | Impact | Technical Mitigation | Operational Mitigation | Residual |
|------|--------|---------------------|----------------------|----------|
| **Hallucinated Citations** | Critical | Pre-numbered sources (agent can't invent), validation pipeline | Mandatory human review, feedback loop | Low (90%+ accuracy) |
| **Poor Retrieval** | High | Relevance filtering (>0.75), refuse if <4 sources, hybrid search (Phase 2) | User feedback, archive audits | Medium (Phase 2 reduces) |
| **API Downtime** | High | Graceful degradation (archive-only), retry logic, multi-provider failover | Status monitoring, incident playbook | Medium (external dependency) |
| **Cost Overruns** | Medium | Caching (-40% Phase 2), prompt optimization, rate limiting | Daily budget alerts, quota systems | Low ($0.26 validated) |
| **Bias in Content** | Critical | Diverse archive, bias detection models, prompt guardrails | Editorial review, bias audits, training | Medium (human catches most) |
| **Over-Reliance on AI** | Critical | Position as "assistant" in UX, preserve journalist control | Training on AI limitations, quality incentives | Medium (cultural challenge) |

**Technical Debt** (with payoff plan):
1. Vector-only search → Phase 2 Month 5: Add BM25 + reranking when >10% queries <0.70 relevance
2. Manual evaluation → Phase 1 Month 9: Automated pipeline after 100+ labeled examples
3. Single agent → Phase 3: Multi-agent only if data shows clear bottlenecks

**Competitive Advantage**: Most AI journalism tools prioritize speed over trust. Citation integrity + human review = credibility over throughput.

---

## 8. Conclusion

**Why This Wins**:

1. **Architecture Validated**: Prototype shows great outcomes with easy to use interface
2. **Strategic Choices**: Rejected Graph RAG, deferred fine-tuning, chose ReActAgent, vendor-independent abstractions with LlamaIndex
3. **Journalist-Centric**: Transparent sourcing (pre-numbered citations, reasoning logs), quality thresholds (refuse if insufficient sources), human-in-loop design
4. **Improves productivity**: Facilitate ideation for journalists, streamline research, sparing partner for journalists 

**Differentiation vs. Generic RAG**:

| Dimension | This Solution | Typical RAG | Advantage |
|-----------|---------------|-------------|-----------|
| Intelligence | Autonomous agent: archive + web + future tools | Single DB, hard-coded | Comprehensive research in one query |
| Trust | Pre-numbered validation: 90%+ accuracy | Generic sources: 60-70% | Editorial credibility, legal risk reduction |
| Adaptability | Editorial guidelines | Hard-coded prompts | Scales across publications |
| Cost Control | Optional web search, caching roadmap | Always-on APIs | Flexible cost/quality trade-off |
| Transparency | Agent reasoning logs visible | Black-box | Journalists understand WHY |


**Contact**: Anand Bhaskaran | [GitHub](https://github.com/anandbhaskaran/ai-knowledge-assistant) | [Writing](https://thecompoundingcuriosity.substack.com)
