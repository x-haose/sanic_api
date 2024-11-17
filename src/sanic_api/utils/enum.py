import json
from dataclasses import dataclass, field
from enum import Enum, auto
from types import DynamicClassAttribute
from typing import Any


@dataclass
class EnumField:
    """
    枚举字段类
    """

    value: Any = field(default=auto())
    desc: str = field(default_factory=str)


class EnumBase(Enum):
    """
    枚举基类
    """

    @classmethod
    def _missing_(cls, value: object) -> Any:
        result = list(filter(lambda d: d.value == value, cls))
        return result[0] if result else None

    @DynamicClassAttribute
    def value(self) -> Any:
        """
        获取枚举的值
        Returns:

        """
        if isinstance(self._value_, EnumField):
            return self._value_.value
        return self._value_

    @DynamicClassAttribute
    def desc(self) -> str:
        """
        获取枚举值的描述
        Returns:

        """
        if isinstance(self._value_, EnumField):
            return self._value_.desc
        else:
            return ""

    @classmethod
    def list(cls) -> list:
        return [c.value for c in cls]

    @classmethod
    def to_desc(cls) -> str:
        data = {d.value: d.desc for d in cls}
        return json.dumps(data, ensure_ascii=False)
