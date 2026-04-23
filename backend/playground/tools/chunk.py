import sys

sys.path.append(".")

from app.modules.rag.chunker import chunk_text

with open("playground/常暗之廂.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_text(text, chunk_size=1024, overlap=128)

for chunk in chunks:
    print(chunk.text)
    print(chunk.start_token)
    print(chunk.end_token)
    print(chunk.token_count)
    print(chunk.index)
    print("-" * 100)
