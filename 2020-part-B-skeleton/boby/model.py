import tensorflow as tf
import numpy as np


class Model:
    """
    a model for the eval function
    inspired by reference : https://adamklecz.wordpress.com/2017/10/30/tic-tac-tensorflow/
    """

    def __init__(self, input_dim):
        self.feature_vector_ = tf.placeholder(tf.float32,
                                              shape=[1, input_dim],
                                              name='feature_vector_')

        self.trainable_variables = tf.Variable(tf.ones([input_dim, 1]), dtype=tf.float32)

        self.value = tf.tanh(tf.matmul(self.feature_vector_, self.trainable_variables), name='value')
        # self.value = tf.tanh(, name='value')

        # self.W = np.ones([input_dim, 1], dtype=float)
        #
        # with tf.variable_scope('model'):
        #     self.feature_vector_ = tf.placeholder(tf.float32,
        #                                           shape=[None, input_dim],
        #                                           name='feature_vector_')
        #     with tf.variable_scope('layer_1'):
        #
        #
        #
        #     self.trainable_variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
        #                                                  scope=tf.get_variable_scope().name)
