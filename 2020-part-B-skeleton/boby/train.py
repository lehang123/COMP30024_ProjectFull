import tensorflow as tf
import json

from boby.model import Model
from boby.random_agent import RandomAgent
from boby.td_leaf_agent import TdLeafAgent
from boby.vectorize import pieces_positions_vectorize, characteristic_vectorize
from environment import Environment


def main():
    env = Environment()
    model = Model(7)

    with tf.Session() as sess :
        agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
        random_agent = RandomAgent(env)
        # episode_count = sess.run(agent.episode_count)
        # agent.train(.2)
        # sess.run(agent.increment_episode_count)
        episode_count = sess.run(agent.episode_count)
        while episode_count < 100:
            episode_count = sess.run(agent.episode_count)
            print("episode_count : " + str(episode_count))
            agent.train(.1)
            sess.run(agent.increment_episode_count)

        # train finished, record weight
        with open('weight.json', 'w', encoding='utf-8') as f:
            trainable_variables = model.trainable_variables.eval()
            # print("trainable variable : " + str(trainable_variables))

            weight_list = []
            for tav in trainable_variables:
                weight_list.append((tav[0]).item())
            # print("wieght list : " + str(weight_list))
            dic = {"weight" : weight_list}
            json.dump(dic, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
