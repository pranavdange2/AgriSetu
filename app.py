
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AgriSetu AI", page_icon="🌾", layout="wide")

BASE = Path(__file__).parent

@st.cache_data
def load_data():
    recs = pd.read_csv(BASE / "final_recommendations.csv")
    market = pd.read_csv(BASE / "market_intelligence.csv")
    return recs, market

recs, market = load_data()

# Transparent suitability rules used to personalize the existing Kaggle results.
# The market intelligence values remain the ML/data-driven values from the project.
CROP_PROFILES = {
    "Green Chilli": {"soil": ["Loamy", "Sandy Loam"], "water": ["Medium", "High"], "climate": ["Warm", "Hot"]},
    "Brinjal": {"soil": ["Loamy", "Clay Loam"], "water": ["Medium", "High"], "climate": ["Warm", "Hot"]},
    "Onion": {"soil": ["Loamy", "Sandy Loam"], "water": ["Low", "Medium"], "climate": ["Cool", "Warm"]},
    "Tomato": {"soil": ["Loamy", "Sandy Loam"], "water": ["Medium", "High"], "climate": ["Warm", "Hot"]},
    "Potato": {"soil": ["Loamy", "Sandy Loam"], "water": ["Medium", "High"], "climate": ["Cool", "Warm"]},
}

def suitability(commodity, soil, water, climate):
    p = CROP_PROFILES.get(commodity, {})
    score = 0
    score += 40 if soil in p.get("soil", []) else 15
    score += 30 if water in p.get("water", []) else 10
    score += 30 if climate in p.get("climate", []) else 10
    return score

st.title("🌾 AgriSetu AI")
st.caption("Personalized crop recommendation using farm suitability + market intelligence")

with st.sidebar:
    st.header("🚜 Your Farm Profile")
    location = st.text_input("Village / District", placeholder="e.g. Madurai, Tamil Nadu")
    soil = st.selectbox("Soil type", ["Loamy", "Sandy Loam", "Clay Loam", "Clay", "Sandy"])
    water = st.selectbox("Water availability", ["Low", "Medium", "High"])
    climate = st.selectbox("Climate / temperature", ["Cool", "Warm", "Hot"])
    land = st.number_input("Land size (acres)", min_value=0.1, value=1.0, step=0.1)

# Build personalized ranking
data = recs.copy()
data["Your_Farm_Suitability"] = data["Commodity"].apply(
    lambda x: suitability(x, soil, water, climate)
)
# 60% personalized farm suitability + 40% existing data-driven market score
data["Personalized_AgriSetu_Score"] = (
    0.60 * data["Your_Farm_Suitability"] +
    0.40 * data["Enhanced_Market_Score"]
)
data = data.sort_values("Personalized_AgriSetu_Score", ascending=False).reset_index(drop=True)

winner = data.iloc[0]

st.success(
    f"🏆 Best recommendation for your selected farm profile: **{winner['Commodity']}** "
    f"with a score of **{winner['Personalized_AgriSetu_Score']:.1f}/100**"
)

a, b, c, d = st.columns(4)
a.metric("🌱 Recommended Crop", winner["Commodity"])
b.metric("⭐ Personalized Score", f"{winner['Personalized_AgriSetu_Score']:.1f}/100")
c.metric("💰 Estimated Price", f"₹ {winner['Market_Price_Estimate']:,.0f}")
d.metric("📏 Land Size", f"{land:.1f} acres")

st.divider()

st.header("🥇 Your Personalized Crop Rankings")

ranked = data[[
    "Commodity", "Your_Farm_Suitability", "Enhanced_Market_Score",
    "Market_Price_Estimate", "Price_Volatility", "Personalized_AgriSetu_Score"
]].copy()

st.dataframe(
    ranked.style.format({
        "Your_Farm_Suitability": "{:.0f}/100",
        "Enhanced_Market_Score": "{:.1f}/100",
        "Market_Price_Estimate": "₹ {:,.2f}",
        "Price_Volatility": "{:.2f}",
        "Personalized_AgriSetu_Score": "{:.1f}/100",
    }),
    use_container_width=True,
    hide_index=True
)

st.bar_chart(
    data.set_index("Commodity")["Personalized_AgriSetu_Score"],
    use_container_width=True
)

st.divider()

st.header("🔍 Explore a Crop")
selected = st.selectbox("Choose a crop", data["Commodity"])
crop = data[data["Commodity"] == selected].iloc[0]

x, y, z = st.columns(3)
x.metric("Farm Suitability", f"{crop['Your_Farm_Suitability']:.0f}/100")
y.metric("Market Intelligence", f"{crop['Enhanced_Market_Score']:.1f}/100")
z.metric("Final Personalized Score", f"{crop['Personalized_AgriSetu_Score']:.1f}/100")

st.subheader("💰 Price Intelligence")
p1, p2, p3 = st.columns(3)
p1.metric("Historical Average", f"₹ {crop['Historical_Price']:,.2f}")
p2.metric("ML Predicted Price", f"₹ {crop['ML_Predicted_Price']:,.2f}")
p3.metric("Market Price Estimate", f"₹ {crop['Market_Price_Estimate']:,.2f}")

st.info(
    "How the recommendation works: your selected farm conditions determine a transparent "
    "farm-suitability score (60%), while the Kaggle-generated market intelligence score "
    "contributes 40%. Price values shown come from your project's existing dataset/ML output."
)

st.divider()
st.header("📈 Full Market Intelligence")

st.dataframe(
    market[[
        "Commodity", "Historical_Price", "ML_Predicted_Price",
        "Market_Price_Estimate", "Price_Volatility",
        "Market_Count", "Enhanced_Market_Score"
    ]].style.format({
        "Historical_Price": "₹ {:,.2f}",
        "ML_Predicted_Price": "₹ {:,.2f}",
        "Market_Price_Estimate": "₹ {:,.2f}",
        "Price_Volatility": "{:.2f}",
        "Enhanced_Market_Score": "{:.1f}",
    }),
    use_container_width=True,
    hide_index=True
)

st.subheader("Historical vs ML Predicted Price")
st.bar_chart(
    market.set_index("Commodity")[["Historical_Price", "ML_Predicted_Price"]],
    use_container_width=True
)

st.download_button(
    "⬇️ Download Your Personalized Recommendations",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="agrisetu_personalized_recommendations.csv",
    mime="text/csv"
)

st.caption("AgriSetu AI • Decision-support prototype • Recommendations should be validated with local agronomy and market conditions.")
