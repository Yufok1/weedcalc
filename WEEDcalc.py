import streamlit as st
import pandas as pd
import altair as alt

# Set page title and icon
st.set_page_config(page_title="WEEDcalc", page_icon="🍀")
st.title("WEEDcalc")

# Apply custom styling
st.markdown(
    """
    <style>
        div[data-baseweb="input"] > div {
            background-color: #222 !important;
            color: #00FF00 !important;
            border: 2px solid #00FF00 !important;
        }
        input {
            color: #00FF00 !important;
        }
        .stButton > button {
            background-color: #00FF00 !important;
            color: #222 !important;
            font-weight: bold;
            border: 2px solid #00FF00 !important;
        }
        .stSlider > div > div {
            height: 8px !important;
            background: linear-gradient(to right, #00FF00, #FFFF00, #FF0000) !important;
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "pot_log" not in st.session_state:
    st.session_state["pot_log"] = []
if "base_pot" not in st.session_state:
    st.session_state["base_pot"] = 0

# Layout
col1, col2 = st.columns([2, 1])

# Inputs and reset button
with col1:
    total_pot = st.number_input("Total Pot", value=420.0, min_value=0.0, format="%.4f")
    if st.session_state["base_pot"] == 0 and total_pot > 0:
        st.session_state["base_pot"] = total_pot

    percentage = st.slider("Bet Percentage", min_value=1, max_value=100, value=50, step=1)
    parts = st.number_input("Split into Parts", min_value=1, max_value=1000, value=1, step=1)

    if st.button("Log Bet"):
        if total_pot > 0:
            bet_size = total_pot * (percentage / 100)
            st.session_state["pot_log"].append({"bet_size": bet_size, "percentage": percentage, "parts": parts})
            st.write("Log updated:", st.session_state["pot_log"])
        else:
            st.error("Invalid Total Pot. Please input a valid number.")

    if st.button("Reset"):
        st.session_state.clear()

# Graph on the right
with col2:
    if st.session_state["pot_log"]:
        df = pd.DataFrame({
            "Entry": range(1, len(st.session_state["pot_log"]) + 1),
            "Bet Size": [bet["bet_size"] for bet in st.session_state["pot_log"]]
        })

        st.text("Current pot log before charting:")
        st.text(str(st.session_state["pot_log"])[:100])

        chart = alt.layer(
            alt.Chart(df).mark_bar().encode(
                x=alt.X("Entry:O", title="Log Entry"),
                y=alt.Y("Bet Size:Q", title="Bet Size"),
                color=alt.condition(alt.datum['Bet Size'] > 0, alt.value("green"), alt.value("red"))
            )
        ).properties(width=300, height=200)

        st.altair_chart(chart)
