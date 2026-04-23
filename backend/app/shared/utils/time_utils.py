import datetime as dt


def datetime_utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)
