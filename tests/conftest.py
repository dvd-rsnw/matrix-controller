from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).parent / "golden"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden frame files instead of asserting against them",
    )


@pytest.fixture
def assert_matches_golden(request: pytest.FixtureRequest):
    def check(actual: str, name: str) -> None:
        path = GOLDEN_DIR / f"{name}.txt"
        if request.config.getoption("--update-golden"):
            GOLDEN_DIR.mkdir(exist_ok=True)
            path.write_text(actual + "\n")
            pytest.skip(f"updated golden file {path.name}")
        expected = path.read_text().rstrip("\n")
        assert actual == expected, (
            f"rendered frame differs from {path.name} — run with --update-golden "
            "and review the diff if the change is intentional"
        )

    return check
