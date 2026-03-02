"""
app.py
------
Streamlit web interface for the Techculture.ai Service Information Assistant.

Run with:
  streamlit run app.py

This gives you a browser-based chat UI that wraps the agent directly
(no need for the FastAPI server to be running separately).
"""

import logging
import streamlit as st

# Set up logging before importing other modules
logging.basicConfig(level=logging.WARNING)

from embeddings import build_vector_store
from agent import run_agent, format_agent_response_for_display

# ─────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Techculture.ai — Service Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────────────────
# Initialize Vector Store (once, cached)
# ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initializing knowledge base...")
def load_vector_store():
    """Load (or build) the ChromaDB vector store. Cached across sessions."""
    return build_vector_store(force_rebuild=False)


# ─────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=Techculture.ai", use_container_width=True)
    st.markdown("---")
    st.markdown("### 🤖 About This Assistant")
    st.markdown(
        "This AI assistant can answer questions about Techculture.ai's services, "
        "pricing, experience, and case studies. Answers are grounded in real company documents."
    )
    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    example_queries = [
        "What AI services do you offer?",
        "Do you have fintech experience?",
        "How much does a 3-month marketing campaign cost?",
        "What's your experience with RAG systems?",
        "Tell me about your data engineering services",
        "What does your web development team build?",
        "Do you offer MLOps services?",
    ]
    for q in example_queries:
        if st.button(q, use_container_width=True, key=q):
            st.session_state["pending_query"] = q

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    show_debug = st.checkbox("Show retrieved chunks (debug)", value=False)

    if st.button("🔄 Rebuild Knowledge Base", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Built with Gemini 1.5 Flash · ChromaDB · FastAPI · Streamlit")


# ─────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────
st.title("🤖 Techculture.ai — Service Assistant")
st.markdown(
    "Ask me anything about our AI consulting, digital marketing, web development, "
    "data engineering services, pricing, or past projects."
)
st.markdown("---")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Load vector store
try:
    collection = load_vector_store()
    st.success(f"✅ Knowledge base loaded ({collection.count()} chunks indexed)")
except Exception as e:
    st.error(f"❌ Failed to load knowledge base: {e}")
    st.stop()

st.markdown("")

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle sidebar button clicks (pre-fill query)
pending = st.session_state.pop("pending_query", None)

# Chat input
user_input = st.chat_input("Ask a question about Techculture.ai's services...")

# Use pending query from sidebar button if no direct input
query = user_input or pending

if query:
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state["messages"].append({"role": "user", "content": query})

    # Run agent and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_agent(query, collection=collection)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        # ── Answer ──────────────────────────────────────
        st.markdown(result["answer"])

        # ── Sources ─────────────────────────────────────
        if result["sources"]:
            with st.expander("📄 Sources", expanded=True):
                for s in result["sources"]:
                    st.markdown(f"• **{s['file']}** — Section: *{s['section']}*")

        # ── Tool Outputs ─────────────────────────────────
        if result.get("tool_outputs"):
            with st.expander("🛠️ Agent Tools Used", expanded=True):
                # Sentiment badge
                sentiment = result["sentiment"]
                sentiment_color = {
                    "Positive": "🟢",
                    "Negative": "🔴",
                    "Neutral": "🟡"
                }.get(sentiment["label"], "⚪")
                st.markdown(
                    f"{sentiment_color} **Sentiment**: {sentiment['label']} "
                    f"(confidence: {sentiment['confidence']})"
                )

                # Pricing estimate
                pricing = result.get("pricing_estimate", {})
                if pricing.get("triggered"):
                    st.markdown("---")
                    st.markdown(f"📊 **Pricing Estimate** ({pricing.get('service_type', 'General')})")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "INR Range",
                            f"₹{pricing['min_inr']:,} – ₹{pricing['max_inr']:,}"
                        )
                    with col2:
                        st.metric(
                            "USD Range",
                            f"${pricing['min_usd']:,} – ${pricing['max_usd']:,}"
                        )
                    st.caption(f"Duration: {pricing.get('duration_months', 1)} month(s)")
                    if pricing.get("notes"):
                        st.info(pricing["notes"])

        # ── Debug: Raw chunks ────────────────────────────
        if show_debug:
            with st.expander("🔍 Debug: Retrieved Chunks"):
                for i, chunk in enumerate(result.get("retrieved_chunks", []), 1):
                    st.markdown(f"**Chunk {i}** — `{chunk['source']}` / {chunk['section']} (distance: {chunk['distance']})")
                    st.text(chunk["text"][:400])
                    st.markdown("---")

        # Store full formatted answer in history
        display_text = result["answer"]
        st.session_state["messages"].append({"role": "assistant", "content": display_text})

# Footer
st.markdown("---")
st.caption("Powered by Google Gemini · Answers are grounded in Techculture.ai documents · Not financial or legal advice")
