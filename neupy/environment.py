import os
import random

import theano
import tensorflow as tf
import numpy as np


__all__ = ('sandbox', 'reproducible', 'speedup')


def sandbox():
    """
    Sandbox mode set up Theano configurations in the way that
    make compilation faster.
    """
    theano.config.optimizer = 'fast_compile'
    theano.config.allow_gc = False


def reproducible(seed=0):
    """
    Set up the same seed value for the NumPy and
    python random module to make your code reproducible.

    Parameters
    ----------
    seed : int
        Defaults to ``0``.
    """
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    random.seed(seed)
    tf.set_random_seed(seed)


def speedup():
    """
    Speed up Theano's computation.
    """
    theano.config.floatX = 'float32'
    theano.config.allow_gc = False
