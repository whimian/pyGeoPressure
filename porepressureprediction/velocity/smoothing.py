# -*- coding: utf-8 -*-
"""
2-d smoothing
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
from scipy import ndimage


def smooth(x, window_len=11, window='hanning'):
    """
    Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    Parameters
    ----------
    x : ndarray
        the input signal
    window_len : scalar
        the dimension of the smoothing window; should be an odd integer.
    window : scalar
        the type of window from 'flat', 'hanning', 'hamming', 'bartlett',
        'blackman' flat window will produce a moving average smoothing.

    Returns
    -------
    y : ndarray
        the smoothed signal

    Examples
    --------
    >>> t=linspace(-2,2,0.1)
    >>> x=sin(t)+randn(len(t))*0.1
    >>> y=smooth(x)

    See Also
    --------
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman,
    numpy.convolve scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array
          instead of a string

    Notes
    -----
    length(output) != length(input), to correct this: return
    y[(window_len/2-1):-(window_len/2)] instead of just y.

    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming',\
                         'bartlett', 'blackman'")

    s = np.r_[x[window_len-1:0:-1], x, x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = np.convolve(w/w.sum(), s, mode='valid')
    # return y

    # return y[(window_len/2 - 1): -(window_len/2 + 1)]
    return y[(window_len/2-1): -(window_len/2)]


def smooth_2d(m):
    smoothed = ndimage.filters.gaussian_filter(m, 1)
    # m, n = smoothed.shape
    # for i in xrange(m):
    #     for j in xrange(n):
    #         smoothed[i][j] = float("%.2f" % smoothed[i][j])
    smoothed = np.round(smoothed, 2)

    return smoothed

if __name__ == "__main__":
    pass
