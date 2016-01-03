'''
1. Building of the sampled covariance C (Fig. 1).
2. Generation of the normal deviates z on the grid.
3. Calculation of the Fourier transforms of z and C, giving Z and the power
   spectrum S, respectively.
4. Derivation of G from S.
5. Multiplication of G by Z.
6. Inverse Fourier transform of (G * Z) giving g*z.
7. Derivation of y from Equation (4).
'''
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft2, ifft2
from autocorrelation import autocorrelation_func


def fft_ma(m, n, a, b, r, dx, dy):
    C = np.zeros((m, n))
    au = autocorrelation_func(a, b)
    for i in xrange(m):
        for j in xrange(n):
            C[i, j] = au.gaussian((i-(m-1)/2.)*dy, (j-(n-1)/2.)*dx)
    S = fft2(C)  # power spectral density
    z = np.random.randn(m, n)
    Z = fft2(z)
    G = np.sqrt(dx * S)
    GZ = G * Z
    gz = ifft2(GZ)
    A = np.real(gz)
    K = np.real(A)
    return K


if __name__ == "__main__":
    m = 200
    n = 200
    a = 20
    b = 20
    r = 1
    vp0 = 1500
    variance = 0.08
    dx = 3
    dy = 3
    field = fft_ma(m, n, a, b, r, dx, dy)

    fig, ax = plt.subplots()
    ax.imshow(field)
    fig.savefig('temp.png', dpi=200)
