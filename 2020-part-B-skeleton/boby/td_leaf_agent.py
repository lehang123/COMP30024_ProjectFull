from boby.utils import make_nodes
import tensorflow as tf

class TdLeafAgent:

    def __init__(self, player, opponent, model, env, sess, verbose=False):
        self.player = player
        self.opponent = opponent
        self.model = model
        self.env = env
        self.sess = sess
        self.verbose = verbose

        self.opt = tf.train.AdamOptimizer()

        self.grads = tf.gradients(self.model.value, self.model.trainable_variables)

        self.grads_s = [tf.placeholder(tf.float32, shape=tvar.get_shape()) for tvar in self.model.trainable_variables]

        self.apply_grads = self.opt.apply_gradients(zip(self.grads_s, self.model.trainable_variables),
                                                    name='apply_grads')


        # episode_count to used for training
        self.episode_count = tf.train.get_or_create_global_step()
        self.increment_episode_count = tf.assign_add(self.episode_count, 1)

        for tvar in self.model.trainable_variables:
            tf.summary.histogram(tvar.op.name, tvar)

        # create random agent variable record the play against this agent
        # this is an baseline test, our game agent should always win the random agent
        with tf.name_scope('random_agent_test_results'):
            self.wins = tf.Variable(0, name="wins", trainable=False)
            self.wins_ = tf.placeholder(tf.int32, name='wins_')

            self.losses = tf.Variable(0, name="losses", trainable=False)
            self.losses_ = tf.placeholder(tf.int32, name='losses_')

            self.draws = tf.Variable(0, name="draws", trainable=False)
            self.draws_ = tf.placeholder(tf.int32, name='draws_')

            self.update_wins = tf.assign(self.wins, self.wins_)
            self.update_draws = tf.assign(self.draws, self.draws_)
            self.update_losses = tf.assign(self.losses, self.losses_)

            self.update_random_agent_test_results = tf.group(*[self.update_wins,
                                                               self.update_draws,
                                                               self.update_losses])

            self.random_agent_test_s = [self.wins_, self.draws_, self.losses_]

            tf.summary.scalar("player_wins", self.wins)
            tf.summary.scalar("player_draws", self.losses)
            tf.summary.scalar("player_losses", self.draws)

    def train(self, epsilon):
        """
        in self training, if the same agent playing against each other, both of them will do that exact same
        move, therefore, we need some epsilon value to let the agent choose to do some random move so it can learnt
        more different situation

        :param epsilon: rand lower than epsilon, do random move
        :return: None
        """

        lamda = 0.7



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
        :return: the ultimate value of the node
        """

        if depth == 0 or not node[self.opponent] or not node[self.player]:
            return self.eval_fun(node)  # the eval value of node

        if maximizing:
            value = float('-Infinity')
            children = make_nodes(node, self.player, self.opponent)
            # todo : if we have optimal ordering, we can pruned more. (but how to order)
            for child in children:
                value = max(value, self.minimax_alphabeta(child, depth - 1, α, β, False))
                α = max(α, value)
                if α >= β:
                    break  # (*β cut - off *)

        else:
            value = float('Infinity')
            children = make_nodes(node, self.player, self.opponent)
            for child in children:
                value = min(value, self.minimax_alphabeta(child, depth - 1, α, β, True))
                β = min(β, value)
                if α >= β:
                    break  # (*α cut - off *)

        return value

    def eval_fun(self, node):
        """
        the evaluate function for the current node

        :param node: the current node
        :return: the value
        """
        return 0