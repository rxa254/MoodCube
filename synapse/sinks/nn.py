import numpy as np
import random
import tensorflow as tf


class MoodyNN(object):
    def __init__(self, shape):
        """
        `shape` is the shape of the network: (Ninputs, Noutputs) 
        """
        self.shape = shape

        tf.reset_default_graph()
    
        # These lines establish the feed-forward part of the network
        # used to choose actions
        self.inputs1 = tf.placeholder(shape=[1, self.shape[0]], dtype=tf.float32)
        self.W = tf.Variable(tf.random_uniform(self.shape, 0, 0.01))
        self.Qout = tf.matmul(inputs1, W)
        # prediction/action is the maximum of the Q (output/action)
        # matrix (vector of length shape[1])
        self.predict = tf.argmax(Qout, 1)
    
        # Below we obtain the loss by taking the sum of squares
        # difference between the target and prediction Q values.
        self.nextQ = tf.placeholder(shape=[1, self.shape[1]], dtype=tf.float32)
        loss = tf.reduce_sum(tf.square(nextQ - Qout))
        trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
        self.updateModel = trainer.minimize(loss)
    
        init = tf.initialize_all_variables()

        # Set learning parameters
        self.y = .99
        self.e = 0.1

        self.session = tf.Session()
        self.session.run(init)

    def reward(self, sample):
        return

    def update(self, sample):
        # FIXME: 's' and 's1' are the current and next observation

        d = False
        j = 0
        # The Q-Network
        while j < 99:
            j += 1

            # Choose an action by greedily (with e chance of random action) from the Q-network
            a, allQ = self.session.run(
                [self.predict, self.Qout],
                feed_dict={self.inputs1: np.identity(self.shape[0])[s:s+1]})

            if np.random.rand(1) < self.e:
                a[0] = env.action_space.sample()

            # Get new state and reward from environment
            # s1, r, d, _ = env.step(a[0])
            reward = self.reward(sample)

            # Obtain the Q' values by feeding the new state
            # through our network
            Q1 = self.session.run(
                self.Qout,
                feed_dict={self.inputs1: np.identity(self.shape[0])[s1:s1+1]})

            # Obtain maxQ' and set our target value for chosen action.
            maxQ1 = np.max(Q1)
            targetQ = allQ
            targetQ[0, a[0]] = reward + self.y*maxQ1

            # Train our network using target and predicted Q
            # values
            _, W1 = self.session.run(
                [self.updateModel, self.W],
                feed_dict={self.inputs1: np.identity(self.shape[0])[s:s+1],
                           self.nextQ: targetQ})

            # FIXME: reduce the chance of random action if this
            # session is done.  but what does that mean?  reward is
            # less than some threshold?  out of bounds?
            if d == True:
                # Reduce chance of random action as we train the model.
                self.e = 1./((i/50) + 10)
                break
