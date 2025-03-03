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

# Main page layout
col1, col2 = st.columns([2, 1])
with col1:
    total_pot = st.number_input("Total Pot", value=420.0, min_value=0.0, format="%.4f")
    percentage = st.slider("Bet Percentage", min_value=1, max_value=100, value=50, step=1)
    parts = st.number_input("Split into Parts", min_value=1, max_value=1000, value=2, step=1)

    if st.button("Log Bet"):
        if total_pot > 0:
            bet_size = total_pot * (percentage / 100)
            split_bet_size = bet_size / parts
            st.session_state["pot_log"].append({
                "total_pot": total_pot,
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

# Statistics and chart
if st.session_state["pot_log"]:
    total_bets, total_bet_amount, average_bet_size, largest_bet, smallest_bet = get_global_stats()

    stat_col, chart_col = st.columns([2, 1])
    with stat_col:
        st.subheader("📊 Global Statistics")
        st.markdown(
            f"- **Total Bets:** {total_bets}\n"
            f"- **Total Bet Amount:** {total_bet_amount:.4f}\n"
            f"- **Average Bet Size:** {average_bet_size:.4f}\n"
            f"- **Largest Bet:** {largest_bet:.4f}\n"
            f"- **Smallest Bet:** {smallest_bet:.4f}"
        )

        st.subheader("📤 Export Bet Log")
        csv = export_bets_to_csv()
        st.download_button(
            label="Download Bet Log as CSV",
            data=csv,
            file_name="bet_log.csv",
            mime="text/csv",
        )

    with chart_col:
        df = pd.DataFrame({
            "Entry": range(1, len(st.session_state["pot_log"]) + 1),
            "Total Pot": [bet["total_pot"] for bet in st.session_state["pot_log"]],
        })
        df["Change"] = df["Total Pot"].diff().fillna(0)

        st.markdown("#### 📊 Total Pot Trend & Fluctuations (Compact)")

        small_bars = alt.Chart(df).mark_bar().encode(
            x=alt.X("Entry:O", title=""),
            y=alt.Y("Change:Q", title=""),
            color=alt.condition(
                alt.datum.Change > 0,
                alt.value("#00FF00"),
                alt.value("#FF0000")
            )
        )

        small_line = alt.Chart(df).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("Entry:O"),
            y=alt.Y("Total Pot:Q"),
            color=alt.value("#FFFF00")
        )

        small_combo_chart = (small_bars + small_line).properties(
            width=350,
            height=200
        )

        st.altair_chart(small_combo_chart, use_container_width=False)

        st.markdown(
            """
            <small>
            <b>Entry</b>: Bet number · 
            <b>Total Pot</b>: Pot value entered · 
            <b>Change</b>: Difference from previous pot<br>
            <span style="color:#00FF00;"><b>Green bars</b></span> = Gains · 
            <span style="color:#FF0000;"><b>Red bars</b></span> = Losses · 
            <span style="color:#FFFF00;"><b>Yellow line</b></span> = Total Pot over time
            </small>
            """,
            unsafe_allow_html=True
        )

        with st.expander("🔍 Expand for Full Chart & Meandering Analysis"):
            large_bars = alt.Chart(df).mark_bar().encode(
                x=alt.X("Entry:O", title="Entry (Bet #)"),
                y=alt.Y("Change:Q", title="Change in Pot"),
                color=alt.condition(
                    alt.datum.Change > 0,
                    alt.value("#00FF00"),
                    alt.value("#FF0000")
                )
            )

            large_line = alt.Chart(df).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X("Entry:O"),
                y=alt.Y("Total Pot:Q"),
                color=alt.value("#FFFF00")
            )

            large_combo_chart = (large_bars + large_line).properties(
                width=700,
                height=400
            )

            st.altair_chart(large_combo_chart, use_container_width=False)

            st.markdown("""
            ### 🧭 Reading the Graph:
            - **Yellow Line**: Tracks your pot's journey over time.
            - **Green Bars**: Show gains from the previous entry.
            - **Red Bars**: Show losses from the previous entry.
            
            Look for streaks, spikes, and dips to understand the flow of your betting.
            """)
