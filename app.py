import streamlit as st
import matplotlib.pyplot as plt
from simulation import simulation_starten

st.title("Blackjack Simulation")

st.write("""
Diese Simulation zeigt:

• durchschnittlichen Gewinn oder Verlust  
• Risiko durch Schwankungen  
• Einfluss von Kartenzählen  

Man kann vergleichen:
ohne Kartenzählen vs mit Kartenzählen.
""")

st.sidebar.header("Einstellungen")

haende = st.sidebar.number_input(
    "Anzahl Hände",
    1000, 200000, 50000, 1000
)

decks = st.sidebar.slider("Anzahl Decks", 1, 8, 6)

penetration = st.sidebar.slider(
    "Penetration",
    0.5, 0.95, 0.75
)

count = st.sidebar.checkbox("Kartenzählen verwenden")

if st.button("Simulation starten"):

    ergebnis = simulation_starten(
        haende=haende,
        decks=decks,
        penetration=penetration,
        count_aktiv=count
    )

    st.subheader("Ergebnisse")

    st.write(f"Durchschnitt pro Hand: {ergebnis['mittelwert']:.4f}")
    st.write(f"Schwankung: {ergebnis['std']:.2f}")
    st.write(f"Endkapital: {ergebnis['endkapital']:.2f}")

    st.subheader("Kapitalverlauf")

    fig, ax = plt.subplots()
    ax.plot(ergebnis["kapital_verlauf"])
    ax.set_xlabel("Hände")
    ax.set_ylabel("Kapital")

    st.pyplot(fig)

    st.info("""
Interpretation:

Negativer Wert → Casino hat Vorteil  
Positiver Wert → Spieler hat Vorteil  

Hohe Schwankungen sind normal.
""")
