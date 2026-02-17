import streamlit as st
from simulation import simulation_starten

st.title("Blackjack Simulation")

st.write("""
Diese Simulation zeigt, wie sich Gewinn, Verlust und Risiko beim Blackjack entwickeln.
Man kann vergleichen:
- Ohne Kartenzählen
- Mit Kartenzählen
""")

st.sidebar.header("Einstellungen")

anzahl_haende = st.sidebar.number_input(
    "Anzahl gespielter Hände",
    min_value=1000,
    max_value=500000,
    value=50000,
    step=1000
)

anzahl_decks = st.sidebar.slider("Anzahl Decks", 1, 8, 6)

penetration = st.sidebar.slider(
    "Penetration (wie tief gespielt wird)",
    0.5, 0.95, 0.75
)

kartenzaehlen = st.sidebar.checkbox("Kartenzählen verwenden", value=False)

if st.button("Simulation starten"):

    ergebnis = simulation_starten(
        haende=anzahl_haende,
        decks=anzahl_decks,
        penetration=penetration,
        count_aktiv=kartenzaehlen
    )

    st.subheader("Ergebnisse")

    st.write(f"Durchschnittlicher Gewinn pro Hand: {ergebnis['mittelwert']:.5f}")
    st.write(f"Schwankung (Standardabweichung): {ergebnis['std']:.3f}")
    st.write(f"Endkapital: {ergebnis['endkapital']:.2f}")

    st.info("""
Interpretation:
- Negativer Wert → Casino hat Vorteil
- Positiver Wert → Spieler hat Vorteil
- Hohe Schwankung → hohes Risiko
""")
