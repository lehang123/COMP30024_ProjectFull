from environment import Environment
from boby.model import Model
from boby.vectorize import characteristic_vectorize
from boby.td_leaf_agent import TdLeafAgent
from alice.human_agent import HumanAgent
import tensorflow as tf
import json

def main():
    log_dir = './boby/weight.json'
    env = Environment()
    model = Model(7)

    with open(log_dir) as file:
        dic = json.load(file)
        weight = dic['weight']
        print("play weight : " + str(weight))
        with tf.Session() as sess:
            agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
            agent.load_weight(weight)

            human = HumanAgent(env)

            players = [agent, human]
            env.play(players)


    # with tf.train.SingularMonitoredSession(checkpoint_dir=log_dir) as sess:
    #     agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
    #     human = HumanAgent(env)
    #
    #     players = [agent, human]
    #     env.play(players)

if __name__ == "__main__":
    main()