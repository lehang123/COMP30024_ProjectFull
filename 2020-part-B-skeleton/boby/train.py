import tensorflow as tf
import json

from boby.model import Model
from boby.td_leaf_agent import TdLeafAgent
from boby.vectorize import pieces_positions_vectorize, characteristic_vectorize, score_vectorize, ultimate_vectorize
from environment import Environment


def main():
    env = Environment()
    model = Model(128)
    # log_dir = './weight.json'
    # baseline_model = Model(7)
    # with open(log_dir) as file:
    #     dic = json.load(file)
    #     weight = dic['weight']

    with tf.Session() as sess :
        agent = TdLeafAgent(model, env, sess, pieces_positions_vectorize, minimax_depth=3)
        # baseline_agent = TdLeafAgent(baseline_model, env, sess, characteristic_vectorize)
        # baseline_agent.load_weight(weight)

        game_result = {0 : 0, 1 : 0, -1 : 0}

        def store_result():
            with open('ultimate_weight.json', 'w', encoding='utf-8') as f:
                trainable_variables = model.trainable_variables.eval()
                # print("trainable variable : " + str(trainable_variables))

                weight_list = []
                for tav in trainable_variables:
                    weight_list.append((tav[0]).item())

                result_list = [game_result[-1], game_result[0], game_result[1]]

                data = {"weight": weight_list, "game_result": result_list}
                json.dump(data, f, ensure_ascii=False, indent=4)

        episode_count = sess.run(agent.episode_count)
        while episode_count <= 1000:
            reward = agent.train(.2)
            game_result[reward] += 1

            print("game result : " + str(game_result))
            print("episode_count : " + str(episode_count))
            sess.run(agent.increment_episode_count)
            episode_count = sess.run(agent.episode_count)

            if episode_count % 10 == 0 :
                # train finished, record weight
                store_result()

        store_result()



        # while True:
        #     episode_count = sess.run(agent.episode_count)
        #     reward = agent.train(.2)
        #     game_result[reward] += 1
        #     print("game result : " + str(game_result))
        #
        #
        #     if episode_count % 50 == 0 and episode_count>1 :
        #
        #         no_lose_as_black = 0
        #         no_lose_as_white = 0
        #         players = [baseline_agent, agent]
        #         for _ in range(10):
        #             reward = env.play(players, random_move=True)
        #             if reward != 1:
        #                 no_lose_as_black +=1
        #
        #         players = [agent, baseline_agent]
        #         for _ in range(10):
        #             reward = env.play(players, random_move=True)
        #             if reward != -1:
        #                 no_lose_as_white += 1
        #
        #         print("against baseline,  no_lose_as_black : " + str(no_lose_as_black)
        #               + " no_lose_as_white : " + str(no_lose_as_white))
        #
        #         if no_lose_as_white == 10 and no_lose_as_black == 10:
        #             break
        #     else:
        #         reward = agent.train(.2)
        #         game_result[reward] += 1
        #         print("game result : " + str(game_result))
        #
        #     print("episode_count : " + str(episode_count))
        #     sess.run(agent.increment_episode_count)

        # train finished, record weight
        # with open('p_weight.json', 'w', encoding='utf-8') as f:
        #     trainable_variables = model.trainable_variables.eval()
        #     # print("trainable variable : " + str(trainable_variables))
        #
        #     weight_list = []
        #     for tav in trainable_variables:
        #         weight_list.append((tav[0]).item())
        #
        #     result_list = [game_result[-1], game_result[0], game_result[1]]
        #
        #     dic = {"weight" : weight_list, "game_result" : result_list}
        #     json.dump(dic, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
