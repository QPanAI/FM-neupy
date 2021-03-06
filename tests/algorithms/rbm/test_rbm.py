import pickle

import numpy as np

from neupy import algorithms
from neupy.utils import asfloat

from base import BaseTestCase


class BernoulliRBMTestCase(BaseTestCase):
    def setUp(self):
        super(BernoulliRBMTestCase, self).setUp()
        self.data = np.array([
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            [1, 0, 0, 0],  # incomplete sample
            [1, 0, 1, 0],

            [0, 1, 0, 1],
            [0, 0, 0, 1],  # incomplete sample
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
        ])
        self.data = asfloat(self.data)

    def test_rbm_score(self):
        rbm = algorithms.RBM(
            n_visible=4,
            n_hidden=1,
            step=0.5,
            batch_size=10
        )
        rbm.train(self.data, epochs=500)

        rbm_error_for_known = rbm.score(np.array([[0, 1, 0, 1]]))
        rbm_error_for_unknown = rbm.score(np.array([[0, 1, 0, 0]]))

        self.assertLess(rbm_error_for_unknown, rbm_error_for_known)

    def test_simple_bernoulli_rbm(self):
        data = self.data

        rbm = algorithms.RBM(n_visible=4, n_hidden=1)
        rbm.train(data, epochs=100)

        output = rbm.visible_to_hidden(data)
        np.testing.assert_array_equal(
            output.round(),
            np.array([[0, 0, 0, 0, 1, 1, 1, 1, 1, 1]]).T
        )

        typical_class1_sample = output[0]
        incomplete_class1_sample = output[2]
        # Check that probability of a typical case is
        # closer to 0 (because 0 is a class defined by RBM)
        # than for the incomplete case.
        self.assertLess(typical_class1_sample, incomplete_class1_sample)

        typical_class2_sample = output[4]
        incomplete_class2_sample = output[5]
        # Same as before but for class 1.
        self.assertGreater(typical_class2_sample, incomplete_class2_sample)

    def test_rbm_storage(self):
        data = self.data
        network = algorithms.RBM(
            n_visible=4,
            n_hidden=1,
            step=0.1,
            batch_size=10,
        )
        network.train(data, epochs=500)

        stored_network = pickle.dumps(network)
        loaded_network = pickle.loads(stored_network)

        network_hidden = network.visible_to_hidden(data)
        loaded_network_hidden = loaded_network.visible_to_hidden(data)

        np.testing.assert_array_almost_equal(
            loaded_network_hidden, network_hidden)

        network_visible = network.hidden_to_visible(network_hidden)
        loaded_network_visible = loaded_network.hidden_to_visible(
            loaded_network_hidden)

        np.testing.assert_array_almost_equal(
            loaded_network_visible, network_visible)

    def test_rbm_batch_size(self):
        data = self.data
        batch_size = 7

        self.assertNotEqual(len(data) % batch_size, 0)

        rbm = algorithms.RBM(
            n_visible=4, n_hidden=1, step=0.1,
            batch_size=batch_size
        )
        # Check if it's possilbe to train RBM in case if
        # we cannot divide dataset into full mini-batches
        rbm.train(data, epochs=2)

    def test_rbm_sampling(self):
        data = self.data

        rbm = algorithms.RBM(n_visible=4, n_hidden=1)
        rbm.train(data, epochs=500)

        proba_sample = rbm.hidden_to_visible(
            rbm.visible_to_hidden(data)
        )
        proba_sample = proba_sample.round().astype(int)

        np.testing.assert_array_equal(
            proba_sample.round(),
            np.array([
                [1, 0, 1, 0],
                [1, 0, 1, 0],
                [1, 0, 1, 0],  # fixed sample
                [1, 0, 1, 0],

                [0, 1, 0, 1],
                [0, 1, 0, 1],  # fixed sample
                [0, 1, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
            ])
        )

        sampled_data = rbm.gibbs_sampling(data, n_iter=1)
        self.assertNotEqual(0, np.abs(sampled_data - self.data).sum())

    def test_rbm_predict(self):
        rbm = algorithms.RBM(n_visible=4, n_hidden=1)
        hidden_state = rbm.visible_to_hidden(self.data)
        prediction = rbm.predict(self.data)
        np.testing.assert_array_almost_equal(hidden_state, prediction)
