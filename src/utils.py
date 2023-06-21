from game.engine.card import Card
from game.engine.hand_evaluator import HandEvaluator
import random

def round_state_to_features(valid_actions, hole_card, round_state, game_info):
    try:
        total_stack = game_info["player_num"]*game_info["rule"]["initial_stack"]
        main_pot = round_state['pot']['main']['amount']/total_stack
        stack = valid_actions[2]['amount']['max']/total_stack
        if stack < 0:
            stack = 0
        street = -1
        if round_state['street'] == "preflop":
            street = 0.25
        elif round_state['street'] == "flop":
            street = 0.5
        elif round_state['street'] == "turn":
            street = 0.75
        else:
            street = 1.0
    except:
        print("error in block 1")
    
    try:
        hole_card = [Card.from_str(card_str) for card_str in hole_card]
        hole_card_ids = [card.to_id() for card in hole_card]
        community_card = [Card.from_str(card_str) for card_str in round_state['community_card']]
        community_card_ids = [card.to_id() for card in community_card]
        unseen_card_ids = [card_id for card_id in range(1,53) if card_id not in community_card_ids + hole_card_ids]
        win_count = 0
        for _ in range(50):
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
        card_score = win_count / 50

        features = [street, main_pot, stack, card_score]
        return features
    except:
        print("error in block 2")