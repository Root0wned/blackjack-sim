# app.py
import streamlit as st
import pandas as pd, time
from simulation import BlackjackSimulator

st.set_page_config(page_title="Blackjack Simulator", layout="centered")
st.title("Blackjack Monte-Carlo Simulator (educational)")

with st.sidebar.expander("Simulation parameters", True):
    num_decks = st.selectbox("Number of decks", [1,4,6,8], index=2)
    penetration = st.slider("Penetration (fraction of shoe played)", 0.5, 0.95, 0.75, 0.05)
    counting_on = st.checkbox("Enable Hi-Lo counting", value=True)
    spread = st.slider("Spread (max multiplier)", 1, 32, 8)
    min_bet = st.number_input("Minimum bet (units)", min_value=1.0, value=1.0, step=1.0)
    max_bet = st.number_input("Maximum bet (units)", min_value=1.0, value=50.0, step=1.0)
    num_hands = st.number_input("Number of hands (N)", min_value=1000, value=50000, step=1000)
    seed = st.number_input("Random seed (0 = random)", min_value=0, value=0, step=1)
    run_button = st.button("Run simulation")

st.markdown("## Notes")
st.markdown("- Educational simulator with approximate Basic Strategy and Hi-Lo counting.")
st.markdown("- For reproducibility, set a random seed. For quick tests use N=50000.")

if run_button:
    cfg = {
        'num_decks': int(num_decks),
        'penetration': float(penetration),
        'min_bet': float(min_bet),
        'max_bet': float(max_bet),
        'spread': int(spread),
        'counting_on': bool(counting_on),
        'num_hands': int(num_hands),
        'initial_bankroll': 1000.0,
        'log_hands': False,
        'verbose': False,
        'seed': None if seed==0 else int(seed)
    }
    st.info("Starting simulation... this can take a while for large N.")
    sim = BlackjackSimulator(cfg)
    start = time.time()
    res = sim.run()
    duration = time.time() - start
    st.success(f"Simulation finished in {duration:.1f}s")
    st.write("Summary:")
    st.write(pd.DataFrame([{
        'hands': res.hands,
        'mean_return_per_hand (min-bet units)': res.mean_return_per_hand,
        'sd_return_per_hand (units)': res.sd_return_per_hand,
        'final_bankroll': res.bankroll_end
    }]))
