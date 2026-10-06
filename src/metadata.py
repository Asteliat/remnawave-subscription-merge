from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubscriptionMetadata:
    download: int
    upload: int
    total: int
    expire: int

    def userinfo(self) -> str:
        return f"download={self.download};upload={self.upload};total={self.total};expire={self.expire}"


def parse_userinfo(value: str | None) -> SubscriptionMetadata | None:
    if not value:
        return None
    fields = {}
    for item in value.split(";"):
        if not item.strip():
            continue
        key, sep, raw = item.partition("=")
        if not sep:
            raise ValueError("invalid subscription-userinfo metadata")
        fields[key.strip().lower()] = raw.strip()
    required = ("download", "upload", "total", "expire")
    if any(key not in fields for key in required):
        raise ValueError("incomplete subscription-userinfo metadata")
    try:
        values = {key: int(fields[key]) for key in required}
    except ValueError as exc:
        raise ValueError("invalid subscription-userinfo metadata") from exc
    if any(value < 0 for value in values.values()):
        raise ValueError("invalid subscription-userinfo metadata")
    return SubscriptionMetadata(**values)


def merge_userinfo(main: str | None, secondary: str | None) -> str | None:
    first = parse_userinfo(main)
    second = parse_userinfo(secondary)
    if first is None and second is None:
        return None
    if first is None:
        return second.userinfo()
    if second is None:
        return first.userinfo()
    return SubscriptionMetadata(
        download=first.download + second.download,
        upload=first.upload + second.upload,
        total=first.total + second.total,
        expire=max(first.expire, second.expire),
    ).userinfo()
