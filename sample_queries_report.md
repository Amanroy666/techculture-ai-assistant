# Sample Queries & Results Report
## Techculture.ai Service Information Assistant

This document demonstrates the assistant's capabilities across 10 test queries covering different scenarios — service information, pricing, agentic tool use, and edge cases.

---

## Query 1: General AI Services

**Question:** "What AI consulting services do you offer?"

**Answer:**
Techculture.ai offers a comprehensive suite of AI consulting services designed to help organizations adopt and scale artificial intelligence responsibly. These include:

- **AI Readiness Assessment** (2–3 weeks): Evaluates your organization's data infrastructure, talent, and processes, and delivers a prioritized AI roadmap with ROI estimates. Cost ranges from ₹3.5L to ₹6L.
- **AI Strategy & Roadmap Development** (4–6 weeks): A multi-year strategic plan covering use case prioritization, build-vs-buy analysis, and talent planning.
- **Proof of Concept (POC) Development** (3–5 weeks): Fast, focused POCs to validate AI ideas before full investment — typically ₹4L to ₹10L.
- **GenAI Integration Consulting**: Helps companies adopt LLMs, RAG systems, and prompt engineering strategies within existing workflows.
- **AI Vendor Evaluation**: Independent advisory for selecting AI platforms and SaaS tools.

Sources: ai_consulting_services.md (What We Offer), services_overview.md (Core Service Areas)

**Tools Used:** SentimentAnalyzer (Neutral)
**Pricing Tool:** Not triggered (no pricing intent detected)

**Analysis:** Answer accurately reflects document content. Covers all major consulting sub-services with pricing where available. Source citations are specific and accurate.

---

## Query 2: Fintech Experience

**Question:** "Do you have experience with fintech projects?"

**Answer:**
Yes, Techculture.ai has substantial fintech experience. A notable project involved building an AI-powered fraud detection system for a digital lending NBFC (Series B funded, Mumbai). The engagement ran for 5 months and covered custom ML development and MLOps setup.

Key outcomes from that project:
- False positive rate reduced from 23% to 7.2% (69% reduction)
- Fraud slippage rate reduced from 3.1% to 0.8% (74% reduction)
- Manual review volume dropped from ~400/day to ~95/day
- Estimated ₹3.2 Cr in annual fraud losses prevented

The solution involved a layered detection system using XGBoost for individual application scoring, graph-based ring detection for organized fraud, and SHAP for explainability. An automated MLOps pipeline using Airflow and GCP Cloud Run was set up for continuous retraining.

Beyond fraud detection, Techculture.ai lists fintech as a core industry, with experience in credit scoring, automated KYC, and chatbot development.

Sources: case_study_fintech.md (The Problem, Results), services_overview.md (Industries We Serve)

**Tools Used:** SentimentAnalyzer (Neutral)
**Pricing Tool:** Not triggered

**Analysis:** The answer pulls from the fintech case study with specific metrics, which is exactly what a potential client would want to see. Well-sourced and credible.

---

## Query 3: Pricing for Digital Marketing Campaign

**Question:** "What's the estimated cost for a 3-month digital marketing campaign?"

**Answer:**
For a 3-month digital marketing campaign, Techculture.ai offers the following pricing tiers:

- **Basic** (SEO + 2 social platforms): ₹2,00,000 – ₹2,50,000 total
- **Growth** (SEO + PPC + Social + Email): ₹2,40,000 – ₹3,50,000 total
- **Performance** (full-stack with ad spend management): ₹4,00,000 – ₹6,00,000+ (excluding ad spend)

The Growth package is the most popular for businesses looking to establish a strong digital presence across multiple channels within a 3-month window. All packages include weekly reporting, a dedicated account manager, and monthly strategy review calls.

Sources: pricing_guide.md (Campaign Packages), faq.md (Pricing Questions)

**🛠️ Pricing Estimator Tool Output:**
- Service: Digital Marketing
- Duration: 3 months
- INR Range: ₹2,25,000 – ₹6,00,000
- USD Range: $2,711 – $7,229
- Note: Full-stack digital marketing. Excludes ad spend.

**🎭 Sentiment:** Neutral (High confidence)

**Analysis:** Pricing tool correctly triggered by "cost" and "3-month" keywords. Duration extraction worked correctly. Answer is grounded in document content with specific ranges. Good example of agentic tool use.

---

## Query 4: RAG and LLM Systems

**Question:** "Do you build RAG systems and LLM-powered applications?"

**Answer:**
Yes, building RAG (Retrieval-Augmented Generation) systems and LLM-powered applications is one of Techculture.ai's strongest practice areas. Their capabilities include:

