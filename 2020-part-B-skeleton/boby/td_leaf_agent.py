import time

import numpy as np
import tensorflow as tf

from book_of_moves import is_terrible_move
from utils import make_nodes


class TdLeafAgent:

    def __init__(self, model, env, sess, vectorize_method, minimax_depth=2):
        """

        :param model: the train model
        :param env: the environment
        :param vectorize_method: the vectorize method for the features
        :param minimax_depth: depth of the minmax search
        """
        self.model = model
        self.sess = sess
        self.env = env
        self.minimax_depth = minimax_depth

        # episode_count to used for training
        self.episode_count = tf.train.get_or_create_global_step()
        self.increment_episode_count = tf.assign_add(self.episode_count, 1)

        # create random agent variable record the play against this agent
        # this is an baseline test, our game agent should always win the random agent

        self.vectorize_method = vectorize_method

        # init all the variable
        self.sess.run(tf.global_variables_initializer())

        # the gradients graph that the model trainable variables (W_1) to the final value
        self.grads = tf.gradients(self.model.value, self.model.trainable_variables)
        print("grad : " + str(self.grads))

        print("trainable variable : " + str(self.model.trainable_variables.eval()))

    def train(self, epsilon, learning_rate=0.1, against=None):
        """
        in self training, if the same agent playing against each other, both of them will do that exact same
        move, therefore, we need some epsilon value to let the agent choose to do some random move so it can learnt
        more different situation

        :param epsilon: rand lower than epsilon, do random move
        :param learning_rate: the learning rate
        :param agent that train against
        :return: None
        """

        reward_sequence = []

        lamda = 0.7

        self.env.reset()

        feature_vector = self.vectorize_method(self.env.get_board(), self.env.get_turn())

        eval_value, grads = self.sess.run([self.model.value, self.grads],
                                                            feed_dict={self.model.feature_vector_: feature_vector})

        reward_sequence.append((eval_value[0, 0], grads))

        # training begin, playing with itself
        while True:

            if against is not None:
                move = against.get_move()
                self.env.make_move(move)

            move, eval_value = self.get_move(return_value=True)

            # to prevent both agent doing the same move during training, we used some random move
            if np.random.rand() < epsilon:
                move = self.env.make_random_move(include_boom=False)
                feature_vector = self.vectorize_method(move, self.env.get_turn())
                # try the eval_function for the random move
                eval_value = self.sess.run(self.model.value,
                                            feed_dict={self.model.feature_vector_: feature_vector})
            else:
                self.env.make_move(move)
                feature_vector = self.vectorize_method(move, self.env.get_turn())

            reward = self.env.get_reward()
            if reward is not None:
                break

            grads = self.sess.run(self.grads,
                                  feed_dict={self.model.feature_vector_: feature_vector})

            reward_sequence.append((eval_value, grads))

        # after getting reward_sequence, start updating weight

        weight_change_rate = self.sum_grads(learning_rate, lamda, reward_sequence, reward)
        print("rate change rate : " + str(weight_change_rate))
        f = tf.add(self.model.trainable_variables, weight_change_rate)
        update = self.model.trainable_variables.assign(f)
        self.sess.run(update)
        print("trainable variable updated : " + str(self.model.trainable_variables.eval()))

        return reward

    def minimax_alphabeta(self, node, depth, α, β, maximizing, turn_to, with_move=False):
        """
        minimax_alphabeta cut off search, used to eval all possible child nodes of the current state and get back the value,
        then we choose the node that has the highest value

        :param node: the node that we are evaluating
        :param depth: the cut-off depth
        :param α: alpha (in minimizing, the value used to cut-off loop if we find a value smaller than alpha)
        :param β: beta (in maximizing, the value used to cut-off loop if we find a value greater than beta)
        :param maximizing: is it maximizing now
        :param turn_to: who's turn to move
        :param with_move: does return move as well?
        :return: the ultimate value of the node, and the leaf node for the value
        """

        if self.env.get_reward() is not None:
            value = self.env.get_reward()

            # print("final v : " + str(value))
            if with_move:
                return value, node
            else:
                return value
        elif depth == 0:
            value = self.eval_fun(node, turn_to)

            if with_move:
                return value[0, 0], node
            else:
                return value[0, 0] # the eval value of node

        move = node

        children = make_nodes(node, turn_to)
        children = self.filter(node, children, turn_to)
        next_turn = 'white' if turn_to == 'black' else 'black'
        if maximizing:
            value = -1.0
            # children = make_nodes(node, self.env.get_turn())
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, False, next_turn)
                if new_value>=value:
                    value = new_value
                    move = child
                # value = max(value, self.minimax_alphabeta(child, depth - 1, α, β, False))
                # show_move = nodes_to_move(node, child, 'white')
                # print("maxing with value : " + str(new_value) + " with move : "  + str(show_move))
                α = max(α, value)
                if α >= β:
                    break  # (*β cut - off *)

        else:
            value = 1.0
            # children = make_nodes(node, self.env.get_turn())
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, True, next_turn)
                if new_value<=value:
                    value = new_value
                    move = child
                # value = min(value, self.minimax_alphabeta(child, depth - 1, α, β, True))
                # show_move = nodes_to_move(node, child, 'black')
                # print("maxing with value : " + str(new_value) + "with move : " + str(show_move))
                β = min(β, value)
                if α >= β:
                    break  # (*α cut - off *)

        if with_move:
            return value, move
        else:
            return value

    def get_move(self, return_value=False):
        start = time.time()

        is_white_turn = self.env.get_turn() == 'white'

        value, move = self.minimax_alphabeta(self.env.get_board(), self.minimax_depth, -1, 1,
                                             is_white_turn, self.env.get_turn(), with_move=True)

        end = time.time()
        print("time taken  :" + str(end - start))
        if return_value:
            return  move, value
        else:
            return move

    def eval_fun(self, node, turn):
        """
        the evaluate function for the current node

        :param node: the current node
        :param turn: who's turn to move
        :return: the value
        """
        fv = self.vectorize_method(node, turn)
        value = self.sess.run(self.model.value, feed_dict={self.model.feature_vector_: fv})
        return value

    def load_weight(self, weight):
        weight = np.array(weight)
        weight = weight.reshape([weight.shape[0], 1])
        assign_weight = self.model.trainable_variables.assign(weight)
        self.sess.run(assign_weight)
        print("trainable variable loaded : " + str(self.model.trainable_variables.eval()))

    def sum_grads(self, learning_rate, lamda, seq, final_reward):
        """
        calculate gradients to update the weight for TD leaf

        W := W + sum_of_grads

        :param learning_rate: the learning rate
        :param lamda: the lambda
        :param seq: the observation sequence of the the game
        :param final_reward:  the final reward
        :return:
        """
        ans = np.zeros(len(self.grads), dtype=float)
        end = len(seq)

        def sum_eval_diff(start):
            result = 0
            for i in range(start, end+1):
                result += (lamda ** (i - start)) * temp_diff

            return result

        for t in range(1, end+1):
            print("show seq: " + str(seq[t-1]))
            eval_t, grad = seq[t-1]
            if t == end:
                eval_t1 = final_reward
            else:
                eval_t1, _ = seq[t]

            temp_diff = eval_t1 - eval_t

            std = sum_eval_diff(t)
            print("how is std : " + str(std))
            w = np.array(grad[0], dtype=float) * std
            ans = np.add(ans, w)

        ans = ans
        return learning_rate * ans

    def filter(self, current_board, available_moves, turn):
        """
        to filter and sorted moves in order the improve our speed of
            alpha beta pruning(hopefully)

        :param current_board: the current board which we use to evaluate the current situation
        :param available_moves: the move that we have so we can filter or sort in order the improve our speed of
            alpha beta pruning
        :param turn: who's turn is it
        :return: the filtered moves
        """

        # filter_list(available_moves, (lambda x : not is_terrible_move(current_board, x, turn)), [])
        # before = len(available_moves)
        available_moves = [x for x in available_moves if not is_terrible_move(current_board, x, turn)]
        # after = len(available_moves)

        # print(before-after)

        def sort_eval(eval_move):
            return self.eval_fun(eval_move, turn)

        # todo: make all boom action to the head of the moves as these are the most direct result to the score,
        # todo:  so they most likely to filter others by alpha beta (does the sort function help us with this already)

        """
        sort moves by current evaluate function, if we have good ordering, we can prune more for the alpha beta,
        since the difference from state the state is keeping to minial due to the TD lambda nature, I hope this is
        a good enough approximation

        note : sort does help in improving the alpha beta search, however, the sorting taking extra time, and
         it's not a perfect eval_fun, so in total, it's not a very good improvement, I suspect that if we can improve
         more for our eval_fun, this could get better as well.
        """

        # is_maximizing = turn == 'white'
        # sorted_moves = sorted(available_moves, key=sort_eval, reverse=is_maximizing)

        # """
        #     we try to throw away some percentage of the move after the sort,
        #     in order to look deeper, HAVE TO TURN THIS OFF WHILE TRAINING
        # """
        # curr_num = len(sorted_moves)
        # keep_num = int(curr_num*0.3)
        # sorted_moves = sorted_moves[0:keep_num]


        return available_moves