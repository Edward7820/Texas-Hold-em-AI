from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.players import BasePokerPlayer

class Emulator(object):
    def __init__(self):
        self.game_rule = {}
        self.blind_structure = {}
        self.players_holder = {}

    def set_game_rule(self, player_num, initial_stack, small_blind_amount, ante):
        self.game_rule["player_num"] = player_num
        self.game_rule["initial_stack"] = initial_stack
        self.game_rule["small_blind_amount"] = small_blind_amount
        self.game_rule["ante"] = ante

    def set_blind_structure(self, blind_structure):
        self.blind_structure = blind_structure

    def register_player(self, uuid, player):
        assert isinstance(player, BasePokerPlayer):
        self.players_holder[uuid] = player

    def fetch_player(self, uuid):
        return self.players_holder[uuid]

    def generate_initial_game_state(self, players_info):
        table = Table()
        for uuid, info in players_info.items():
            table.seats.sitdown(Player(uuid, info["stack"], info["name"]))
        table.dealer_btn = len(table.seats.players)-1
        return {
            "round_count": 0,
            "small_blind_amount": self.game_rule["small_blind_amount"],
            "street": Const.Street.PREFLOP,
            "next_player": None,
            "table": table
        }

    def generate_possible_actions(self, game_state):
        players = game_state["table"].seats.players
        player_pos = game_state["next_player"]
        sb_amount = game_state["small_blind_amount"]
        return ActionChecker.legal_actions(players, player_pos, sb_amount)

    def apply_action(self, game_state, action, bet_amount=0):
        assert game_state["street"] != Const.Street.FINISHED
        updated_state, messages = RoundManager.apply_action(game_state, action, bet_amount)
        events = [self.create_event(message[1]["message"]) for message in messages]
        events = [e for e in events if e]
        if self._is_last_round(updated_state, self.game_rule):
            events += self._generate_game_result_event(updated_state)
        return updated_state, events

    def run_until_round_finish(self, game_state):
        mailbox = []
        while game_state["street"] != Const.Street.FINISHED:
            next_player_pos = game_state["next_player"]
            next_player_uuid = game_state["table"].seats.players[next_player_pos].uuid
            next_player_algorithm = self.fetch_player(next_player_uuid)
            msg = MessageBuilder.build_ask_message(next_player_pos, game_state)["message"]
            action, amount = next_player_algorithm.declare_action(\
                    msg["valid_actions"], msg["hole_card"], msg["round_state"])
            game_state, messages = RoundManager.apply_action(game_state, action, amount)
            mailbox += messages
        events = [self.create_event(message[1]["message"]) for message in mailbox]
        events = [e for e in events if e]
        if self._is_last_round(game_state, self.game_rule):
            events += self._generate_game_result_event(game_state)
        return game_state, events

