from environment import Environment
from boby.model import Model
from boby.vectorize import characteristic_vectorize
from boby.td_leaf_agent import TdLeafAgent
from alice.human_agent import HumanAgent
import tensorflow as tf

def main():
    log_dir = './boby/log/td_leaf'
    env = Environment()
    model = Model(5)


    with tf.train.SingularMonitoredSession(checkpoint_dir=log_dir) as sess:
        agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
        human = HumanAgent(env)

        players = [agent, human]
        env.play(players)

if __name__ == "__main__":
    main()