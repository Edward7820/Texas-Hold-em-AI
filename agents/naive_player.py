from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
import random

class NaivePlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        print(f"receive round state {round_state}")
        # list unseen cards
        hole_card = [Card.from_str(card_str) for card_str in hole_card]
        hole_card_ids = [card.to_id() for card in hole_card]
        community_card = [Card.from_str(card_str) for card_str in round_state['community_card']]
        community_card_ids = [card.to_id() for card in community_card]
        unseen_card_ids = [card_id for card_id in range(1,53) if card_id not in community_card_ids + hole_card_ids]

        win_count = 0
        for _ in range(20):
            # fill community cards
            num_remain_com_card = 5 - len(community_card_ids)
            filled_community_card_ids = community_card_ids + random.sample(unseen_card_ids, num_remain_com_card)
            filled_community_card = [Card.from_id(card_id) for card_id in filled_community_card_ids]
            # print(community_card_ids, filled_community_card_ids)

            # guess the hole cards of our oponents
            nb_players = len(round_state['seats'])
            unseen_card_ids = [card_id for card_id in range(1,53) if card_id not in filled_community_card_ids + hole_card_ids]
            other_hole_card_ids = random.sample(unseen_card_ids, 2*(nb_players-1))
            other_hole_card = [Card.from_id(card_id) for card_id in other_hole_card_ids]
            oponents_hole_card = [other_hole_card[(2*i):(2*i+2)] for i in range(nb_players-1)]
            # print(hole_card_ids, other_hole_card_ids)

            # evaluate the rank of our oponents and ourselves
            oponents_score = [HandEvaluator.eval_hand(hole, filled_community_card) for hole in oponents_hole_card]
            my_score = HandEvaluator.eval_hand(hole_card, filled_community_card)
            # print(my_score, oponents_score)
            if my_score > max(oponents_score):
                win_count += 1

        win_rate = win_count / 20
        # print(f"street: {round_state['street']}, win rate: {win_rate}")
        raise_action_info = valid_actions[2]
        call_action_info = valid_actions[1]
        fold_action_info = valid_actions[0]
        action, amount = fold_action_info['action'], fold_action_info['amount']
        if win_rate >= 0.75:
            action, amount = raise_action_info['action'], raise_action_info['amount']['max']
        elif win_rate >= 0.6:
            raise_max = raise_action_info['amount']['max']
            raise_min = raise_action_info['amount']['min']
            action = raise_action_info['action']
            amount = int((raise_max+raise_min)/4)
        elif win_rate >= 0.5:
            action, amount = call_action_info['action'], call_action_info['amount']
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
        # 'pot': {'main': {'amount': 20}, 'side': []}, 'community_card': ['C3', 'HA', 'C4', 'H3', 'D4'], 'dealer_btn': 1, 'next_player': 0, 'small_blind_pos': 0, 'big_blind_pos': 1, 'round_count': 20, 'small_blind_amount': 5, 'seats': [{'name': 'p1', 'uuid': 'anhxuzprzeslfdkbelzovz', 'stack': 1060, 'state': 'participating'}, {'name': 'p2', 'uuid': 'sqmngravbajetfbqtarabx', 'stack': 920, 'state': 'participating'}], 'action_histories': {'preflop': [{'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'sqmngravbajetfbqtarabx'}, {'action': 'CALL', 'amount': 10, 'paid': 5, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 10, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'flop': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'turn': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'anhxuzprzeslfdkbelzovz'}, {'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': 'sqmngravbajetfbqtarabx'}], 'river': []}}
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(f"receive round result message {winners}, {hand_info}!")
        pass

def setup_ai():
    return NaivePlayer()