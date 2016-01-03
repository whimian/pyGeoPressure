from __future__ import division
from scipy import interpolate
import numpy as np


def interp_DW(array2d):
    """2-D distance-weighted interpolation

    Parameters
    ----------
    array2d : ndarray
        2-D ndarray void values being singaled by np.nan

    Examples
    --------
    >>> a = np.array([[2, 2, 2], [2, np.nan, 2], [2, 2, 2]])
    >>> b = interp_DW(a)
    """
    m = array2d.shape[0]
    n = array2d.shape[1]
    for i in range(m):
        for j in range(n):
            if np.isnan(array2d[i][j]):
                i_min = np.nan
                i_max = np.nan
                j_min = np.nan
                j_max = np.nan
                for p in xrange(i, -1, -1):
                    if not np.isnan(array2d[p][j]):
                        i_min = p
                        break
                for p in xrange(i, m, 1):
                    if not np.isnan(array2d[p][j]):
                        i_max = p
                        break
                for p in xrange(j, -1, -1):
                    if not np.isnan(array2d[i][p]):
                        j_min = p
                        break
                for p in xrange(j, n, 1):
                    if not np.isnan(array2d[i][p]):
                        j_max = p
                        break
                if np.isnan(i_min):
                    i_min = 0
                if np.isnan(i_max):
                    i_max = m - 1
                if np.isnan(j_min):
                    j_min = 0
                if np.isnan(j_max):
                    j_max = n - 1
                dis = list()
                value = list()
                for p in xrange(i_min, i_max + 1, 1):
                    for q in xrange(j_min, j_max + 1, 1):
                        if not np.isnan(array2d[p][q]):
                            dis.append(
                                1.0 / (np.abs(p - i)**2 + np.abs(q - j)**2))
                            value.append(array2d[p][q])
                interp = 0
                for r in xrange(len(dis)):
                    interp = interp + dis[r] * value[r]
                try:
                    interp = interp / np.sum(dis)
                except Exception, e:
                    print e
                    break
                array2d[i][j] = float("%.2f" % interp)


def spline_1d(twt, vel, step, startTwt=None, endTwt=None, method='cubic'):
    startTwt = twt[0] if startTwt is None else startTwt
    endTwt = twt[-1] if endTwt is None else endTwt

    newTwt = np.arange(startTwt, endTwt, step)
    f = interpolate.interp1d(twt, vel, kind=method)
    newVel = f(newTwt)

    return (list(newTwt), list(newVel))
