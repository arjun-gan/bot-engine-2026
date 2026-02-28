import random
from pkbot.actions import ActionFold, ActionCall, ActionCheck, ActionRaise, ActionBid


class Player:
    def __init__(self):
        # Opponent tracking
        self.opp_fold_count = 0
        self.opp_raise_count = 0
        self.round_count = 0

    # ---------------------------
    # Utility Functions
    # ---------------------------

    def card_rank(self, card):
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                 '7': 7, '8': 8, '9': 9, 'T': 10,
                 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return ranks[card[0]]

    def preflop_strength(self, hand):
        r1 = self.card_rank(hand[0])
        r2 = self.card_rank(hand[1])

        # Pocket pair
        if r1 == r2:
            return 0.6 + r1 / 20.0

        # Suited bonus
        suited_bonus = 0.05 if hand[0][1] == hand[1][1] else 0

        return (r1 + r2) / 30.0 + suited_bonus

    def postflop_strength(self, hand, board):
        all_cards = hand + board
        ranks = [self.card_rank(c) for c in all_cards]

        rank_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1

        max_count = max(rank_counts.values())

        # Simple heuristic scoring
        if max_count >= 4:
            return 0.95
        if max_count == 3:
            return 0.75
        if list(rank_counts.values()).count(2) >= 2:
            return 0.7
        if max_count == 2:
            return 0.55

        return max(ranks) / 20.0

    # ---------------------------
    # Engine Callbacks
    # ---------------------------

    def on_hand_start(self, game_info, current_state):
        self.round_count += 1

    def on_hand_end(self, game_info, current_state):
        if current_state.is_terminal:
            if current_state.payoff > 0 and current_state.opp_revealed_cards:
                pass

    # ---------------------------
    # Main Decision Function
    # ---------------------------

    def get_move(self, game_info, current_state):

        legal = current_state.legal_actions
        street = current_state.street

        # ---------------------------
        # AUCTION STRATEGY
        # ---------------------------
        if street == "auction":
            strength = self.postflop_strength(current_state.my_hand,
                                              current_state.board)

            # Second-price auction logic:
            # Bid proportional to strength but capped
            bid = int(strength * 200)

            bid = min(bid, current_state.my_chips)

            return ActionBid(max(0, bid))

        # ---------------------------
        # PREFLOP
        # ---------------------------
        if street == "preflop":
            strength = self.preflop_strength(current_state.my_hand)

            if current_state.can_act(ActionRaise) and strength > 0.75:
                min_raise, max_raise = current_state.raise_bounds
                raise_amt = min(max_raise, min_raise + 100)
                return ActionRaise(raise_amt)

            if current_state.can_act(ActionCall) and strength > 0.5:
                return ActionCall()

            if current_state.can_act(ActionCheck):
                return ActionCheck()

            return ActionFold()

        # ---------------------------
        # POSTFLOP (flop/turn/river)
        # ---------------------------
        strength = self.postflop_strength(current_state.my_hand,
                                          current_state.board)

        pot = current_state.pot
        cost = current_state.cost_to_call

        # Strong hand → raise
        if strength > 0.8 and current_state.can_act(ActionRaise):
            min_raise, max_raise = current_state.raise_bounds
            raise_amt = min(max_raise, min_raise + int(pot * 0.5))
            return ActionRaise(raise_amt)

        # Medium hand → call/check
        if strength > 0.55:
            if current_state.can_act(ActionCall):
                return ActionCall()
            if current_state.can_act(ActionCheck):
                return ActionCheck()

        # Weak hand → bluff sometimes
        if strength < 0.4 and random.random() < 0.1:
            if current_state.can_act(ActionRaise):
                min_raise, max_raise = current_state.raise_bounds
                return ActionRaise(min_raise)

        if current_state.can_act(ActionCheck):
            return ActionCheck()

        if current_state.can_act(ActionCall) and cost < pot * 0.2:
            return ActionCall()

        return ActionFold()