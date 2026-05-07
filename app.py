import streamlit as st
import anthropic
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Restaurant Review Analyzer", page_icon="🍽️")
st.title("🍽️ Restaurant Review Analyzer")
st.write("Analyze your restaurant reviews with AI")

client = anthropic.Anthropic(api_key="YOUR_API_KEY_HERE")

st.sidebar.header("Add Reviews")
review_input = st.sidebar.text_area("Paste your reviews here (one per line)", height=200)
analyze_button = st.sidebar.button("Analyze Reviews")

if "results" not in st.session_state:
    st.session_state.results = []

if analyze_button and review_input:
    reviews = [r.strip() for r in review_input.strip().split("\n") if r.strip()]
    
    with st.spinner("Analyzing reviews with AI..."):
        for review in reviews:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this restaurant review and respond ONLY with JSON in this exact format:
{{"sentiment": "positive" or "negative" or "neutral", "score": number from 1 to 10, "category": "food" or "service" or "ambiance" or "value", "summary": "one short sentence"}}

Review: {review}"""
                }]
            )
            
            import json
            text = response.content[0].text
            clean = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
            result["review"] = review
            st.session_state.results.append(result)

if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_score = df["score"].mean()
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col2:
        positive = len(df[df["sentiment"] == "positive"])
        st.metric("Positive Reviews", f"{positive}/{len(df)}")
    with col3:
        top_category = df["category"].mode()[0]
        st.metric("Top Category", top_category.capitalize())
    
    st.subheader("Sentiment Distribution")
    fig1 = px.pie(df, names="sentiment", color="sentiment",
                  color_discrete_map={"positive":"#2ecc71","negative":"#e74c3c","neutral":"#f39c12"})
    st.plotly_chart(fig1)
    
    st.subheader("Score by Category")
    fig2 = px.bar(df.groupby("category")["score"].mean().reset_index(), 
                  x="category", y="score", color="category")
    st.plotly_chart(fig2)
    
    st.subheader("Review Details")
    st.dataframe(df[["review", "sentiment", "score", "category", "summary"]])
    
    if st.button("Clear Results"):
        st.session_state.results = []
        st.rerun()