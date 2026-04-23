# Alembic Migration

Alembic 是 SQLAlchemy 的官方遷移工具，透過 migration script 追蹤資料庫 schema 的變化。

---

## 產生 Migration

```bash
alembic revision --autogenerate -m "<message>"
```
👉 產生的檔案會放在 `alembic/versions/` 目錄中。

---

## 更新資料庫（套用 Migration）

```bash
alembic upgrade head
```

* 執行所有尚未套用的遷移，將資料庫更新到最新狀態。

```bash
alembic upgrade <版本號>
```

* 將資料庫更新到指定版本（例如 `alembic upgrade abc123`）。

---

## 回復資料庫（Rollback）

```bash
alembic downgrade -1
```

* 回復上一個版本。

```bash
alembic downgrade base
```

* 回復到最初版本（相當於清空 migration）。

```bash
alembic downgrade <版本號>
```

* 回復到指定版本。

---

## 額外常用指令

### 檢查當前版本

```bash
alembic current
```

### 查看所有歷史紀錄

```bash
alembic history
```

### 查看當前資料庫的 head（最新版本）

```bash
alembic heads
```

### 查看尚未套用的遷移

```bash
alembic check
```

---