from pydantic import ConfigDict


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


CAMEL_CONFIG: ConfigDict = {
    "from_attributes": True,
    "alias_generator": to_camel,
    "populate_by_name": True,
}
