import os

import pytest


@pytest.fixture(scope="session")
def real_indicxlit_engine():
    if os.getenv("RUN_INDICXLIT_INTEGRATION") != "1":
        pytest.skip(
            "Real IndicXlit integration tests are disabled. "
            "Set RUN_INDICXLIT_INTEGRATION=1 to enable them."
        )

    os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")

    try:
        from phase6.inference import create_engine
    except Exception as exc:
        pytest.fail(
            f"IndicXlit runtime dependencies could not be imported: {exc}",
            pytrace=True,
        )

    try:
        return create_engine()
    except Exception as exc:
        pytest.fail(
            f"IndicXlit runtime/model failed to initialize: {exc}",
            pytrace=True,
        )
