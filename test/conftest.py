import pytest
import numpy as np

@pytest.fixture(scope="session", autouse=True)
def depth():
    return np.arange(10)
