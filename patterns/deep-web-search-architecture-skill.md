---
name: deep-web-search-architecture
description: >
  Teaches AI agents the full internal pipeline of production-grade deep web
  search systems — from query intake to grounded response generation. Activate
  when building RAG pipelines, engineering search queries, designing retrieval
  systems, or needing to understand how semantic search, vector embeddings,
  hybrid retrieval, Cross-Encoder reranking, and context injection work end to
  end. Trigger on: "deep web search", "RAG pipeline", "semantic search",
  "vector retrieval", "reranking", "query engineering", "context injection",
  "web search architecture", "how does search work", or any request to build
  or improve a retrieval-augmented generation system.
---

# SKILL: Deep Web Search Architecture
**Version:** 1.0  
**Author:** OVERLORD Empire  
**Purpose:** Teach AI agents the full internal pipeline of production-grade deep web search systems — from query intake to grounded response generation. Use this to engineer better queries, interpret search results intelligently, and build RAG pipelines that mirror how top-tier search systems operate.

---

## WHAT THIS SKILL COVERS

This skill covers the four-phase pipeline behind deep, semantic web search:

1. **Intent Parsing & Query Generation** — Deconstructing messy user prompts into optimized, parallel search queries
2. **Massive-Scale Live Retrieval** — Hybrid search (sparse + dense) across a live web index
3. **Deep Read: Extraction & Reranking** — Semantic chunking + Cross-Encoder precision scoring
4. **Grounding & Generation** — Context injection, conflict resolution, and grounded synthesis

---

## PHASE 1 — INTENT PARSING & QUERY GENERATION

Never pass a raw user prompt directly to a search engine. Conversational language is messy — full of pronouns, implied context, and temporal assumptions.

### Steps:
1. **Deconstruct the prompt** — Extract:
   - Core intent (what does the user actually want to know?)
   - Temporal constraints (is this about current/live data? What year?)
   - Implicit background assumptions
   - Entity references (people, companies, tools, events)

2. **Generate multiple parallel queries** — Break complex requests into 3–5 distinct, optimized sub-queries attacking the problem from different angles simultaneously. Do NOT rely on a single query.

### Example:
> User: "How is the Fed affecting crypto right now?"  
> Generated queries:
> - "Federal Reserve interest rate decision 2026"
> - "crypto market response Fed rate hike June 2026"
> - "Bitcoin price Fed monetary policy correlation"
> - "DeFi liquidity impact interest rates 2026"

---

## PHASE 2 — MASSIVE-SCALE LIVE RETRIEVAL (THE WIDE NET)

**Goal: Maximum Recall** — capture every potentially relevant page before narrowing down.

### 2.1 — Hybrid Search (Dual-Track Index)

Run **two retrieval methods in parallel** and fuse their results:

#### Track A: Sparse Retrieval (Lexical / BM25)
- Exact keyword and phrase matching
- Frequency and document length weighting
- Best for: specific error codes, product names, unique identifiers, technical terms
- **Use when precision of wording matters**

#### Track B: Dense Retrieval (Bi-Encoder / Semantic)
- Web pages are pre-embedded into high-dimensional vector space (768–1536 dimensions)
- The query is also embedded into the same space at runtime
- Finds pages that **mean the same thing**, even if they use different words
- **Use when conceptual understanding matters over exact match**

### 2.2 — Vector Space Matching

The Bi-Encoder converts your query into a vector **v_q** and compares it to pre-computed document vectors **v_d** using:

```
Similarity(q, d) = (v_q · v_d) / (||v_q|| × ||v_d||)
```

This is **Cosine Similarity** — it measures the geometric angle between two meaning-vectors.

To do this across billions of documents fast, use **Approximate Nearest Neighbor (ANN)** algorithms — specifically **HNSW (Hierarchical Navigable Small World)** — which navigate a multi-layer graph in logarithmic time to reach the nearest semantic cluster.

### 2.3 — Reciprocal Rank Fusion (RRF)

Merge the ranked outputs of both tracks:

```
RRF_Score(d) = Σ 1 / (k + rank_i(d))
```

Where `k` is a smoothing constant (typically 60) and `rank_i` is the document's position in each track's results.

**Output:** A fused, normalized candidate pool of ~50–100 document URLs.

---

## PHASE 3 — THE DEEP READ: EXTRACTION & RERANKING (THE PRECISION LENS)

**Goal: Maximum Precision** — from 100 candidates, extract only the 3–7 most fact-dense, query-relevant chunks.

