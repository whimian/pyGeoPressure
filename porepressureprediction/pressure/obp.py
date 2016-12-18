import numpy as np


def traugott(z, a, b):
    """
    estimate density with depth

    Parameters
    ----------
    depth : 1-d ndarray

    a, b: scalar

    Notes
    -----
    .. math:: \overline{\rho (h)}=16.3+{h/3125}^{0.6}
    gives the average sediment density in pounds per gallon (ppg) mud weight
    equivalent between the sea floor and depth h (in feet) below the sea floor.

    So, density variation with depth takes the form

    .. math:: \rho(z) = {\rho}_{0} + a{z}^{b}

    .. [1] Traugott, Martin. "Pore/fracture pressure determinations in deep
       water." World Oil 218.8 (1997): 68-70.
    """
    # rho0 = 2.65
    return 1.70 + a * z**b


def gardner(v, c, d):
    """
    Estimate density with velocity

    Parameters
    ----------
    v : 1-d ndarray
        interval velocity array
    c : float, optional
        coefficient a
    d : float, optional
        coefficient d

    Returns
    -------
    out : 1-d ndarray
        density array

    Notes
    -----
    .. math:: \rho = c{V}^{d}

    typical values for a and b in GOM coast are a=0.31, b=0.25

    [1]G. Gardner, L. Gardner, and A. Gregory, "Formation velocity and density
       - the diagnostic basics for stratigraphic traps," Geophysics, vol. 39,
       no. 6, pp. 770-780, 1974.
    """
    return c * v**d


def overburden_pressure(depth, rho, kelly_bushing=41, depth_w=82, rho_w=1.01):
    """
    Calculate Overburden Pressure

    Parameters
    ----------
    depth : 1-d ndarray
    rho : 1-d ndarray
        density in g/cm3
    kelly_bushing : scalar
        kelly bushing elevation in meter
    depth_w : scalar
        from sea level to sea bottom (a.k.a mudline) in meter
    rho_w : scalar
        density of sea water - depending on the salinity of sea water
        (1.01-1.05g/cm3)

    Returns
    -------
    obp : 1-d ndarray
        overburden pressure in mPa
    """
    g = 9.80665  # m/s2
    depth = np.array(depth)
    rho = np.array(rho)
    rho = 1000 * rho  # convert unit from g/cm3 to kg/m3
    rho_w = 1000 * rho_w
    mask = depth < kelly_bushing + depth_w
    rho[mask] = rho_w
    mask = depth < kelly_bushing
    rho[mask] = 0
    delta_h = np.zeros(depth.shape)
    delta_h[1:] = depth[1:] - depth[:-1]
    p = rho * delta_h * g
    obp = np.cumsum(p)
    water_pressure = rho_w * depth_w * g  # pressure of water column
    obp = obp + water_pressure
    obp_dtype = np.dtype([("depth", 'f8'),
                          (("Overburden pressure in Pa", "obp"), 'f8')])
    OBP = np.zeros(depth.shape, dtype=obp_dtype)
    OBP['depth'] = depth
    OBP['obp'] = obp / 1000000
    return OBP
