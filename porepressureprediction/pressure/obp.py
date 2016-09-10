import numpy as np


def traugott(depth, a=16.3, b=3125, c=0.6):
    """
    estimate density with depth

    Parameters
    ----------
    depth : 1-d ndarray

    a, b, c: scalar

    Notes
    -----
    .. math:: \cap{\rho (h)}=a+{h/b}^{c}

    .. math:: \cap{\rho (h)}=16.3+{h/3125}^{0.6}
    gives the average sediment density in pounds per gallon (ppg) mud weight
    equivalent between the sea floor and depth h (in feet) below the sea floor.

    .. [1] Traugott, Martin. "Pore/fracture pressure determinations in deep
       water." World Oil 218.8 (1997): 68-70.
    """
    return a + (depth / b)**c


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
    """
    rho = c * v**d
    return rho


def overburden_pressure(depth, rho, depth_w=90, rho_w=1.01, g=0.98):
    """
    Calculate Overburden Pressure

    Parameters
    ----------
    depth : 1-d ndarray
    rho : 1-d ndarray
        density in g/cm3
    depth_w : scalar
        from sea level to sea bottom (a.k.a mudline) in meters
    rho_w : scalar
        density of sea water - depending on the salinity of sea water
        (1.01-1.05g/cm3)
    g : scalar
        gravitational acceleration in m/s2

    Returns
    -------
    obp : 1-d ndarray
        overburden pressure in Pa
    """
    rho = 1000 * rho  # convert unit from g/cm3 to kg/m3
    rho_w = 1000 * rho_w
    delta_h = np.zeros(depth.shape)
    delta_h[1:] = depth[1:] - depth[:-2]
    p = rho * delta_h * g
    obp = np.cumsum(p)
    water_pressure = rho_w * depth_w * g  # pressure of water column
    obp = obp + water_pressure
    obp_dtype = np.dtype([("depth", 'f8'),
                          (("Overburden pressure in Pa", "obp"), 'f8')])
    OBP = np.zeros(depth.shape, dtype=obp_dtype)
    OBP['depth'] = depth
    OBP['obp'] = obp
    return OBP
