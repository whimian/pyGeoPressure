import numpy as np


def normal(depth, a, b):
    """
    Extrapolate velocity using normal trend.

    Parameters
    ----------
    depth : 1-d ndarray
        depth to convert
    a, b : scalar
        coefficents

    Returns
    -------
    out : 1-d ndarray
        esitmated velocity

    Notes
    -----
    .. math:: \log d{t}_{Normal}=a-bz

    the exponential relation is unphysical especially in depth bellow the
    interval within which the equation is calibrated.

    [1]C. Hottmann, R. Johnson, and others, “Estimation of formation pressures
       from log-derived shale properties,” Journal of Petroleum Technology,
       vol. 17, no. 6, pp. 717–722, 1965.

    """
    return np.exp(z*b - a)


def slotnick(depth, k, v0=1500):
    """
    Notes
    -----
    typical values of velocity gradient k falls in the range 0.6-1.0s-1

    [1]M. Slotnick, “On seismic computations, with applications, I,”
        Geophysics, vol. 1, no. 1, pp. 9–22, 1936.
    """
    return v0 + k*depth
