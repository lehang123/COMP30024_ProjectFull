from teamProject.environment import Environment
from teamProject.evaluate import mobility_eval
from teamProject.minimax_agent import MinimaxAgent
from calro.human_agent import HumanAgent
from calro.random_agent import RandomAgent


def main():

    log_dir = './boby/weight_zero.json'
    env = Environment()

    minimax_agent = MinimaxAgent(env, mobility_eval, minimax_depth=2, sort_eval=mobility_eval)
    agent = RandomAgent(env)
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