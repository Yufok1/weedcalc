import streamlit as st
import pandas as pd
import altair as alt
import io

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
if "base_pot" not in st.session_state:
    st.session_state["base_pot"] = 0

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

def import_bets_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    required_columns = {"bet_size", "percentage", "parts", "split_bet_size"}
    if required_columns.issubset(df.columns):
        st.session_state["pot_log"] = df.to_dict('records')
        st.success("Bet log successfully imported and replaced.")
        st.experimental_rerun()
    else:
        st.error("CSV is missing required columns.")

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

def generate_pie_chart(df):
    pie_df = df.copy()
    pie_df["Bet Label"] = pie_df["Entry"].apply(lambda x: f"Entry {x}")
    return alt.Chart(pie_df).mark_arc().encode(
        theta=alt.Theta(field="Bet Size", type="quantitative"),
        color=alt.Color(field="Bet Label", type="nominal")
    ).properties(width=600, height=400)

def generate_win_loss_chart(df):
    # Placeholder for win/loss ratio chart
    # This would need actual win/loss data to calculate
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("Entry:O", title="Log Entry"),
        y=alt.Y("Bet Size:Q", title="Bet Size"),
        color=alt.value("#00FF00")
    ).properties(width=600, height=300)

# Tabs
tabs = st.tabs(["Main", "Statistics"])

with tabs[0]:
    col1, _ = st.columns([2, 1])
    
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

with tabs[1]:
    if st.session_state["pot_log"]:
        total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet = get_global_stats()
        st.subheader("📊 Global Statistics")
        st.markdown(
            f"- **Total Bets:** {total_bets}\\n"
            f"- **Total Bet Amount:** {total_bet_amount:.4f}\\n"
            f"- **Average Bet Size:** {average_bet_size:.4f}\\n"
            f"- **Largest Bet:** {largest_bet:.4f}\\n"
            f"- **Smallest Bet:** {smallest_bet:.4f}"
        )

        # Import/export buttons
        st.subheader("📥 Import Bet Log")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            import_bets_from_csv(uploaded_file)

        st.subheader("📤 Export Bet Log")
        csv = export_bets_to_csv()
        st.download_button(
            label="Download Bet Log as CSV",
            data=csv,
            file_name="bet_log.csv",
            mime="text/csv",
        )

        # Graphs
        st.subheader("📊 Graphs")
        df = pd.DataFrame({
            "Entry": range(1, len(st.session_state["pot_log"]) + 1),
            "Bet Size": [bet["bet_size"] for bet in st.session_state["pot_log"]]
        })
        df = df.tail(5)

        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(generate_bar_chart(df))
        with col2:
            st.altair_chart(generate_line_chart(df))

        col3, col4 = st.columns(2)
        with col3:
            st.altair_chart(generate_pie_chart(df))
        with col4:
            st.altair_chart(generate_win_loss_chart(df))

        # Remove bet functionality
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
        st.info("No bets have been logged yet to calculate statistics.")
'''
