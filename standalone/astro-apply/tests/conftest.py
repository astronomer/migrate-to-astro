import os

import pytest

manual_tests = pytest.mark.skipif(not bool(os.getenv("MANUAL_TESTS")), reason="requires env setup")
