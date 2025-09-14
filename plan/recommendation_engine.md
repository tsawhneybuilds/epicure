# Epicure Recommendation Engine Plan

## Strategy Overview

Embedding + Tag Inference + Weighted Scoring + Hard Constraints architecture for personalized restaurant recommendations.

## Required Access

### Supabase Setup
- pgvector extension for vector similarity  
- PostgreSQL with PostGIS for geo queries
- Vector dimension: 384 (sentence-transformers)

### API Access  
1. **Groq API**: Chinese open source models + fast inference
   - `deepseek-v3` (primary - superior reasoning for tagging & extraction)
   - `llama3-70b-8192` (fallback for complex tasks)
   - `mixtral-8x7b-32768` (fallback for speed)
2. **Hugging Face**: sentence-transformers/all-MiniLM-L6-v2 (embeddings only)
3. **Google Places** (optional): real-time hours, metadata

**Note**: DeepSeek-V3 replaces BART for all text analysis tasks due to:
- Superior reasoning for nuanced preference extraction
- Better understanding of food context and implicit preferences
- Ability to extract multiple overlapping dietary/preference categories
- More accurate confidence scoring for extracted preferences

## Architecture Components

### 1. Item Encoder Service
Generates embeddings for dishes and restaurants using sentence transformers.

### 2. Tag Inference Service
Extracts preferences using Groq LLMs + Hugging Face zero-shot classification:
- **Groq Llama3-8B**: Fast preference extraction from natural language
- **BART-large-mnli**: Zero-shot dietary/cuisine classification
- **Combined approach**: LLM for complex reasoning, classifier for speed

### 3. Scoring Engine  
Weighted ranking:
- Embedding similarity (40%)
- Tag matching (30%)
- Rating normalization (10%) 
- Price fit (10%)
- Distance fit (10%)

### 4. Filtering Engine
Hard constraints:
- Opening hours
- Price limits
- Distance caps
- Dietary restrictions
- Allergen safety

### 5. Search Pipeline
Complete flow from query to ranked results.

### 6. Learning Loop
- Real-time preference updates
- XGBoost ranker training
- A/B testing framework

## Data Integration

Processes existing soho_menu_harvest data:
1. Import venues_enriched.jsonl → restaurants
2. Import menu_items.csv → menu items
3. Generate embeddings for all content
4. Infer tags and dietary info
5. Store in vector database

## Timeline

**Week 1-2**: Infrastructure setup, Supabase + pgvector
**Week 3-4**: Core recommendation logic, scoring engine  
**Week 5-6**: Data integration, optimization
**Week 7-8**: Learning systems, production deployment

## Performance Targets

- Search latency: <200ms
- Groq LLM inference: <500ms (much faster than OpenAI)
- Embedding generation: <5ms per item
- Tag classification: <10ms per text
- User satisfaction: >85% on liked items
- Personalization lift: >20% vs baseline

## Success Metrics

- Click-through rate on top 3 results
- Like vs dislike ratio
- Result diversity
- Restaurant coverage
- End-to-end latency

This engine provides personalized, context-aware recommendations that improve through continuous learning.
