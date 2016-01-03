# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
import matplotlib


class Krig(object):

    def __init__(self, mesh, points, model='spherical', bw=500, info=None):
        self.model = model
        self.mesh = mesh
        self.points = points
        self.covfunc = None
        self.kriged_value = None
        self.kriged_variance = None

        self.bw = bw
        self.hs = None
        self.sv = None
        self.info = {"startInline": 2000,
                     "endInline": 3600,
                     "stepInline": 20,
                     "startCrline": 8000,
                     "endCrline": 9000,
                     "stepCrline": 40
                     }

    def __str__():
        pass

    def __repr__():
        pass

    def train(self):
        if self.hs is None:
            _max = pdist(self.points[:, :2]).max()  # / 2
            self.hs = np.arange(0, _max, self.bw)

        if self.covfunc is None:
            if self.model == 'spherical':
                vfunc_model = np.vectorize(self._spherical)
                self.covfunc = self._cvmodel(self.points, vfunc_model,
                                             self.hs, self.bw)
        self.sv = self._SV(self.points, self.hs, self.bw)

    def krig(self):
        # X0, X1 = self.points[:, 0].min(), self.points[:, 0].max()
        # Y0, Y1 = self.points[:, 1].min(), self.points[:, 1].max()

        n, m = self.mesh.shape
        # dx, dy = (X1 - X0) / n, (Y1 - Y0) / m
        dx = self.info["stepInline"]
        dy = self.info["stepCrline"]
        x0 = self.info["startInline"]
        y0 = self.info["startCrline"]

        self.kriged_value = np.zeros(self.mesh.shape)
        self.kriged_variance = np.zeros(self.mesh.shape)
        m, n = int(m), int(n)
        for i in xrange(m):
            percent = int(i / m * 100)
            print('[' + percent * '=' + (100 - percent) * ' ' + '] ' +
                  str(percent) + '%')
            for j in xrange(n):
                self.kriged_value[i, j], self.kriged_variance[i, j] = \
                    self._krige(
                            self.points, self.covfunc, self.hs, self.bw,
                            (x0 + dx * i, y0 + dy * j), 16)
        print('[' + 100 * '=' + '] ' + '100%' + '\nCompleted!')

    def semivariogram(self, savefig=False):
        fig2, ax2 = plt.subplots()
        ax2.plot(self.sv[0], self.sv[1], '.-')
        ax2.plot(self.sv[0], self.covfunc(self.sv[0]))
        ax2.set_title('Spherical Model')
        ax2.set_ylabel('Semivariance')
        ax2.set_xlabel('Lag [m]')
        if savefig is True:
            fig2.savefig('semivariogram_model.png', fmt='png', dpi=200)

    def plot(self, savefig=False):
        cdict = {'red':   ((0.0, 1.0, 1.0),
                           (0.5, 225 / 255., 225 / 255.),
                           (0.75, 0.141, 0.141),
                           (1.0, 0.0, 0.0)),
                 'green': ((0.0, 1.0, 1.0),
                           (0.5, 57 / 255., 57 / 255.),
                           (0.75, 0.0, 0.0),
                           (1.0, 0.0, 0.0)),
                 'blue':  ((0.0, 0.376, 0.376),
                           (0.5, 198 / 255., 198 / 255.),
                           (0.75, 1.0, 1.0),
                           (1.0, 0.0, 0.0))}
        my_cmap = matplotlib.colors.LinearSegmentedColormap(
            'my_colormap', cdict, 256)
        fig, ax = plt.subplots()
        H = np.zeros_like(self.kriged_value)
        for i in xrange(self.kriged_value.shape[0]):
            for j in xrange(self.kriged_value.shape[1]):
                H[i, j] = np.round(self.kriged_value[i, j] * 3)
        ax.matshow(H, cmap=my_cmap, interpolation='nearest')
        ax.scatter(self.points[:][0] / 200.0, self.points[:][1] / 200.0,
                   facecolor='none', linewidths=0.75, s=50)
        ax.set_xlim(0, 99)
        ax.set_ylim(0, 80)
        ax.set_xticks([25, 50, 75], [5000, 10000, 15000])
        ax.set_yticks([25, 50, 75], [5000, 10000, 15000])
        if savefig is True:
            fig.savefig('krigingpurple.png', fmt='png', dpi=200)

        # figx, axx = plt.subplots()
        # HV = np.zeros_like(V)
        # for i in range(V.shape[0]):
        #     for j in range(V.shape[1]):
        #         HV[i, j] = np.round(V[i, j] * 3)
        # axx.matshow(HV, cmap=my_cmap, interpolation='nearest')
        # axx.scatter(z.x/200.0, z.y/200.0,
        #             facecolor='none', linewidths=0.75, s=50)
        # axx.set_xlim(0, 99)
        # axx.set_ylim(0, 80)
        # axx.set_xticks([25, 50, 75], [5000, 10000, 15000])
        # axx.set_yticks([25, 50, 75], [5000, 10000, 15000])
        # if savefig is True:
        #     figx.savefig('krigingpurple2.png', fmt='png', dpi=200)

    def _spherical(self, h, a, c0):
        if h <= a:
            return c0 * (1.5 * h / a - 0.5 * (h / a)**3.0)
        else:
            return c0

    def _opt(self, fct, x, y, c0, parameterRange=None, meshSize=1000):
        '''
        Parameters
        ----------
        fct : callable
            functions to minimize
        x : ndarray
            input x array
        y : ndarray
            input y array
        c0 : scalar
            covariance

        Returns
        -------
        a : scalar
            the best fitting coefficient
        '''
        if parameterRange is None:
            parameterRange = [x[1], x[-1]]

        def residuals(pp, yy, xx):
            a = pp
            err = yy - fct(xx, a, c0)
            return err

        p0 = x[1]
        plsq = leastsq(residuals, p0, args=(y, x))
        return plsq[0][0]

    def _SVh(self, P, h, bw):
        '''
        Experimental semivariogram for a single lag
        '''
        pd = squareform(pdist(P[:, :2]))
        N = pd.shape[0]
        Z = list()
        for i in xrange(N):
            for j in xrange(i + 1, N):
                if pd[i, j] >= h - bw and pd[i, j] <= h + bw:
                    Z.append((P[i, 2] - P[j, 2])**2.0)
        return np.sum(Z) / (2.0 * len(Z))

    def _SV(self, P, hs, bw):
        '''
        Experimental variogram for a collection of lags
        '''
        sv = list()
        for h in hs:
            sv.append(self._SVh(P, h, bw))
        sv = [[hs[i], sv[i]] for i in range(len(hs)) if sv[i] > 0]
        return np.array(sv).T

    def _C(self, P, h, bw):
        """
        calculate nugget covariance of the variogram

        Parameters
        ----------
        P : ndarray
          samples
        h : scalar
          lag
        bw : scalar
          bandwidth

        Returns
        -------
        c0 : number
          nugget variance
        """
        c0 = np.var(P[:, 2])  # sill variance, which is a priori variance
        if h == 0:
            return c0
        return c0 - self._SVh(P, h, bw)

    def _cvmodel(self, P, model, hs, bw):
        '''
        Parameters
        ----------
        P : ndarray
          data
        model : callable
            modeling function

              - spherical
              - exponential
              - gaussian
        hs : ndarray
          distances
        bw : scalar
          bandwidth

        Returns
        -------
        covfct : callable
          the optimized function modeling the semivariogram
        '''
        sv = self._SV(P, hs, bw)  # calculate the semivariogram
        C0 = self._C(P, hs[0], bw)  # calculate the nugget
        param = self._opt(model, sv[0], sv[1], C0)

        def covfct(h, a=param):
            return model(h, a, C0)
        # covfct = partial(model, a=param, c0=C0)
        return covfct

    def _krige(self, P, model, hs, bw, u, N):
        '''
        Parameters
        ----------
        P : ndarray
          data
        model : callable
          modeling function
          (spherical, exponential, gaussian)
        hs:
          kriging distances
        bw:
          kriging bandwidth
        u:
          unsampled point
        N:
          number of neighboring points to consider

        Returns
        -------
        estimate : scalar
          krigged value
        '''
        # covfct = cvmodel(P, model, hs, bw)  # covariance function
        covfct = model
        mu = np.mean(P[:, 2])  # mean of the variable
        # distance between u and each data point in P
        d = np.sqrt((P[:, 0] - u[0])**2.0 + (P[:, 1] - u[1])**2.0)
        P = np.vstack((P.T, d)).T  # add these distances to P
        # sort P by these distances
        # take the first N of them
        P = P[d.argsort()[:N]]
        k = covfct(P[:, 3])  # apply the covariance model to the distances
        k = np.matrix(k).T  # cast as a matrix
        # form a matrix of distances between existing data points
        K = squareform(pdist(P[:, :2]))
        # apply the covariance model to these distances
        K = covfct(K.ravel())
        K = np.array(K)
        K = K.reshape(N, N)
        K = np.matrix(K)
        # calculate the kriging weights
        weights = np.linalg.inv(K) * k
        weights = np.array(weights)

        variance_sample = np.var(P[:, 2])
        variance = variance_sample - np.dot(k.T, weights)

        residuals = P[:, 2] - mu  # calculate the residuals

        # calculate the estimation
        estimation = np.dot(weights.T, residuals) + mu

        return float(estimation), float(variance)

if __name__ == '__main__':
    pass
