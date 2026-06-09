from dataclasses import dataclass

import tiktoken


@dataclass
class Chunk:
    """單一文本 chunk 的標準資料結構。"""

    text: str
    start_token: int
    end_token: int
    token_count: int
    index: int

    def __repr__(self) -> str:
        preview = self.text[:40].replace("\n", " ")
        return (
            f"Chunk(index={self.index}, tokens=[{self.start_token}:{self.end_token}], "
            f'text="{preview}...")'
        )


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
    encoding_name: str = "cl100k_base",
) -> list[Chunk]:
    """將輸入文本依 token 長度切分為多個 Chunk，支援滑動窗口重疊。

    Args:
        text:          任意長度的輸入文本。
        chunk_size:    每個 chunk 的最大 token 數（須 > 0）。
        overlap:       相鄰 chunk 間重疊的 token 數（須 < chunk_size）。
        encoding_name: tiktoken encoding 名稱，預設 cl100k_base（GPT-4 / GPT-3.5）。

    Returns:
        list[Chunk]：依序排列的 chunk 列表。

    Raises:
        ValueError: 當 chunk_size <= 0 或 overlap >= chunk_size 時。
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size 必須 > 0，目前為 {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap 必須 >= 0，目前為 {overlap}")
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) 必須小於 chunk_size ({chunk_size})")

    enc = tiktoken.get_encoding(encoding_name)
    token_ids: list[int] = enc.encode(text)
    total_tokens = len(token_ids)

    if total_tokens == 0:
        return []

    # 將 token 邊界對應回原文的字元偏移，避免對子序列 decode 時
    # 在 UTF-8 / BPE 邊界產生 ? 等替換字元。
    char_offsets = [0]
    for i in range(1, total_tokens + 1):
        char_offsets.append(len(enc.decode(token_ids[:i])))

    step = chunk_size - overlap
    chunks: list[Chunk] = []
    index = 0
    start = 0

    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_text_str = text[char_offsets[start] : char_offsets[end]]

        chunks.append(
            Chunk(
                text=chunk_text_str,
                start_token=start,
                end_token=end,
                token_count=end - start,
                index=index,
            )
        )

        if end == total_tokens:
            break

        start += step
        index += 1

    return chunks
