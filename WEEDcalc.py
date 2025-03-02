
import streamlit as st
import pandas as pd
import altair as alt

# Set page title and icon
st.set_page_config(page_title="Bet Bud", page_icon="🍀")
st.title("Bet Bud")

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
            width: 150px !important;
            height: 40px !important;
            font-size: 14px !important;
        }
        .delete-button > button {
            margin-left: -100px !important;
        }
        .stSlider > div > div {
            height: 8px !important;
            background: linear-gradient(to right, #00FF00, #FFFF00, #FF0000) !important;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Initialize session state
if "pot_log" not in st.session_state:
    st.session_state["pot_log"] = []
if "base_pot" not in st.session_state:
    st.session_state["base_pot"] = 0

# Calculate Global Statistics
def get_global_stats():
    pot_log = st.session_state["pot_log"]
    total_bets = len(pot_log)
    total_bet_amount = sum(bet["bet_size"] for bet in pot_log)
    average_bet_size = total_bet_amount / total_bets if total_bets > 0 else 0
    largest_bet = max((bet["bet_size"] for bet in pot_log), default=0)
    smallest_bet = min((bet["bet_size"] for bet in pot_log), default=0)
    return total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet

# Display Global Stats
if st.session_state["pot_log"]:
    total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet = get_global_stats()
    st.subheader("📊 Global Stats")
    st.markdown(f"""
    - **Total Bets:** {total_bets}
    - **Total Bet Amount:** {total_bet_amount:.4f}
    - **Average Bet Size:** {average_bet_size:.4f}
    - **Largest Bet:** {largest_bet:.4f}
    - **Smallest Bet:** {smallest_bet:.4f}
    """)

# Layout
col1, col2 = st.columns([2, 1])

# Inputs and reset button
with col1:
    total_pot = st.number_input("Total Pot", value=420.0, min_value=0.0, format="%.4f")
    if st.session_state["base_pot"] == 0 and total_pot > 0:
        st.session_state["base_pot"] = total_pot

    percentage = st.slider("Bet Percentage", min_value=1, max_value=100, value=50, step=1)
    parts = st.number_input("Split into Parts", min_value=1, max_value=1000, value=2, step=1)

    if st.button("Log Bet"):
        if total_pot > 0:
            bet_size = total_pot * (percentage / 100)
            split_bet_size = bet_size / parts
            st.session_state["pot_log"].append({
                "bet_size": bet_size,
                "percentage": percentage,
                "parts": parts,
                "split_bet_size": split_bet_size
            })
            st.session_state["pot_log"] = st.session_state["pot_log"][-5:]
            st.success(f"Logged Bet: {bet_size:.4f} split into {parts} parts of {split_bet_size:.4f} each")
        else:
            st.error("Invalid Total Pot. Please input a valid number.")

    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()

# Graph on the right
with col2:
    if st.session_state["pot_log"]:
        df = pd.DataFrame({
            "Entry": range(1, len(st.session_state["pot_log"]) + 1),
            "Bet Size": [bet["bet_size"] for bet in st.session_state["pot_log"]]
        })
        df = df.tail(5)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Entry:O", title="Log Entry"),
            y=alt.Y("Bet Size:Q", title="Bet Size"),
            color=alt.value("#00FF00")
        ).properties(width=350, height=250)

        st.altair_chart(chart)

        st.subheader("Remove a Logged Bet")
        bet_labels = [f"Entry {i+1}: {bet['bet_size']:.4f} split into {bet['parts']} parts of {bet['split_bet_size']:.4f} each" for i, bet in enumerate(st.session_state["pot_log"])]
        col3, col4 = st.columns([3, 1])
        with col3:
            selected_bet = st.selectbox("Select a bet to remove:", options=bet_labels, index=None)
        with col4:
            st.markdown("<div class='delete-button' style='width: 150px; display: inline-block;'>", unsafe_allow_html=True)
            if st.button("Delete Selected Bet"):
                if selected_bet:
                    index_to_remove = bet_labels.index(selected_bet)
                    del st.session_state["pot_log"][index_to_remove]
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No bets logged yet. Start by entering your total pot and logging a bet.")