### 3.1 — Dynamic Semantic Chunking

Strip raw HTML down to clean text, then chunk it intelligently:

- **Chunk size:** 100–500 tokens per chunk
- **Overlapping chunks:** e.g., 500 characters with 100-character overlap to preserve context at boundaries
- **Semantic boundaries:** Use a sliding semantic distance tracker — when paragraph topic shifts sharply, draw a chunk boundary. Never cut mid-thought.
- **Discard:** Navigation menus, footers, ads, cookie banners, sidebars

### 3.2 — Cross-Encoder Reranking (The Microscope)

This is the most computationally expensive and most important step.

**Bi-Encoder vs. Cross-Encoder:**

| Feature | Bi-Encoder (Phase 2) | Cross-Encoder (Phase 3) |
|---|---|---|
| Processing | Query & document encoded **separately** | Query & document processed **jointly** |
| Attention | No cross-token attention between query and doc | Full multi-head self-attention across both |
| Speed | Fast (vector math at query time) | Slow (full transformer forward pass per chunk) |
| Goal | Broad Recall (top 100) | Precision Targeting (top 3–7) |

**Cross-Encoder input format:**
```
[CLS] + [Query text] + [SEP] + [Document chunk text] + [SEP]
```

By processing them together, every token in the query attends to every token in the document — enabling the model to detect:
- Double negatives
- Conditional logic ("if X but only when Y")
- Structural and positional context

**Output:** A relevance score between 0 and 1 per chunk.

### 3.3 — Pruning & Final Selection

1. Sort all chunks by their Cross-Encoder relevance score (descending)
2. Discard anything below a strict relevance threshold
3. Keep only the **top 3–7 chunks** — the elite tier of fact-dense paragraphs
4. These surviving chunks are injected into the LLM's context window

---

## PHASE 4 — GROUNDING & GENERATION

### 4.1 — Context Injection

The LLM's prompt is dynamically restructured:

```
"You are an expert. Using the following verified facts retrieved from the live web:
[Chunk 1 — Relevance: 0.97]
[Chunk 2 — Relevance: 0.91]
[Chunk 3 — Relevance: 0.88]
Answer the user's query accurately. If sources conflict, prioritize the most recent and authoritative."
```

This is an **open-book exam** — the LLM doesn't need to recall facts from training data; it synthesizes from injected evidence.

### 4.2 — Conflict Resolution & Synthesis

When two sources contradict each other:
- Assess source authority (domain trust, publication date, author credentials)
- Weight more recent data for time-sensitive topics
- Synthesize a single coherent answer — do NOT just repeat both claims
- Cite sources for transparency where possible

---

## OPERATIONAL RULES FOR AGENTS USING THIS SKILL

1. **Never send raw user prompts to search** — always parse intent and generate optimized sub-queries first
2. **Always use hybrid search** (sparse + dense) for best recall — never rely on one method alone
3. **Never dump full web pages into context** — always chunk and rerank first
4. **Cross-Encoder is expensive — use it only on the top 50–100 candidates from Phase 2**
5. **Inject only top 3–7 chunks** into the LLM context — more than this causes context stuffing and degraded performance
6. **For time-sensitive queries**, include year/date in sub-queries explicitly and filter by recency in ranking
7. **For exact-match queries** (error codes, names, IDs), weight sparse retrieval (BM25) higher than dense
8. **For conceptual/intent queries**, weight dense retrieval (Bi-Encoder) higher than sparse

---

## KEY TERMS GLOSSARY

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — grounding LLM output in live retrieved facts |
| **Bi-Encoder** | Embeds query and documents independently; fast but less precise |
| **Cross-Encoder** | Processes query + document jointly; slow but highly precise |
| **BM25** | Sparse keyword-matching algorithm using term frequency and document length |
| **HNSW** | Hierarchical Navigable Small World — graph-based ANN algorithm for fast vector search |
| **Cosine Similarity** | Geometric angle between two vectors; measures semantic closeness |
| **RRF** | Reciprocal Rank Fusion — method for merging ranked lists from multiple retrieval tracks |
| **Semantic Chunking** | Topic-aware text splitting that preserves meaning at chunk boundaries |
| **Context Stuffing** | Degraded LLM performance caused by injecting too much text into the context window |
| **ANN** | Approximate Nearest Neighbor — fast algorithm for finding closest vectors in large spaces |

---

## SOURCE
Adapted from: *Deep Web Search Architecture Conversation with Gemini (2026)*  
Empire Reference: `Deep-Web-Search-Query.md`
