import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="AgriSetu AI",
    page_icon="🌾",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

@st.cache_data
def load_data():
    recommendations = pd.read_csv(BASE_DIR / "final_recommendations.csv")
    market = pd.read_csv(BASE_DIR / "market_intelligence.csv")
    return recommendations, market

recs, market = load_data()

st.title("🌾 AgriSetu AI")
st.caption("AI-powered crop recommendation and market intelligence dashboard")

# Sidebar
st.sidebar.header("⚙️ Recommendation Controls")
top_n = st.sidebar.slider(
    "Number of recommendations",
    min_value=1,
    max_value=len(recs),
    value=min(5, len(recs))
)

min_score = st.sidebar.slider(
    "Minimum AgriSetu Score",
    min_value=0,
    max_value=100,
    value=0
)

filtered = (
    recs[recs["Final_AgriSetu_Score"] >= min_score]
    .sort_values("Final_AgriSetu_Score", ascending=False)
    .head(top_n)
)

# Top recommendation
top_crop = filtered.iloc[0] if not filtered.empty else None

if top_crop is not None:
    st.success(
        f"🏆 **Top Recommendation: {top_crop['Commodity']}** "
        f"— AgriSetu Score: **{top_crop['Final_AgriSetu_Score']:.2f}/100**"
    )
else:
    st.warning("No crops match the selected minimum score.")

# KPI cards
if top_crop is not None:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Top Crop",
        top_crop["Commodity"]
    )
    c2.metric(
        "AgriSetu Score",
        f"{top_crop['Final_AgriSetu_Score']:.2f}"
    )
    c3.metric(
        "Estimated Market Price",
        f"₹ {top_crop['Market_Price_Estimate']:,.2f}"
    )
    c4.metric(
        "Farm Suitability",
        f"{top_crop['Farm_Suitability_Score']:.0f}/100"
    )

st.divider()

# Recommendations
st.header("🥇 Crop Recommendations")

display_cols = [
    "Commodity",
    "Final_AgriSetu_Score",
    "Farm_Suitability_Score",
    "Enhanced_Market_Score",
    "Market_Price_Estimate",
    "Prediction_Source"
]

st.dataframe(
    filtered[display_cols].style.format({
        "Final_AgriSetu_Score": "{:.2f}",
        "Farm_Suitability_Score": "{:.0f}",
        "Enhanced_Market_Score": "{:.2f}",
        "Market_Price_Estimate": "₹ {:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.bar_chart(
    filtered.set_index("Commodity")["Final_AgriSetu_Score"],
    use_container_width=True
)

st.divider()

# Detailed crop analysis
st.header("🔍 Detailed Crop Analysis")

selected_crop = st.selectbox(
    "Select a crop",
    recs.sort_values("Final_AgriSetu_Score", ascending=False)["Commodity"]
)

crop = recs[recs["Commodity"] == selected_crop].iloc[0]

left, right = st.columns(2)

with left:
    st.subheader(f"🌱 {selected_crop}")
    st.metric("Final AgriSetu Score", f"{crop['Final_AgriSetu_Score']:.2f}/100")
    st.metric("Farm Suitability Score", f"{crop['Farm_Suitability_Score']:.0f}/100")
    st.metric("Enhanced Market Score", f"{crop['Enhanced_Market_Score']:.2f}/100")

with right:
    st.subheader("💰 Price Intelligence")
    st.metric("Historical Average Price", f"₹ {crop['Historical_Price']:,.2f}")
    st.metric("Predicted Market Price", f"₹ {crop['Market_Price_Estimate']:,.2f}")
    st.metric("Median Price", f"₹ {crop['Median_Price']:,.2f}")

st.subheader("📊 Score Breakdown")

score_data = pd.DataFrame({
    "Score": [
        crop["Farm_Suitability_Score"],
        crop["Enhanced_Market_Score"],
        crop["Final_AgriSetu_Score"]
    ]
}, index=[
    "Farm Suitability",
    "Market Intelligence",
    "Final AgriSetu Score"
])

st.bar_chart(score_data, use_container_width=True)

st.divider()

# Market intelligence
st.header("📈 Market Intelligence")

market_display = market[[
    "Commodity",
    "Historical_Price",
    "ML_Predicted_Price",
    "Price_Volatility",
    "Market_Count",
    "Enhanced_Market_Score"
]].copy()

st.dataframe(
    market_display.style.format({
        "Historical_Price": "₹ {:,.2f}",
        "ML_Predicted_Price": "₹ {:,.2f}",
        "Price_Volatility": "{:,.2f}",
        "Enhanced_Market_Score": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

price_chart = market.set_index("Commodity")[[
    "Historical_Price",
    "ML_Predicted_Price"
]]

st.subheader("Historical vs ML Predicted Price")
st.bar_chart(price_chart, use_container_width=True)

st.divider()

# Downloads
st.header("⬇️ Download Results")

d1, d2 = st.columns(2)

with d1:
    st.download_button(
        "Download Final Recommendations CSV",
        data=recs.to_csv(index=False).encode("utf-8"),
        file_name="final_recommendations.csv",
        mime="text/csv"
    )

with d2:
    st.download_button(
        "Download Market Intelligence CSV",
        data=market.to_csv(index=False).encode("utf-8"),
        file_name="market_intelligence.csv",
        mime="text/csv"
    )

st.divider()
st.caption(
    "AgriSetu AI combines ML-based market price signals, market intelligence, "
    "and farm suitability scoring to recommend crops."
)
