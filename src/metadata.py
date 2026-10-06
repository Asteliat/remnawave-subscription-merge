from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubscriptionMetadata:
    download: int
    upload: int
    total: int
    expire: int

    def userinfo(self) -> str:
        return f"upload={self.upload};download={self.download};total={self.total};expire={self.expire}"


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

    # Remnawave uses total=0 to mean unlimited. If either subscription is
    # unlimited, the merged subscription must remain unlimited.
    total = 0 if first.total == 0 or second.total == 0 else first.total + second.total
    return SubscriptionMetadata(
        download=first.download + second.download,
        upload=first.upload + second.upload,
        total=total,
        expire=max(first.expire, second.expire),
    ).userinfo()
