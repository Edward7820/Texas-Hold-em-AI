from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
import random

class CallPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        # print(f"valid actions: {valid_actions}")
        # print(f"hole card: {hole_card}")
        # print(f"round state: {round_state}")
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        # game_info format => {'player_num': 2, 
        # 'rule': {'initial_stack': 1000, 'max_round': 20, 'small_blind_amount': 5, 'ante': 0, 'blind_structure': {}},
        # 'seats': [{'name': 'p1', 'uuid': 'ekygljctfkwbvsmxcvnqkc', 'stack': 1000, 'state': 'participating'}, {'name': 'p2', 'uuid': 'lnnrtbaxtewcewhhskwrbm', 'stack': 1000, 'state': 'participating'}]}
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        # round_count => int
        # hole_count format => ['CT', 'S4']
        # seats format => [{'name': 'p1', 'uuid': 'anhxuzprzeslfdkbelzovz', 'stack': 1065, 'state': 'participating'}, {'name': 'p2', 'uuid': 'sqmngravbajetfbqtarabx', 'stack': 920, 'state': 'participating'}]
        pass

    def receive_street_start_message(self, street, round_state):
        # round_state format => {'street': 'river',
        # 'pot': {'main': {'amount': 20}, 'side': []},
        # 'community_card': ['C3', 'HA', 'C4', 'H3', 'D4'],
        # 'dealer_btn': 1, 'next_player': 0, 'small_blind_pos': 0,
        # 'big_blind_pos': 1, 'round_count': 20, 'small_blind_amount': 5,
        # 'seats': [{'name': 'p1', 'uuid': 'anhxuzprzeslfdkbelzovz', 'stack': 1060, 'state': 'participating'}, {'name': 'p2', 'uuid': 'sqmngravbajetfbqtarabx', 'stack': 920, 'state': 'participating'}],
        # 'action_histories': {'preflop': [{'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'sqmngravbajetfbqtarabx'}, {'action': 'CALL', 'amount': 10, 'paid': 5, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 10, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'flop': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'turn': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'river': []}}
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return CallPlayer()
