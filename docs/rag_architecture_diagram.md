# RAG Retrieval Strategy: Semantic Disambiguation

## The Challenge: Semantic Ambiguity
**User Query:** "Erkläre mir das Perfekt" (Explain the perfect tense)
**Issue:** Standard dense retrieval often selects "Präsens" (present tense) due to high vector similarity in the latent space (both are grammatical tenses with similar structural contexts), failing to distinguish the specific semantic intent.

## The Solution: Two-Stage Pipeline

To address this, we implement a specific enhancement to the retrieval pipeline:

1.  **Query Expansion via HyDE (Hypothetical Document Embeddings):**
    We first generate a hypothetical answer to the user's question. This "hallucinated" but semantically relevant text is then embedded. This shifts the query vector from "question space" to "answer space", making it much closer to the actual document we want to retrieve.

2.  **Cross-Encoder Re-ranking:**
    We retrieve a broader set of candidates (Top-K) using the vector search. Then, a Cross-Encoder model (which takes pairs of Query + Document) scores them. Cross-Encoders are far more accurate at capturing fine-grained semantic nuances than bi-encoders (vector dot products) and effectively filter out the "Präsens" distractor in favor of the "Perfekt" document.

### Architecture Diagram

```mermaid
graph TD
    %% Styling
    classDef failure fill:#ffe6e6,stroke:#ff9999,stroke-width:2px;
    classDef success fill:#e6ffe6,stroke:#99ff99,stroke-width:2px;
    classDef process fill:#e6f3ff,stroke:#99ccff,stroke-width:2px;

    subgraph Standard_RAG ["🔴 Standard Retrieval Failure"]
        direction TB
        User1([User Query: "Erkläre mir das Perfekt"])
        VectorSearch1[Vector Search <br/>(Cosine Similarity)]
        
        User1 --> VectorSearch1
        VectorSearch1 -->|High Similarity| BadResult[❌ Retrieved: "Präsens"]
        
        class BadResult failure
    end

    subgraph Advanced_RAG ["🟢 Enhanced Pipeline Solution"]
        direction TB
        User2([User Query: "Erkläre mir das Perfekt"])
        
        subgraph Stage1 [Stage 1: Query Expansion]
            HyDE[HyDE Generator<br/>Create Hypothetical Answer]
            User2 --> HyDE
            HyDE -->|Embeds closer to target| VectorSearch2[Vector Search]
        end

        subgraph Stage2 [Stage 2: Re-ranking]
            TopK[Retrieve Top-K Candidates<br/>(Präsens, Perfekt, Präteritum...)]
            CrossEncoder[Cross-Encoder Re-ranker<br/>Scores query vs. doc pairs]
            
            VectorSearch2 --> TopK
            TopK --> CrossEncoder
        end

        CrossEncoder -->|Highest Relevance Score| GoodResult[✅ Selected: "Perfekt"]
        
        class HyDE,CrossEncoder,VectorSearch2 process
        class GoodResult success
    end
```

## Answer
When retrieval fails due to semantic ambiguity — like 'Perfekt' retrieving 'Präsens' — I'd implement a two-stage fix: Query expansion via HyDE: Generate a hypothetical answer to enrich the query's semantics before embedding, steering retrieval toward the correct concept region. Cross-encoder re-ranking: After initial vector search, pass top-k candidates through a cross-encoder to distinguish fine-grained relevance (e.g., 'Perfekt' vs 'Präsens' are both tenses but different). This balances latency and accuracy — critical for production RAG.
