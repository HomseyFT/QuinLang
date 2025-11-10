from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Type:
    name: str
    size: int  # bytes

    def __str__(self) -> str:
        return self.name

Int = Type("int", 2)
Str = Type("str", 2)  # pointer to string data
Void = Type("void", 0)
Bool = Type("bool", 1)

BUILTIN_TYPES: Dict[str, Type] = {
    "int": Int,
    "str": Str,
    "void": Void,
    "bool": Bool,
}

def type_from_name(name: str) -> Type:
    if name in BUILTIN_TYPES:
        return BUILTIN_TYPES[name]
    # Unknown types default to int for now (placeholder)
    return Int