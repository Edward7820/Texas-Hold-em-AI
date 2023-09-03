import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.naive_player import setup_ai as naive_ai
from agents.train_player import setup_ai as train_ai
from agents.DQN_player import setup_ai as dqn_ai

from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
# config.register_player(name="random", algorithm=random_ai())
# config.register_player(name="baseline0", algorithm=baseline0_ai())
# config.register_player(name="baseline1",algorithm=baseline1_ai())
# config.register_player(name="baseline2",algorithm=baseline2_ai())
# config.register_player(name="baseline3",algorithm=baseline3_ai())
# config.register_player(name="baseline4",algorithm=baseline4_ai())
config.register_player(name="baseline5",algorithm=baseline5_ai())
config.register_player(name="myagent", algorithm=naive_ai())
# config.register_player(name="myagent", algorithm=train_ai())
# config.register_player(name="myagent", algorithm=dqn_ai())

## Play in interactive mode if uncomment
#config.register_player(name="me", algorithm=console_ai())

for _ in range(100):
    game_result = start_poker(config, verbose=1)

print(json.dumps(game_result, indent=4))
