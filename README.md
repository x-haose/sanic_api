[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg?logo=python)]()
[![Sanic](https://img.shields.io/badge/framework-Sanic-Server.svg)](http://www.gnu.org/licenses/agpl-3.0)

# Sanic-API

让您的sanic服务程序更好的支持API文档、参数校验、日志打印、响应规范等

## 特性

- 无需任何多余改动，全自动生成openapi文档，使用更加方便 (新版方案正在积极优化开发中)

- 基于`pydantic`的参数校验器，让接口的请求及响应更符合你的预期，使用更方便

- 使用`loguru`库代替官方`logging`日志库，并对访问日志进行扩展，支持写入文件及推送loki

- 使用了基于`pydantic-settings`的项目配置方案，支持json、yml、ini、.env等多种格式

- 对sanic的启动进行了简单的封装，可快速启动项目


## 截图

## 路线图

- 全自动生成openapi文档

- 编写详细文档

## 安装

使用 pip 安装 sanic-api

```bash
  pip install sanic-api
```

## 使用方法/示例

### 最小示例
```python
from sanic_api.app import BaseApp


class App(BaseApp):
    """
    最小的sanic服务示例
    """


if __name__ == "__main__":
    App.run()
```

### 带参数校验的示例
```python
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
```

## 开发

要部署这个项目，请先安装rye

```bash
  rye sync
```

## 文档
正在编写中，敬请期待