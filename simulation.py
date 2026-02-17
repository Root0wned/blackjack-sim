# simulation.py
# (Der Code ist vollständig — falls Copy/Paste hakt, lade die Datei über "Upload files".)
import random, math
from collections import deque, namedtuple

CARD_VALUES = {
    'A': 11, 'K': 10, 'Q': 10, 'J': 10, '10': 10,
    '9':9,'8':8,'7':7,'6':6,'5':5,'4':4,'3':3,'2':2
}

HI_LO_VALUES = {
    '2': +1, '3': +1, '4': +1, '5': +1, '6': +1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def make_deck(num_decks=6):
    deck = []
    for _ in range(num_decks):
        for r in RANKS:
            deck += [r]*4
    random.shuffle(deck)
    return deque(deck)

class Shoe:
    def __init__(self, num_decks=6, penetration=0.75, seed=None):
        self.num_decks = num_decks
        self.penetration = penetration
        if seed is not None:
            random.seed(seed)
        self._reshuffle()

    def _reshuffle(self):
        self.cards = make_deck(self.num_decks)
        total = len(self.cards)
        cards_to_deal = int(total * self.penetration)
        self.cut_card_position = total - cards_to_deal

    def needs_shuffle(self):
        return len(self.cards) <= self.cut_card_position

    def draw_card(self):
        if len(self.cards) == 0:
            self._reshuffle()
        return self.cards.popleft()

    def decks_remaining(self):
        return max(0.0, len(self.cards) / 52.0)

class HiLoCounter:
    def __init__(self):
        self.running = 0
    def update(self, card):
        self.running += HI_LO_VALUES.get(card, 0)
    def running_count(self):
        return self.running
    def true_count(self, decks_remaining):
        if decks_remaining <= 0.0:
            return 0.0
        return self.running / decks_remaining

def hand_value(cards):
    total = 0
    aces = 0
    for c in cards:
        total += CARD_VALUES[c]
        if c == 'A':
            aces += 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def is_soft(cards):
    total = 0
    aces = 0
    for c in cards:
        total += CARD_VALUES[c]
        if c == 'A': aces += 1
    return (aces>0 and total <= 21)

# simplified basic strategy (practical approx.)
def basic_strategy_action(player_cards, dealer_upcard, can_double=True, can_split=True):
    up = CARD_VALUES[dealer_upcard]
    if len(player_cards) == 2 and player_cards[0] == player_cards[1] and can_split:
        rank = player_cards[0]
        if rank == 'A': return 'split'
        if rank == '8': return 'split'
        if rank in ('2','3'):
            if up in (2,3,4,5,6,7): return 'split'
            else: return 'hit'
        if rank == '4':
            if up in (5,6): return 'split'
            else: return 'hit'
        if rank == '6':
            if up in (2,3,4,5,6): return 'split'
            else: return 'hit'
        if rank == '7':
            if up in (2,3,4,5,6,7): return 'split'
            else: return 'hit'
        if rank == '9':
            if up in (2,3,4,5,6,8,9): return 'split'
            else: return 'stand'
        if rank in ('10','J','Q','K'):
            return 'stand'
    val = hand_value(player_cards)
    soft = False
    if 'A' in player_cards:
        soft = hand_value(player_cards) != sum(CARD_VALUES[c] if c!='A' else 1 for c in player_cards)
    if soft:
        if val >= 19:
            return 'stand'
        if val == 18:
            if up in (2,7,8): return 'stand'
            if up in (3,4,5,6) and can_double: return 'double'
            return 'hit'
        if val in (17,16,15,14,13):
            if up in (4,5,6) and can_double: return 'double'
            return 'hit'
    if val >= 17:
        return 'stand'
    if val >= 13 and val <= 16:
        if up in (2,3,4,5,6): return 'stand'
        else: return 'hit'
    if val == 12:
        if up in (4,5,6): return 'stand'
        else: return 'hit'
    if val == 11:
        if can_double: return 'double'
        else: return 'hit'
    if val == 10:
        if up in (2,3,4,5,6,7,8,9) and can_double: return 'double'
        else: return 'hit'
    if val == 9:
        if up in (3,4,5,6) and can_double: return 'double'
        else: return 'hit'
    return 'hit'

Result = namedtuple('Result', ['hands','mean_return_per_hand','sd_return_per_hand','bankroll_end'])

class BlackjackSimulator:
    def __init__(self, config):
        self.config = config
        self.shoe = Shoe(num_decks=config.get('num_decks',6),
                         penetration=config.get('penetration',0.75),
                         seed=config.get('seed',None))
        self.counter = HiLoCounter()
        self.bankroll = config.get('initial_bankroll',1000.0)
        self.min_bet = config.get('min_bet',1.0)
        self.max_bet = config.get('max_bet',100.0)
        self.spread = config.get('spread',16)
        self.allow_double = config.get('allow_double',True)
        self.allow_split = config.get('allow_split',True)
        self.dealer_hits_soft17 = config.get('dealer_hits_soft17',False)
        self.counting_on = config.get('counting_on',True)
        self.log_hands = config.get('log_hands',False)
        self.max_hands = config.get('num_hands',100000)
        self.verbose = config.get('verbose',False)
        self.hand_logs = []

    def _bet_from_truecount(self, tc):
        if tc <= 0:
            return self.min_bet
        base = 1 << int(tc)
        multiplier = min(base, self.spread)
        bet = self.min_bet * multiplier
        return min(bet, self.max_bet)

    def _deal_initial(self):
        p = [self.shoe.draw_card(), self.shoe.draw_card()]
        d = [self.shoe.draw_card(), self.shoe.draw_card()]
        return p, d

    def _update_count_visible(self, cards):
        for c in cards:
            self.counter.update(c)

    def _play_player_hand(self, player_cards, dealer_upcard):
        hands = [(player_cards[:], 1.0)]
        i = 0
        final_hands = []
        while i < len(hands):
            cards, bet_mul = hands[i]
            if len(cards) == 2 and set(cards) & set(['A']) and hand_value(cards) == 21:
                final_hands.append((cards, bet_mul))
                i += 1
                continue
            action = basic_strategy_action(cards, dealer_upcard, can_double=self.allow_double, can_split=self.allow_split)
            if action == 'split' and len(cards) == 2 and self.allow_split:
                a, b = cards[0], cards[1]
                hands[i] = ([a, self.shoe.draw_card()], bet_mul)
                hands.insert(i+1, ([b, self.shoe.draw_card()], bet_mul))
                self._update_count_visible([hands[i][0][-1], hands[i+1][0][-1]])
            elif action == 'double' and len(cards) == 2 and self.allow_double:
                cards.append(self.shoe.draw_card())
                self._update_count_visible([cards[-1]])
                final_hands.append((cards, bet_mul*2.0))
                i += 1
            elif action == 'hit':
                cards.append(self.shoe.draw_card())
                self._update_count_visible([cards[-1]])
                if hand_value(cards) > 21:
                    final_hands.append((cards, bet_mul))
                    i += 1
                else:
                    hands[i] = (cards, bet_mul)
            elif action == 'stand':
                final_hands.append((cards, bet_mul))
                i += 1
            else:
                final_hands.append((cards, bet_mul))
                i += 1
        return final_hands

    def _play_dealer(self, dealer_cards):
        while True:
            val = hand_value(dealer_cards)
            if val < 17:
                dealer_cards.append(self.shoe.draw_card())
            elif val == 17:
                if is_soft(dealer_cards) and self.dealer_hits_soft17:
                    dealer_cards.append(self.shoe.draw_card())
                else:
                    break
            else:
                break
        return dealer_cards

    def _settle_hand(self, player_hand_cards, dealer_cards, bet_units, is_initial_blackjack=False):
        pval = hand_value(player_hand_cards)
        dval = hand_value(dealer_cards)
        if pval > 21:
            return -bet_units
        if is_initial_blackjack and not (hand_value(dealer_cards) == 21 and len(dealer_cards) == 2):
            return 1.5 * bet_units
        if (dval == 21 and len(dealer_cards) == 2) and not (pval == 21 and len(player_hand_cards) == 2):
            return -bet_units
        if dval > 21:
            return bet_units
        if pval > dval:
            return bet_units
        if pval == dval:
            return 0.0
        return -bet_units

    def run(self):
        N = self.max_hands
        returns = []
        for hand_no in range(1, N+1):
            if self.shoe.needs_shuffle():
                self.shoe._reshuffle()
                self.counter = HiLoCounter()
            decks_rem = max(1/52.0, self.shoe.decks_remaining())
            tc = self.counter.true_count(decks_rem) if self.counting_on else 0.0
            bet = self._bet_from_truecount(tc)
            bet = max(self.min_bet, min(bet, self.max_bet))
            player_cards, dealer_cards = self._deal_initial()
            self._update_count_visible([player_cards[0], player_cards[1], dealer_cards[0]])
            player_has_blackjack = (len(player_cards)==2 and hand_value(player_cards)==21)
            dealer_has_blackjack = (len(dealer_cards)==2 and hand_value(dealer_cards)==21)
            final_player_hands = self._play_player_hand(player_cards, dealer_cards[0])
            self._update_count_visible([dealer_cards[1]])
            dealer_final = self._play_dealer(dealer_cards[:])
            total_return = 0.0
            for ph, mult in final_player_hands:
                is_init_bj = (len(ph)==2 and hand_value(ph)==21 and ph==player_cards)
                payout = self._settle_hand(ph, dealer_final, bet * mult, is_initial_blackjack=is_init_bj)
                total_return += payout
            self.bankroll += total_return
            returns.append(total_return / self.min_bet)
            if self.log_hands:
                self.hand_logs.append({
                    'hand_no': hand_no,
                    'bet': bet,
                    'tc': round(tc,3),
                    'player': list(player_cards),
                    'dealer_up': dealer_cards[0],
                    'result_units': total_return / self.min_bet,
                    'bankroll': self.bankroll
                })
        mean_ret = sum(returns)/len(returns)
        sd = (sum((x-mean_ret)**2 for x in returns)/len(returns))**0.5
        return Result(hands=len(returns), mean_return_per_hand=mean_ret, sd_return_per_hand=sd, bankroll_end=self.bankroll)

if __name__ == "__main__":
    cfg = {
        'num_decks': 6,
        'penetration': 0.75,
        'min_bet': 1.0,
        'max_bet': 50.0,
        'spread': 8,
        'counting_on': True,
        'num_hands': 200000,
        'initial_bankroll': 1000.0,
        'log_hands': False,
        'verbose': True
    }
    sim = BlackjackSimulator(cfg)
    res = sim.run()
    print("Result:", res)