- Production RAG systems for legal firms, healthcare companies, and enterprise knowledge bases
- LLM integration using models from OpenAI, Google (Gemini), Anthropic (Claude), and open-source options via Ollama and Hugging Face
- Frameworks: LangChain, LlamaIndex, and custom orchestration
- Vector databases: Chroma, Pinecone, FAISS
- Document intelligence applications (upload PDFs, extract structured data, Q&A over large document collections)
- AI-powered semantic search to replace keyword search

Pricing for LLM/RAG projects typically ranges from ₹6L – ₹20L ($7,200 – $24,000) depending on scope.

Sources: web_app_development.md (AI-Integrated Application Development), faq.md (AI & ML Questions)

**Tools Used:** SentimentAnalyzer (Neutral), PricingEstimator (triggered by detected LLM context)

**Analysis:** Demonstrates that the assistant can pull AI-specific technical details from multiple documents and synthesize them coherently.

---

## Query 5: MLOps Services

**Question:** "What MLOps services do you provide and how much does a 6-month engagement cost?"

**Answer:**
Techculture.ai provides end-to-end MLOps services including:

- Model versioning and experiment tracking (MLflow)
- CI/CD pipelines for machine learning
- Model serving infrastructure (Docker, Kubernetes, FastAPI)
- Pipeline orchestration (Airflow)
- Model monitoring and drift detection (Evidently AI, Prometheus)
- Automated retraining pipelines

A real example: For a fintech client, they deployed a real-time fraud scoring API with p99 latency under 180ms at 200 concurrent requests, with a 30-day Airflow-based retraining pipeline.

For a **6-month MLOps engagement**:
- INR Range: ₹12,00,000 – ₹24,00,000
- USD Range: $14,458 – $28,916
- Typical scope includes: pipeline setup, monitoring infrastructure, retraining automation, and team handoff.

Sources: services_overview.md (MLOps & AI Infrastructure), case_study_fintech.md (MLOps Pipeline & Deployment)

**🛠️ Pricing Estimator:** Triggered — MLOps, 6 months, ₹12L – ₹24L

**Analysis:** Both pricing tool (triggered by "how much" + "6-month") and RAG retrieval worked together to give a complete answer. Good example of tool + context synthesis.

---

## Query 6: Data Engineering Services

**Question:** "Tell me about your data engineering capabilities"

**Answer:**
Techculture.ai's Data Engineering practice covers the full spectrum of data infrastructure:

**Pipelines & ETL**: They build ETL/ELT pipelines using Apache Airflow or Prefect for orchestration, dbt or PySpark for transformation, connecting sources like PostgreSQL, MongoDB, Salesforce, and Shopify to destinations like BigQuery, Snowflake, and Delta Lake.

**Real-Time Streaming**: Kafka-based streaming pipelines, Debezium for CDC (Change Data Capture), and Apache Flink for stateful stream processing. They've handled 5M+ database events/day with sub-5-minute latency.

**Cloud Data Warehouses**: Setup and optimization on BigQuery, Snowflake, or Redshift, including schema design, partitioning, access control, and BI tool connections.

**Data Quality**: Great Expectations for automated validation, data lineage tracking, and anomaly detection on pipeline metrics.

Engagement options include project-based work (₹6L – ₹20L for pipeline development) or monthly retainers (₹1.5L – ₹4L/month).

Sources: data_engineering_services.md (Services, Our Data Engineering Stack)

**Tools Used:** SentimentAnalyzer (Neutral)
**Pricing Tool:** Not triggered

**Analysis:** Comprehensive retrieval from the data engineering document. The answer is well-organized and covers all major service areas mentioned in the source material.

---

## Query 7: E-Commerce AI Project

**Question:** "Can you share a case study about e-commerce or recommendation systems?"

**Answer:**
Techculture.ai completed a recommendation engine project for a D2C fashion brand (80 employees, bootstrapped, Delhi-based) running a Shopify storefront with 12,000 SKUs and 85,000 monthly active users.

**The problem**: Repeat purchase rate was only 18% (vs industry average of 30–35%), and the site showed identical product listings to all users with no personalization.

**The solution**: A multi-algorithm recommendation engine combining:
- Collaborative filtering (for returning customers)
- Content-based filtering using enriched product embeddings (CLIP-based)
- Session-based recommendations (GRU model) for first-time visitors

They also enriched the product catalog metadata using a multimodal model (CLIP + product descriptions) to standardize 12,000 SKU tags.

**Results after 90 days:**
- Repeat purchase rate: 18% → 28% (+56%)
- Average order value: ₹2,100 → ₹2,650 (+26%)
- Email click-through rate: 3.2% → 8.7% (+172%)
- Revenue on same traffic: +38%

Sources: case_study_ecommerce.md (The Problem, Our Approach, Results)

**Analysis:** Excellent retrieval — specific metrics from the case study document are accurately reproduced. This is exactly the kind of answer a potential e-commerce client needs to evaluate the company.

