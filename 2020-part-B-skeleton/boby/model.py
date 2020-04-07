import tensorflow as tf


class Model:
    """
    a 1-hidden layer neural network Model to be used as our TD-learning value function
    reference : https://adamklecz.wordpress.com/2017/10/30/tic-tac-tensorflow/
    """
    def __init__(self, input_dim, hidden_dim):

        with tf.variable_scope('model'):
            self.feature_vector_ = tf.placeholder(tf.float32,
                                                  shape=[None, input_dim],
                                                  name='feature_vector_')
            with tf.variable_scope('layer_1'):
                self.W_1 = tf.get_variable('W_1',
                                      shape=[input_dim, hidden_dim],
                                      initializer=tf.contrib.layers.xavier_initializer())
                hidden_1 = tf.nn.relu(tf.matmul(self.feature_vector_, self.W_1), name='hidden_1')

            with tf.variable_scope('layer_2'):
                self.W_2 = tf.get_variable('W_2', shape=[hidden_dim, 1],
                                      initializer=tf.contrib.layers.xavier_initializer())
                self.value = tf.tanh(tf.matmul(hidden_1, self.W_2), name='value')

            self.trainable_variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                                         scope=tf.get_variable_scope().name)