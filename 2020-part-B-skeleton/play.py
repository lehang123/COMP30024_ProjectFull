from environment import Environment
from boby.model import Model
from boby.vectorize import characteristic_vectorize, pieces_positions_vectorize
from boby.td_leaf_agent import TdLeafAgent
from calro.human_agent import HumanAgent
from alice.minimax_agent import MinimaxAgent
from alice.evaluate import prime_eval, mobility_eval
import json

def main():

    log_dir = './boby/weight_zero.json'
    env = Environment()
    minimax_agent = MinimaxAgent(env, mobility_eval, minimax_depth=4, sort_eval=mobility_eval)
    agent = HumanAgent(env)
    env.show_board()
    players = [agent, minimax_agent]
    reward = env.play(players)



    # with tf.train.SingularMonitoredSession(checkpoint_dir=log_dir) as sess:
    #     agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
    #     human = HumanAgent(env)
    #
    #     players = [agent, human]
    #     env.play(players)

if __name__ == "__main__":
    main()