---

## Query 8: Pricing Inquiry with Negative Sentiment

**Question:** "I've been looking everywhere and can't find clear pricing — it's really frustrating. How much does a basic website cost?"

**Answer:**
I understand that unclear pricing can be frustrating — let me give you a direct answer.

For web development at Techculture.ai:
- **MVP Web App** (6–10 weeks): ₹5,00,000 – ₹15,00,000 ($6,000 – $18,000)
- **Full Web Application** (3–6 months): ₹15,00,000 – ₹60,00,000

For a **basic website** specifically, the MVP package (₹5L–₹15L) is the most relevant. The final cost depends on features, number of pages, integrations needed, and design complexity.

A free 1-hour discovery call is available at hello@techculture.ai to get a more accurate estimate for your specific needs.

Sources: pricing_guide.md (Web & App Development), web_app_development.md (MVP Development)

**🎭 Sentiment:** Negative (Medium confidence) — signals: "frustrating", "can't find"
**🛠️ Pricing Estimator:** Triggered — Web Development, 1 month (default)

**Analysis:** Sentiment analysis correctly flagged the negative/frustrated tone. The pricing tool was triggered by implied pricing intent. The answer is direct and addresses the frustration. Shows good agentic awareness of user emotional context.

---

## Query 9: Edge Case — Out-of-Scope Question

**Question:** "What is your company's annual revenue?"

**Answer:**
I don't have specific information about Techculture.ai's annual revenue in the documents available to me. Revenue figures are typically not published in service documentation.

What I can tell you is that Techculture.ai has been operating since 2019 and has completed over 80 projects across 15+ industries, working with clients in India, Southeast Asia, the Middle East, and Europe.

For detailed business information, I'd recommend reaching out directly at hello@techculture.ai.

Sources: services_overview.md (About Us), faq.md (General Questions)

**Analysis:** The assistant correctly identifies that the question is out of scope, doesn't hallucinate financial data, and still provides what context it can from available documents. This is the expected behavior for edge cases.

---

## Query 10: Multi-Service Comparison Question

**Question:** "I'm a startup. Should I go for your MVP web development package or invest in AI consulting first? What's the cost difference?"

**Answer:**
Great question — and the right one to ask early. Here's a practical breakdown:

**MVP Web App Package**: ₹5,00,000 – ₹15,00,000 (6–10 weeks)
Best if: You have a clear product idea and need to build and ship fast to validate it with users.

**AI Consulting (Readiness Assessment + Roadmap)**: ₹3,50,000 – ₹6,00,000 (2–3 weeks)
Best if: You're unsure where AI fits in your product or want to avoid investing in ML before you know if your data is ready for it.

**For most early-stage startups**, Techculture.ai's FAQ suggests starting with a free discovery call to define scope before committing. If your primary need is getting a product to market quickly, the MVP package makes sense first. If you're building something AI-native from the start, a light AI consulting engagement (2–3 weeks) can save significant rework later.

The cost difference is relatively small (₹1.5L – ₹9L depending on tiers), but the strategic difference is significant.

Sources: pricing_guide.md (AI & ML Services, Web & App Development), faq.md (Project & Pricing Questions)

**🛠️ Pricing Estimator:** Triggered for both web_development and ai_consulting
**🎭 Sentiment:** Positive (signals: startup enthusiasm detected)

**Analysis:** The assistant synthesized information from multiple documents to give genuinely useful strategic advice. This is the highest-quality response type — going beyond simple retrieval to practical guidance, while remaining grounded in document content.

---

## Summary

| Query | Tools Triggered | Sources Used | Quality |
|-------|----------------|--------------|---------|
| 1. AI Services | Sentiment | 2 docs | ✅ Excellent |
| 2. Fintech Experience | Sentiment | 2 docs | ✅ Excellent |
| 3. Marketing Campaign Cost | Sentiment + Pricing | 2 docs | ✅ Excellent |
| 4. RAG/LLM Systems | Sentiment + Pricing | 2 docs | ✅ Good |
| 5. MLOps 6-month | Sentiment + Pricing | 2 docs | ✅ Excellent |
| 6. Data Engineering | Sentiment | 1 doc | ✅ Excellent |
| 7. E-Commerce Case Study | Sentiment | 1 doc | ✅ Excellent |
| 8. Frustrated Pricing Query | Sentiment (Negative) + Pricing | 2 docs | ✅ Good |
| 9. Out-of-Scope (Revenue) | Sentiment | 1 doc | ✅ Handled correctly |
| 10. Multi-service Comparison | Sentiment + Pricing | 2 docs | ✅ Excellent |

**Overall**: The system consistently retrieved relevant context, cited sources accurately, triggered tools appropriately, and avoided hallucination when information was unavailable.
