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
            split_bet_size = bet_size / parts  # Compute per-part bet size
            st.session_state["pot_log"].append({
                "bet_size": bet_size,
                "percentage": percentage,
                "parts": parts,
                "split_bet_size": split_bet_size
            })
            
            # Keep only the last 5 bets in session state
            st.session_state["pot_log"] = st.session_state["pot_log"][-5:]
            
            st.success(f"Logged Bet: {bet_size:.4f} split into {parts} parts of {split_bet_size:.4f} each")
        else:
            st.error("Invalid Total Pot. Please input a valid number.")

    # Full reset button
    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()  # Forces Streamlit to restart and clear all session data

# Graph on the right
with col2:
    if st.session_state["pot_log"]:
        df = pd.DataFrame({
            "Entry": range(1, len(st.session_state["pot_log"]) + 1),
            "Bet Size": [bet["bet_size"] for bet in st.session_state["pot_log"]]
        })
        
        # Ensure only the last 5 bets are shown
        df = df.tail(5)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Entry:O", title="Log Entry"),
            y=alt.Y("Bet Size:Q", title="Bet Size"),
            color=alt.value("#00FF00")  # Consistent green color
        ).properties(width=350, height=250)

        st.altair_chart(chart)

        # Allow deletion of specific bets
        st.subheader("Remove a Logged Bet")
        if st.session_state["pot_log"]:
            bet_labels = [f"Entry {i+1}: {bet['bet_size']:.4f}" for i, bet in enumerate(st.session_state["pot_log"])]
            bet_to_remove = st.selectbox("Select a bet to remove:", options=bet_labels, index=None)
            if st.button("Delete Selected Bet") and bet_to_remove:
                index_to_remove = bet_labels.index(bet_to_remove)
                del st.session_state["pot_log"][index_to_remove]
                st.rerun()
