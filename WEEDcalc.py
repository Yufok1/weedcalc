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
    """,
    unsafe_allow_html=True
)

if "pot_log" not in st.session_state:
    st.session_state["pot_log"] = []

def get_global_stats():
    pot_log = st.session_state["pot_log"]
    total_bets = len(pot_log)
    total_bet_amount = sum(bet["bet_size"] for bet in pot_log)
    average_bet_size = total_bet_amount / total_bets if total_bets > 0 else 0
    largest_bet = max((bet["bet_size"] for bet in pot_log), default=0)
    smallest_bet = min((bet["bet_size"] for bet in pot_log), default=0)
    return total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet

def export_bets_to_csv():
    df = pd.DataFrame(st.session_state["pot_log"])
    return df.to_csv(index=False).encode('utf-8')

def generate_bar_chart(df):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("Entry:O", title="Log Entry"),
        y=alt.Y("Bet Size:Q", title="Bet Size"),
        color=alt.value("#00FF00")
    ).properties(width=600, height=300)

def generate_line_chart(df):
    return alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("Entry:O", title="Log Entry"),
        y=alt.Y("Bet Size:Q", title="Bet Size"),
        color=alt.value("#00FF00")
    ).properties(width=600, height=300)

# Main tab: Input and logging functionality
col1, _ = st.columns([2, 1])
with col1:
    total_pot = st.number_input("Total Pot", value=420.0, min_value=0.0, format="%.4f")
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
            st.success(f"Logged Bet: {bet_size:.4f} split into {parts} parts of {split_bet_size:.4f} each")
        else:
            st.error("Invalid Total Pot. Please input a valid number.")

    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()

# Statistics tab: Displaying statistics and graphs
if st.session_state["pot_log"]:
    total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet = get_global_stats()
    st.subheader("📊 Global Statistics")
    st.markdown(
        f"- **Total Bets:** {total_bets}\n"
        f"- **Total Bet Amount:** {total_bet_amount:.4f}\n"
        f"- **Average Bet Size:** {average_bet_size:.4f}\n"
        f"- **Largest Bet:** {largest_bet:.4f}\n"
        f"- **Smallest Bet:** {smallest_bet:.4f}"
    )

    # Export button
    st.subheader("📤 Export Bet Log")
    csv = export_bets_to_csv()
    st.download_button(
        label="Download Bet Log as CSV",
        data=csv,
        file_name="bet_log.csv",
        mime="text/csv",
    )

    # Graphs
    col1, col2 = st.columns(2)
    with col1:
        df = pd.DataFrame(st.session_state["pot_log"])
        st.altair_chart(generate_bar_chart(df), use_container_width=True)
    with col2:
        st.altair_chart(generate_line_chart(df), use_container_width=True)
