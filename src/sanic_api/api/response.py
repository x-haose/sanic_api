from typing import Any, ClassVar

from pydantic import BaseModel, Field, PrivateAttr
from sanic.compat import Header
from sanic.response import JSONResponse


class TempModel(BaseModel):
    _data_field: str = PrivateAttr(default="data")
    data: Any = Field(default=None, title="数据")
    code: str = Field(default_factory=str, title="业务状态码")
    msg: str = Field(default_factory=str, title="消息")

    def get_data_field_name(self) -> str:
        return self._data_field


class BaseResp(BaseModel):
    temp_data: ClassVar = Ellipsis

    def resp(self, status: int = 200, headers: Header | dict[str, str] | None = None) -> JSONResponse:
        data = self.model_dump(mode="json")
        return JSONResponse(data, status=status, headers=headers)


class BaseRespTml(BaseModel):
    temp_data: TempModel | None = Field(default_factory=TempModel)

    def resp(self, status: int = 200, headers: Header | dict[str, str] | None = None) -> JSONResponse:
        tmp_data_field_name = self.temp_data.get_data_field_name()
        self_data = self.model_dump(mode="json", exclude={"temp_data"})
        setattr(self.temp_data, tmp_data_field_name, self_data)
        tml_data = self.temp_data.model_dump(mode="json")
        return JSONResponse(tml_data, status=status, headers=headers)
