# Blackjack Monte-Carlo Simulator (educational)

Beschreibung:
Dieses Repository enthält eine einfache Monte-Carlo-Simulation für Blackjack und eine Streamlit-Oberfläche zur interaktiven Ausführung von Simulationen. Die Anwendung ist für die Nutzung in einer Schularbeit erstellt worden.

Schnellstart (lokal):
1. Repo klonen: `git clone https://github.com/<DeinBenutzername>/blackjack_simulator.git`
2. Virtuelle Umgebung erstellen: `python -m venv venv` → aktivieren
3. Abhängigkeiten installieren: `pip install -r requirements.txt`
4. App starten: `streamlit run app.py`

Reproduzierbarkeit:
- Commit / Tag: `<COMMIT_HASH_HIER_EINFÜGEN>`
- Für die in der Facharbeit genutzten Runs wurden folgende Parameter verwendet: `<PARAMS_HIER_EINFÜGEN>` (z. B. 6 Decks, Penetration 0.75, Hi-Lo, spread 8, min_bet 1, max_bet 50, N=200000, seed=42)

Kontakt / Hinweise:
- Diese Implementierung ist edukativ; Basic Strategy ist eine praktische Näherung, Splits/Double sind vereinfacht.
