import random
import numpy as np


FARBEN = ["♠", "♥", "♦", "♣"]
WERTE = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "B", "D", "K", "A"]

KARTEN_WERT = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "B": 10, "D": 10, "K": 10, "A": 11
}


def neue_karte() -> str:
    return random.choice(WERTE) + random.choice(FARBEN)


def karte_wert(karte: str) -> int:
    return KARTEN_WERT[karte[:-1]]


def deck_erstellen(decks: int) -> list[str]:
    deck = [neue_karte() for _ in range(decks * 52)]
    random.shuffle(deck)
    return deck


def hand_wert(hand: list[str]) -> int:
    wert = sum(karte_wert(k) for k in hand)
    asse = sum(1 for k in hand if k.startswith("A"))

    while wert > 21 and asse > 0:
        wert -= 10
        asse -= 1

    return wert


def hi_lo_wert(karte: str) -> int:
    rang = karte[:-1]
    if rang in ["2", "3", "4", "5", "6"]:
        return 1
    if rang in ["10", "B", "D", "K", "A"]:
        return -1
    return 0


def einfache_strategie(hand: list[str]) -> bool:
    return hand_wert(hand) < 17


def simulation(
    haende: int = 1000,
    decks: int = 6,
    penetration: float = 0.75,
    count_aktiv: bool = False,
    seed: int | None = None
) -> dict:

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    deck = deck_erstellen(decks)
    running_count = 0

    kapital = 1000.0
    ergebnisse = []
    kapital_verlauf = []

    mischgrenze = int(52 * decks * (1 - penetration))

    for _ in range(haende):
        if len(deck) < mischgrenze:
            deck = deck_erstellen(decks)
            running_count = 0

        verbleibende_decks = max(len(deck) / 52, 1.0)
        true_count = running_count / verbleibende_decks

        einsatz = 1
        if count_aktiv:
            if true_count > 4:
                einsatz = 8
            elif true_count > 2:
                einsatz = 4

        spieler = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        for k in spieler + dealer:
            running_count += hi_lo_wert(k)

        spieler_wert = hand_wert(spieler)
        dealer_wert = hand_wert(dealer)

        # Natural Blackjack (3:2)
        if spieler_wert == 21 and len(spieler) == 2:
            if dealer_wert == 21:
                gewinn = 0
            else:
                gewinn = 1.5 * einsatz
        else:
            while einfache_strategie(spieler):
                karte = deck.pop()
                spieler.append(karte)
                running_count += hi_lo_wert(karte)

            spieler_wert = hand_wert(spieler)

            while dealer_wert < 17:
                karte = deck.pop()
                dealer.append(karte)
                running_count += hi_lo_wert(karte)
                dealer_wert = hand_wert(dealer)

            if spieler_wert > 21:
                gewinn = -einsatz
            elif dealer_wert > 21 or spieler_wert > dealer_wert:
                gewinn = einsatz
            elif spieler_wert < dealer_wert:
                gewinn = -einsatz
            else:
                gewinn = 0

        kapital += gewinn
        ergebnisse.append(gewinn)
        kapital_verlauf.append(kapital)

    arr = np.array(ergebnisse, dtype=float)

    return {
        "mittelwert": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "endkapital": float(kapital),
        "kapital_verlauf": kapital_verlauf,
        "ergebnisse": arr.tolist()
    }