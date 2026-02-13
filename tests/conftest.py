from __future__ import annotations

import pytest


@pytest.fixture
def sample_html_content() -> str:
    return "<html><body><h1>Test</h1></body></html>"


@pytest.fixture
def sample_md_content() -> str:
    return "# Test\n\nThis is a test."
