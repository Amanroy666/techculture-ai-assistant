# Case Study: Personalized Recommendation Engine for a D2C E-Commerce Brand

## Client Background

**Industry**: E-Commerce (Direct-to-Consumer, Fashion & Lifestyle)
**Company Size**: 80 employees, bootstrapped
**Location**: Delhi, India
**Engagement Duration**: 4 months
**Engagement Type**: Custom AI Development + Digital Marketing Optimization

*Client name withheld under NDA.*

---

## The Problem

The client ran a D2C fashion brand with a Shopify-based storefront, around 12,000 SKUs, and roughly 85,000 monthly active users. They were doing well — but they noticed a clear pattern: most customers bought once and never came back.

Their analytics showed:
- **Repeat purchase rate**: Only 18% (industry average for fashion D2C is 30–35%)
- **Average order value**: ₹2,100 — lower than expected for their product range
- **Homepage bounce rate**: 64%
- **Category page CTR to product pages**: Only 22%

The team suspected that customers weren't finding products relevant to them. The site showed the same products to everyone — bestsellers, new arrivals — with no personalization whatsoever.

Their email marketing was also generic: a weekly newsletter blasted to their entire list with the same content regardless of what each customer had previously bought or browsed.

---

## Our Approach

### Phase 1: Data Assessment & Strategy (Weeks 1–2)

We audited their data sources:
- **Shopify order history**: 3 years, ~240,000 orders — clean and well-structured
- **Website clickstream data**: 14 months via Google Analytics 4 — usable but needed proper extraction
- **Customer profiles**: Basic (name, email, location, acquisition channel)
- **Product catalog metadata**: Partially structured — tags were inconsistent (some products had good metadata, many didn't)

Two problems identified:
1. Poor product metadata quality would hurt recommendation relevance — we'd need to fix this first
2. Cold start problem: ~40% of sessions were from first-time visitors with no history — recommendations needed a non-personalized fallback strategy

### Phase 2: Product Metadata Enrichment (Weeks 2–4)

Before building recommendations, we enriched the product catalog:
- Used a multimodal approach: product images + existing description text
- Fine-tuned a CLIP-based model to extract fashion-specific attributes: color, pattern, style category, occasion type, formality level
- Automatically tagged all 12,000 SKUs with standardized attributes
- This also cleaned up search — customers could now find "floral summer dress" even if the product description didn't use those exact words

### Phase 3: Recommendation Engine Development (Weeks 4–12)

We built a multi-algorithm recommendation system:

**Algorithm 1 – Collaborative Filtering (User-Based)**
- Identifies customers with similar purchase patterns and recommends what similar customers bought
- Works well for returning customers with 3+ purchase history
- Used matrix factorization (ALS algorithm) on the order history data

**Algorithm 2 – Content-Based Filtering**
- Recommends products similar to what a customer has viewed or purchased (based on product attributes)
- Works for both new and returning customers
- Uses cosine similarity on the enriched product embeddings

**Algorithm 3 – Session-Based Recommendations (for Anonymous Users)**
- Uses clickstream data from the current session to recommend products
- Implemented using a lightweight sequential model (GRU-based)
- Important for the 40% of first-time visitors

**Ensemble Logic**
- A simple weighted ensemble combines signals from all three algorithms
- Weights are adjusted based on how much data is available for each user
- New user → session-based weights higher; loyal customer → collaborative filtering weights higher

**Placement on Site**:
- Homepage: "Recommended for you" section (personalized per user)
- Product pages: "You might also like" (content-based)
- Cart page: "Complete the look" / "Frequently bought together"
- Category pages: Rerank product listing by predicted relevance

### Phase 4: Personalized Email Marketing (Weeks 10–14)

We connected the recommendation engine to their Klaviyo email setup:
- Automated "browse abandonment" emails with personalized product suggestions
- Weekly emails dynamically populated with recommended products per recipient
- Replenishment reminders for consumable products
- Lapsed customer win-back sequences with personalized offers

### Phase 5: A/B Testing & Optimization (Ongoing)

- Ran 30-day A/B test: 50% of users got personalized experience, 50% got original
- Monitored: conversion rate, AOV, CTR, repeat purchase rate

---

## Results (Measured 90 Days After Full Launch)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Repeat Purchase Rate | 18% | 28% | ↑ 56% |
| Average Order Value | ₹2,100 | ₹2,650 | ↑ 26% |
| Homepage Bounce Rate | 64% | 49% | ↓ 23% |
| Category Page CTR | 22% | 34% | ↑ 55% |
| Email Click-Through Rate | 3.2% | 8.7% | ↑ 172% |
| Revenue (same traffic) | Baseline | +38% | — |

The revenue increase of 38% on effectively the same traffic volume made this one of their highest-ROI projects ever — no additional ad spend required.

---

## Technologies Used

- **ML/AI**: Python, PyTorch, Scikit-learn, CLIP (for image embeddings), Surprise library (ALS)
- **Data Processing**: PySpark, Pandas, dbt (for data modeling)
- **Vector Search**: FAISS (for fast product similarity search)
- **API**: FastAPI (recommendation serving API)
- **Deployment**: Docker, GCP Cloud Run
- **Email Integration**: Klaviyo API
- **Analytics**: BigQuery + Looker Studio for recommendation performance tracking

---

## Key Learnings

1. **Data quality is the prerequisite.** We couldn't build good recommendations without first enriching the product metadata. This phase was unglamorous but critical.
2. **Personalization compounds.** The more customers interact, the better the recommendations get — and better recommendations drive more interactions.
3. **Cold start is a real problem.** Having a good non-personalized fallback strategy for new users matters more than most teams expect.
4. **Email + on-site personalization together outperform either alone.** Consistent personalization across touchpoints reinforces product discovery and trust.
