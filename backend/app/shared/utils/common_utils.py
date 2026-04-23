import re


def safe_upload_filename(name: str) -> str:
    """取得僅含檔名的安全字串，供儲存檔案使用。"""
    base = name.replace("\\", "/").split("/")[-1]
    base = re.sub(r"[^a-zA-Z0-9._\u4e00-\u9fff-]", "_", base).strip("._")[:200]
    return base or "unnamed"
