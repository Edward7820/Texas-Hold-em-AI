from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from DQN_model import DQN
from utils import round_state_to_features
import random
import torch.nn as nn
import torch.optim as optim
import torch

class DQNPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    
    def __init__(self, num_actions = 7):
        self.DQN = DQN(num_actions=num_actions)
        self.DQN.load_state_dict(torch.load("src/model.pth"))
        self.DQN.eval()
        self.num_actions = num_actions

    def select_epsilon_greedy_action(self, state_feature, epsilon):
        sample = random.random()
        if sample > epsilon:
            output = self.DQN(torch.Tensor(state_feature))
            return int(torch.argmax(output).cpu())
        else:
            return random.randrange(self.num_actions)

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        # print(f"valid actions: {valid_actions}")
        # print(f"hole card: {hole_card}")
        # print(f"round state: {round_state}")
        state_feature = round_state_to_features(valid_actions, hole_card, round_state, self.game_info)
        
        # select the action
        try:
            raise_action_info = valid_actions[2]
            call_action_info = valid_actions[1]
            fold_action_info = valid_actions[0]
            all_actions = [[fold_action_info["action"],fold_action_info["amount"]],[call_action_info["action"],call_action_info["amount"]]]
            max_raise_amount = raise_action_info["amount"]["max"]
            min_raise_amount = raise_action_info["amount"]["min"]
            for i in range(self.num_actions-2):
                all_actions.append([raise_action_info["action"], min_raise_amount+(max_raise_amount-min_raise_amount)*i/4])
            
            output = self.DQN(state_feature)
            action_id = int(torch.argmax(output).cpu())
        except:
            print("error in action selection")
        action, amount = all_actions[action_id][0], all_actions[action_id][1]
        return action, amount  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        # game_info format => {'player_num': 2, 
        # 'rule': {'initial_stack': 1000, 'max_round': 20, 'small_blind_amount': 5, 'ante': 0, 'blind_structure': {}},
        # 'seats': [{'name': 'p1', 'uuid': 'ekygljctfkwbvsmxcvnqkc', 'stack': 1000, 'state': 'participating'}, {'name': 'p2', 'uuid': 'lnnrtbaxtewcewhhskwrbm', 'stack': 1000, 'state': 'participating'}]}
        self.game_info = game_info
        self.total_stack = game_info["player_num"]*game_info["rule"]["initial_stack"]

    def receive_round_start_message(self, round_count, hole_card, seats):
        # round_count => int
        # hole_card format => ['CT', 'S4']
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
    return DQNPlayer()