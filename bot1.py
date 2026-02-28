from pkbot import Player, ActionFold, ActionCall, ActionCheck, ActionRaise, ActionBid

class Bot(Player):
    def __init__(self):
        """
        Initialize any variables you want to track across the 1000 rounds.
        """
        self.opp_fold_count = 0
        self.opp_raise_count = 0

    def on_hand_start(self, game_info, current_state):
        """
        Called at the beginning of every round. 
        You are allocated 5000 chips at the start of each round.
        """
        # Example: Access your private hole cards
        my_cards = current_state.my_hand
        
        # Reset any per-round variables here
        pass

    def on_hand_end(self, game_info, current_state):
        """
        Called when the round finishes. 
        Use this to learn from the opponent's revealed cards and update your strategy.
        """
        if current_state.is_terminal:
            payoff = current_state.payoff
            
            # Example: Track if opponent folded
            # (You would need more advanced logic to confidently track this based on actions)
            
        pass

    def get_move(self, game_info, current_state):
        """
        This is where your main strategy lives. Called whenever the engine needs your action.
        You must return a valid action, or you will be assumed to have folded.
        """
        # 1. Handle the Sneak Peek Auction Phase
        # This happens after the flop (3 community cards) is dealt.
        if current_state.street == 'auction':
            # Example Strategy: Always bid 10 chips for the auction if possible
            bid_amount = max(10, current_state.my_chips)
            return ActionBid(bid_amount)

        # 2. Handle standard betting rounds (Pre-flop, Flop, Turn, River)
        # Check if we can Check (bet 0 chips)
        if current_state.can_act(ActionCheck):
            return ActionCheck()
            
        # Check if we can Call (match the opponent's wager)
        if current_state.can_act(ActionCall):
            return ActionCall()
            
        # As a last resort, Fold (withdraw from the hand)
        return ActionFold()