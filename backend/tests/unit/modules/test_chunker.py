import pytest
from chunker import Chunk, chunk_text


# ── 基本結構 ──────────────────────────────────────────────────────────────────

def test_returns_list_of_chunks():
    chunks = chunk_text("Hello world", chunk_size=100)
    assert isinstance(chunks, list)
    assert all(isinstance(c, Chunk) for c in chunks)


def test_chunk_fields_populated():
    chunks = chunk_text("Hello world", chunk_size=100)
    c = chunks[0]
    assert c.text != ""
    assert c.start_token == 0
    assert c.end_token > 0
    assert c.token_count == c.end_token - c.start_token
    assert c.index == 0


# ── 邊界情況 ──────────────────────────────────────────────────────────────────

def test_empty_string_returns_empty_list():
    assert chunk_text("") == []


def test_short_text_returns_single_chunk():
    chunks = chunk_text("Hello world", chunk_size=512)
    assert len(chunks) == 1
    assert chunks[0].index == 0


def test_exact_chunk_size_returns_single_chunk():
    """token 數恰好等於 chunk_size，應只產生一個 chunk。"""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    text = "word " * 10          # 產生固定數量 token
    token_count = len(enc.encode(text))
    chunks = chunk_text(text, chunk_size=token_count, overlap=0)
    assert len(chunks) == 1


# ── chunk_size / overlap 行為 ─────────────────────────────────────────────────

def test_chunk_size_respected():
    """每個 chunk（除最後一個）的 token_count 應等於 chunk_size。"""
    chunks = chunk_text("word " * 200, chunk_size=50, overlap=10)
    for c in chunks[:-1]:
        assert c.token_count == 50


def test_overlap_correct():
    """相鄰兩個 chunk 的 token 範圍重疊數應等於 overlap。"""
    chunks = chunk_text("word " * 200, chunk_size=50, overlap=10)
    for prev, curr in zip(chunks, chunks[1:]):
        actual_overlap = prev.end_token - curr.start_token
        assert actual_overlap == 10


def test_no_overlap():
    chunks = chunk_text("word " * 200, chunk_size=50, overlap=0)
    for prev, curr in zip(chunks, chunks[1:]):
        assert prev.end_token == curr.start_token


def test_index_is_sequential():
    chunks = chunk_text("word " * 200, chunk_size=50, overlap=10)
    for i, c in enumerate(chunks):
        assert c.index == i


def test_tokens_cover_full_text():
    """所有 chunk 合起來應覆蓋整個 token 序列（第一個 start=0，最後一個 end=total）。"""
    import tiktoken
    text = "word " * 200
    enc = tiktoken.get_encoding("cl100k_base")
    total = len(enc.encode(text))

    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert chunks[0].start_token == 0
    assert chunks[-1].end_token == total


def test_text_decode_matches_tokens():
    """chunk.text 應能由對應 token ids decode 還原。"""
    import tiktoken
    text = "The quick brown fox jumps over the lazy dog. " * 20
    enc = tiktoken.get_encoding("cl100k_base")
    token_ids = enc.encode(text)

    chunks = chunk_text(text, chunk_size=30, overlap=5)
    for c in chunks:
        expected = enc.decode(token_ids[c.start_token:c.end_token])
        assert c.text == expected


# ── 參數驗證 ──────────────────────────────────────────────────────────────────

def test_invalid_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)


def test_negative_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=-1)


def test_overlap_gte_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)


def test_negative_overlap_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=-1)
