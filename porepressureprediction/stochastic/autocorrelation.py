'''
    different kind of autocorrelation functions
'''
import numpy as np


def autocorrelation_fuction(x, z, a, b, r):
    return np.exp(-(x**2/a**2+z**2/b**2)**(1.0/(r+1)))


def exponential(x, z, a, b):
    return np.exp(-(x**2/a**2+z**2/b**2)**(1./2.))


def gaussian(x, z, a, b):
    return np.exp(-(x**2/a**2+z**2/b**2))


def spherical():
    pass


def stable():
    pass


class autocorrelation_func:
    def __init__(self, lc_a, lc_b):
        self.a = lc_a
        self.b = lc_b

    def exponential(self, x, z):
        return np.exp(-(x**2/self.a**2+z**2/self.b**2)**(1./2.))

    def gaussian(self, x, z):
        return np.exp(-(x**2/self.a**2+z**2/self.b**2))

    def spherical(self, x):
        v = 0
        if x <= self.a:
            v = 1 - 1.5 * x / self.a + 0.5 * x**3 / self.a**3
        return v

    def stable(self, x, z, r):
        return np.exp(-(x**r/self.a**r+z**r/self.b**r)**(1./r))


if __name__ == '__main__':
    pass
