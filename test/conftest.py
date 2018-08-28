import pytest
import numpy as np

@pytest.fixture(scope="session", autouse=True)
def depth():
    return np.arange(10)


@pytest.fixture(scope='session')
def pseudo_las_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('fake.las')
    fn.write("Depth(M)\tVelocity(Meter/Second)\tShale_Volume(Fraction)\tOverburden_Pressure(MegaPascal)\n0.0\t1e30\t1e30\t21.59144783\n0.1\t1e30\t1e30\t21.59350014\n0.2\t1e30\t1e30\t21.59555817\n0.3\t1e30\t1e30\t21.59760857\n0.4\t1e30\t1e30\t21.59966278\n0.5\t1e30\t1e30\t21.60171509\n0.6\t1e30\t1e30\t21.6037693\n0.7\t1e30\t1e30\t21.60582542\n0.8\t1e30\t1e30\t21.60787773\n0.9\t1e30\t1e30\t21.60993195\n1.0\t1e30\t0.0934\t21.61189842\n1.1\t1e30\t0.0909\t21.61394691\n1.2\t1e30\t0.09070902\t21.616045\n1.3\t1e30\t0.0944\t21.6181488\n1.4\t1e30\t0.102\t21.62023735\n1.5\t1e30\t0.1097\t21.62229919\n1.6\t1e30\t0.1147\t21.62433434\n1.7\t1e30\t0.1178112\t21.62635612\n1.8\t1e30\t0.1224\t21.62836266\n1.9\t1e30\t0.1296\t21.63037682\n2.0\t1e30\t0.138\t21.63240242\n")
    return fn

@pytest.fixture(scope='session')
def mdf5_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('fake.h5')
    return fn
