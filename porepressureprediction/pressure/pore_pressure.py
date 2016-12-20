"""routines to assist velocity data processing.
"""
from __future__ import division
import numpy as np


def bowers(v, obp, a=275, b=0.6, v0=1524):
    """
    Compute pressure using Bowers equation.

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    v0 : float, optional
        the velocity of unconsolidated regolith whose unit is m/s.
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b

    Notes
    -----
    .. math:: P = OBP - [\\frac{(V-V_{0})}{a}]^{\\frac{1}{b}}
    """
    # ves = ((v - v0) / a)**(1.0 / b)
    # pressure = obp - ves
    # return pressure
    return obp - ((v - v0) / a)**(1.0 / b)


def virgin_curve(effective_stress, a, b):
    "Virgin curve in Bowers' method."
    v0 = 1524
    return v0 + a * effective_stress**b


def eaton(v, vn, vesn, obp, a=0.785213, b=1.49683):
    """
    Compute pore pressure using Eaton equation.

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    vn : 1-d ndarray
        normal velocity array whose unit is m/s.
    vesn : 1-d ndarray
        vertical effective stress under normal compaction array
        whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    v0 : float, optional
        the velocity of unconsolidated regolith whose unit is ft/s.
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b

    Notes
    -----
    .. math:: P = OBP - VES_{n}* a (\\frac{V}{V_{n}})^{b}
    """
    ves = vesn * a * (v / vn)**b
    pressure = obp - ves
    return pressure


def fillipino():
    pass
