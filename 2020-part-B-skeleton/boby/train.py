import tensorflow as tf

from boby.model import Model
from boby.random_agent import RandomAgent
from boby.td_leaf_agent import TdLeafAgent
from boby.vectorize import pieces_positions_vectorize, characteristic_vectorize
from environment import Environment


def main():
    env = Environment()
    model = Model(5)

    log_dir = "./log/td_leaf"

    with tf.Session() as sess :
        agent = TdLeafAgent(model, env, sess, characteristic_vectorize)
        # agent.sess = sess
        random_agent = RandomAgent(env)


        episode_count = sess.run(agent.episode_count)
        agent.train(.2)
        sess.run(agent.increment_episode_count)

        # while True:
        #     episode_count = sess.run(agent.episode_count)
        #     # agent.train(.2)
        #     if episode_count % 50 == 0:
        #         print("doing this")
        #         results = random_agent.test(agent)
        #         print("finished this")
        #         print(episode_count, ':', results)
        #
        #         if results[2] + results[5] + results[1] + results[4] == 0:
        #             print("successfully beat random agent baseline")
        #             break
        #     else:
        #         print("start doing this")
        #         agent.train(.2)
        #     sess.run(agent.increment_episode_count)



    # scaffold = tf.train.Scaffold(summary_op=summary_op)
    #
    # with tf.train.MonitoredTrainingSession(checkpoint_dir=log_dir,
    #                                        scaffold=scaffold) as sess:
    #
    #     agent.sess = sess
    #     random_agent = RandomAgent(env)
    #
    #     while True:
    #         episode_count = sess.run(agent.episode_count)
    #         if episode_count % 50 == 0:
    #             print("doing this")
    #             results = random_agent.test(agent)
    #             print("finished this")
    #
    #             sess.run(agent.update_random_agent_test_results,
    #                      feed_dict={random_agent_test_: result
    #                                 for random_agent_test_, result in zip(agent.random_agent_test_s, results)})
    #             print(episode_count, ':', results)
    #
    #             if results[2] + results[5] + results[1] + results[4] == 0:
    #                 final_summary = sess.run(summary_op)
    #                 summary_writer.add_summary(final_summary, global_step=episode_count)
    #                 break
    #         else:
    #             print("start doing this")
    #             agent.train(.2)
    #         sess.run(agent.increment_episode_count)


if __name__ == "__main__":
    main()
