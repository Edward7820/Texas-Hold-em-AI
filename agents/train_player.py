from game.players import BasePokerPlayer
from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
from src.DQN_model import DQN
from src.utils import round_state_to_features
import random
import torch.nn as nn
import torch.optim as optim
import torch
# Reference: https://github.com/hungtuchen/pytorch-dqn

def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)

class TrainPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    
    def __init__(self, num_actions = 7):
        self.DQN = DQN(num_actions=num_actions)
        self.target_DQN = DQN(num_actions=num_actions)
        self.DQN.apply(init_weights)
        self.target_DQN.load_state_dict(self.DQN.state_dict())
        for p in self.target_DQN.parameters():
            p.requires_grad = False

        self.replay_buffer = []
        self.optimizer = optim.Adam(self.DQN.parameters())
        self.criterion = nn.MSELoss()
        self.num_actions = num_actions
        self.step = 0
        self.learning_freq = 1
        self.target_update_freq = 8
        self.learning_start_step = 20
        self.checkpoint_period = 500
        self.batch_size = 16
        self.gamma = 0.99

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
        stack = valid_actions[2]["amount"]["max"]
        if stack < 0:
            stack = 0
        reward = (stack - self.last_stack)/self.total_stack
        if self.last_state != None:
            self.replay_buffer.append((self.last_state, self.last_action, reward, state_feature))
            print("add a record to the replay buffer: ",end="")
            print((self.last_state, self.last_action, reward, state_feature))
        self.last_state = state_feature
        self.last_stack = stack
        
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
            
            if self.step < self.learning_start_step:
                action_id = random.randrange(self.num_actions)
            else:
                action_id = self.select_epsilon_greedy_action(state_feature, 0.3)
            self.last_action = action_id
            # print(f"choose action {all_actions[action_id]} at step {self.step}")
        except:
            print("error in action selection")

        try:
            if self.step >= self.learning_start_step and self.step % self.learning_freq == 0:
                batch = random.sample(self.replay_buffer, self.batch_size)
                # print(f"sample batch {batch} at step {self.step}")
                state_batch = torch.Tensor([record[0] for record in batch])
                action_batch = torch.Tensor([record[1] for record in batch]).to(dtype=torch.int64)
                reward_batch = torch.Tensor([record[2] for record in batch])
                nxt_state_batch = torch.Tensor([record[3] for record in batch])

                current_Q_values = self.DQN(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze() # shape: (batch_size,)
                next_Q_values = self.target_DQN(nxt_state_batch).detach().max(1)[0] # shape: (batch_size,)
                target_Q_values = reward_batch + self.gamma*next_Q_values
                bellman_error = self.criterion(current_Q_values, target_Q_values)
                print(f"loss in step {self.step} is {bellman_error}")
                self.optimizer.zero_grad()
                bellman_error.backward()
                self.optimizer.step()
            if self.step % self.target_update_freq == 0 and self.step >= self.learning_start_step:
                self.target_DQN.load_state_dict(self.DQN.state_dict())
            if self.step % self.checkpoint_period == 0 and self.step >= self.learning_start_step:
                torch.save(self.DQN.state_dict(), f"src/model_{self.step}.pth")
        except:
            print(f"error in training process at step {self.step}!")

        self.step += 1
        action, amount = all_actions[action_id][0], all_actions[action_id][1]
        return action, amount  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        # game_info format => {'player_num': 2, 
        # 'rule': {'initial_stack': 1000, 'max_round': 20, 'small_blind_amount': 5, 'ante': 0, 'blind_structure': {}},
        # 'seats': [{'name': 'p1', 'uuid': 'ekygljctfkwbvsmxcvnqkc', 'stack': 1000, 'state': 'participating'}, {'name': 'p2', 'uuid': 'lnnrtbaxtewcewhhskwrbm', 'stack': 1000, 'state': 'participating'}]}
        self.game_info = game_info
        self.total_stack = game_info["player_num"]*game_info["rule"]["initial_stack"]
        self.last_state = None
        self.last_action = None
        self.last_stack = game_info['rule']['initial_stack']

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
    return TrainPlayer()