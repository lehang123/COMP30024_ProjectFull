import numpy as np
import tensorflow as tf

from utils import make_nodes


class TdLeafAgent:

    def __init__(self, model, env, vectorize_method):
        """

        :param model: the train model
        :param env: the environment
        :param vectorize_method: the vectorize method for the features
        """
        self.model = model
        self.sess = None
        self.env = env

        # episode_count to used for training
        self.episode_count = tf.train.get_or_create_global_step()
        self.increment_episode_count = tf.assign_add(self.episode_count, 1)

        for tvar in self.model.trainable_variables:
            tf.summary.histogram(tvar.op.name, tvar)

        # create random agent variable record the play against this agent
        # this is an baseline test, our game agent should always win the random agent
        with tf.name_scope('random_agent_test_results'):
            self.white_wins = tf.Variable(0, name="white_wins", trainable=False)
            self.white_wins_ = tf.placeholder(tf.int32, name='white_wins_')
            self.black_wins = tf.Variable(0, name="black_wins", trainable=False)
            self.black_wins_ = tf.placeholder(tf.int32, name='black_wins_')

            self.white_losses = tf.Variable(0, name="white_losses", trainable=False)
            self.white_losses_ = tf.placeholder(tf.int32, name='white_losses_')
            self.black_losses = tf.Variable(0, name="black_losses", trainable=False)
            self.black_losses_ = tf.placeholder(tf.int32, name='black_losses_')

            self.white_draws = tf.Variable(0, name="white_draws", trainable=False)
            self.white_draws_ = tf.placeholder(tf.int32, name='white_draws_')
            self.black_draws = tf.Variable(0, name="black_draws", trainable=False)
            self.black_draws_ = tf.placeholder(tf.int32, name='black_draws_')

            self.white_update_wins = tf.assign(self.white_wins, self.white_wins_)
            self.white_update_draws = tf.assign(self.white_draws, self.white_draws_)
            self.white_update_losses = tf.assign(self.white_losses, self.white_losses_)
            self.black_update_wins = tf.assign(self.black_wins, self.black_wins_)
            self.black_update_draws = tf.assign(self.black_draws, self.black_draws_)
            self.black_update_losses = tf.assign(self.black_losses, self.black_losses_)

            self.update_random_agent_test_results = tf.group(*[self.white_update_wins,
                                                               self.white_update_draws,
                                                               self.white_update_losses,
                                                               self.black_update_wins,
                                                               self.black_update_draws,
                                                               self.black_update_losses])

            self.random_agent_test_s = [self.white_wins_, self.white_draws_, self.white_losses_,
                                        self.black_wins_, self.black_draws_, self.black_losses_,]

            tf.summary.scalar("player_white_wins", self.white_wins)
            tf.summary.scalar("player_white_draws", self.white_losses)
            tf.summary.scalar("player_white_losses", self.white_draws)
            tf.summary.scalar("player_black_wins", self.black_wins)
            tf.summary.scalar("player_black_draws", self.black_losses)
            tf.summary.scalar("player_black_losses", self.black_draws)


        self.vectorize_method = vectorize_method

        self.opt = tf.train.AdamOptimizer()

        # the gradients graph that the model trainable variables (W_1, W_2) to the final value
        self.grads = tf.gradients(self.model.value, self.model.trainable_variables)

        self.grads_s = [tf.placeholder(tf.float32, shape=tvar.get_shape()) for tvar in self.model.trainable_variables]

        self.apply_grads = self.opt.apply_gradients(zip(self.grads_s, self.model.trainable_variables),
                                                    name='apply_grads', global_step=tf.train.get_global_step())

    def train(self, epsilon):
        """
        in self training, if the same agent playing against each other, both of them will do that exact same
        move, therefore, we need some epsilon value to let the agent choose to do some random move so it can learnt
        more different situation

        :param epsilon: rand lower than epsilon, do random move
        :return: None
        """

        lamda = 0.7

        self.env.reset()

        # make traces for the two weights from model (W_1, W_2)
        traces = [np.zeros(tvar.shape)
                  for tvar in self.model.trainable_variables]

        feature_vector = self.vectorize_method(self.env.get_board(), self.env.board.turn)

        previous_leaf_value, previous_grads = self.sess.run([self.model.value, self.grads],
                                                            feed_dict={self.model.feature_vector_: feature_vector})
        reward = self.env.get_reward()

        # training begin, playing with itself
        while reward is None:

            move, leaf_value, leaf_node = self.get_move(return_value=True)

            # to prevent both agent doing the same move during training, we used some random move
            if np.random.rand() < epsilon:
                self.env.make_random_move()
            else:
                self.env.make_move(move)

            reward = self.env.get_reward()

            feature_vector = self.vectorize_method(leaf_node, self.env.get_turn())

            grads = self.sess.run(self.grads,
                                  feed_dict={self.model.feature_vector_: feature_vector})

            delta = leaf_value - previous_leaf_value
            for previous_grad, trace in zip(previous_grads, traces):
                trace *= lamda
                trace += previous_grad

            # update weight
            self.sess.run(self.apply_grads,
                          feed_dict={grad_: -delta * trace
                                     for grad_, trace in zip(self.grads_s, traces)})

            previous_grads = grads
            previous_leaf_value = leaf_value

        return self.env.get_reward()

    def minimax_alphabeta(self, node, depth, α, β, maximizing):
        """
        minimax_alphabeta cut off search, used to eval all possible child nodes of the current state and get back the value,
        then we choose the node that has the highest value

        :param node: the node that we are evaluating
        :param depth: the cut-off depth
        :param α: alpha (in minimizing, the value used to cut-off loop if we find a value smaller than alpha)
        :param β: beta (in maximizing, the value used to cut-off loop if we find a value greater than beta)
        :param maximizing: is it maximizing now
        :param player: colour of the player
        :param opponent: colour of the opponent
        :return: the ultimate value of the node, and the leaf node for the value
        """

        if self.env.get_reward() is not None:
            value = self.env.get_reward()
            return np.array([[value]]), node
        elif depth == 0:
            return self.eval_fun(node), node # the eval value of node

        if maximizing:
            value = float('-Infinity')
            children = make_nodes(node, self.env.get_turn())
            # todo : if we have optimal ordering, we can pruned more. (but how to order)
            for child in children:
                (child_value, child_node) = self.minimax_alphabeta(child, depth - 1, α, β, False)
                value, node = (value, node) if value>=child_value else (child_value, child_node)
                # value = max(value, self.minimax_alphabeta(child, depth - 1, α, β, False))
                α = max(α, value)
                if α >= β:
                    break  # (*β cut - off *)

        else:
            value = float('Infinity')
            oppo_turn = 'white' if self.env.get_turn() == 'black' else 'black'
            children = make_nodes(node, oppo_turn)
            for child in children:
                (child_value, child_node) = self.minimax_alphabeta(child, depth - 1, α, β, True)
                value, node = (value, node) if value<=child_value else (child_value, child_node)
                # value = min(value, self.minimax_alphabeta(child, depth - 1, α, β, True))
                β = min(β, value)
                if α >= β:
                    break  # (*α cut - off *)

        return value, node

    def get_move(self, return_value=False):
        # legal_moves = make_nodes(self.env.get_board(), self.env.get_turn())
        legal_moves = self.env.get_legal_moves()

        is_white_turn = self.env.get_turn() == 'white'

        best_v = float('-Infinity') if is_white_turn else float('Infinity')
        best_leaf_node = None
        best_m = None

        for move in legal_moves:
            v, n = self.minimax_alphabeta(move, 1, float('-Infinity'), float('Infinity'), is_white_turn)
            compare = v >= best_v if is_white_turn else v <= best_v
            best_v, best_m, best_leaf_node = (v, move, n) if compare else (best_v, best_m, best_leaf_node)

        if return_value:
            return  best_m, best_v, best_leaf_node
        else:
            return best_m


    def eval_fun(self, node):
        """
        the evaluate function for the current node

        :param node: the current node
        :return: the value
        """
        fv = self.vectorize_method(node, self.env.get_turn())
        value = self.sess.run(self.model.value, feed_dict={self.model.feature_vector_: fv})
        return value

# model = Model(28, 100)
# traces = [np.zeros(tvar.shape)
#                   for tvar in model.trainable_variables]
# for t in traces:
#     print(t.shape)
# print(len(traces))