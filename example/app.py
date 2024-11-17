from pydantic import BaseModel, Field
from sanic import Blueprint, Sanic, json
from sanic.log import logger

from sanic_api.api import BaseRespTml, Request
from sanic_api.app import BaseApp

user_blueprint = Blueprint("user", "/user")


class UserInfoModel(BaseModel):
    user_id: int = Field(title="用户ID")


class UserInfoResponse(BaseRespTml):
    user_name: str = Field(title="用户名")


class UseLoginRequest(Request):
    form_data: UserInfoModel


@user_blueprint.post("info")
async def user_info(request: Request, json_data: UserInfoModel):
    """
    获取用户信息
    """
    logger.info(f"data: {json_data}")
    info = UserInfoResponse(user_name="张三")
    info.temp_data.code = "0000"
    info.temp_data.msg = "查询成功"
    return info.resp()


@user_blueprint.post("login")
async def user_login(request: UseLoginRequest):
    """
    用户登录
    """
    logger.info(f"user_id: {request.form_data.user_id}")
    return json(request.form_data.model_dump())


class App(BaseApp):
    """
    服务示例
    """

    async def setup_route(self, app: Sanic):
        api = Blueprint.group(url_prefix="api")
        api.append(user_blueprint)
        app.blueprint(api)


if __name__ == "__main__":
    App.run()
