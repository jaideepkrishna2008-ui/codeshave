import ast
import pytest
from contextforge.parser import compress_source, extract_symbols


SAMPLE_CODE = '''
"""Module docstring for sample service."""

import os
from typing import List, Optional

MAX_RETRIES: int = 5
API_ENDPOINT = "https://api.example.com/v1"

class UserService:
    """Manages user persistence and validation."""
    table_name: str = "users"

    def __init__(self, db_url: str):
        self.db_url = db_url
        self._connection = None

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Fetch user by primary key."""
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = await self._execute(query)
        return result

    def _internal_helper(self) -> None:
        pass

@pytest.mark.asyncio
async def fetch_all(limit: int = 100) -> List[dict]:
    """Top level query helper."""
    records = []
    for i in range(limit):
        records.append({"id": i})
    return records
'''


def test_compress_source_preserves_signatures_and_docstrings():
    compressed = compress_source(SAMPLE_CODE, preserve_docstrings=True)

    # Must be 100% syntactically valid Python code
    parsed = ast.parse(compressed)
    assert parsed is not None

    # Check that structural elements exist
    assert "class UserService:" in compressed
    assert "async def get_user_by_id(self, user_id: int) -> Optional[dict]:" in compressed
    assert "Fetch user by primary key." in compressed
    assert "MAX_RETRIES: int = 5" in compressed

    # Check that internal implementation was stripped
    assert 'query = f"SELECT * FROM users WHERE id = {user_id}"' not in compressed
    assert "records.append" not in compressed
    assert "..." in compressed


def test_compress_source_no_docstrings():
    compressed = compress_source(SAMPLE_CODE, preserve_docstrings=False)
    assert ast.parse(compressed) is not None
    assert "Fetch user by primary key." not in compressed
    assert "Manages user persistence and validation." not in compressed
    assert "async def get_user_by_id(self, user_id: int) -> Optional[dict]:" in compressed


def test_compress_source_omit_private():
    compressed = compress_source(SAMPLE_CODE, preserve_private=False)
    assert ast.parse(compressed) is not None
    assert "_internal_helper" not in compressed
    assert "get_user_by_id" in compressed


def test_extract_symbols():
    symbols = extract_symbols(SAMPLE_CODE)
    names = [s.name for s in symbols]
    assert "UserService" in names
    assert "fetch_all" in names
