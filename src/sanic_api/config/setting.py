from hs_config import SettingsBase
from pydantic import BaseModel, Field, FilePath, HttpUrl, NewPath

from sanic_api.utils.enum import EnumBase, EnumField


class RunModeEnum(EnumBase):
    """
    运行模式
    """

    DEBNUG = EnumField("debug", desc="开发模式")
    PRODUCTION = EnumField("prod", desc="生产模式")


class LoggerSettings(BaseModel):
    """
    日志配置类
    """

    # 日志文件路径
    file: FilePath | NewPath | None = Field(default=None)

    # 自动轮转条件。就是保留几天的日志。
    # 具体查看loguru文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file
    rotation: str | None = Field(default=None)

    # 日志文件保留条件。就是保留多大的日志。
    # 具体查看loguru文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file
    retention: str | None = Field(default=None)

    # 日志文件的压缩格式。zip、gz、tar等。
    # 体查看loguru文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file
    compression: str | None = Field(default=None)

    # loji的地址。如果存在，则会把日志推送给logki
    loki_url: HttpUrl | None = Field(default=None)


class DefaultSettings(SettingsBase):
    """
    配置类
    """

    # 主机
    host: str = Field(default="127.0.0.1")

    # 端口
    port: int = Field(default=6969)

    # 运行模式
    mode: RunModeEnum = Field(default=RunModeEnum.DEBNUG)

    # 运行环境，仅作为环境标识。
    # 尽量不要使用这个字段去做逻辑判断。请使用mode去进行判断，因为测试环境、预发布环境、生产环境都应属于生产模式模式
    envornment: str = Field(default="dev")

    # 自动重载。生产模式强制关闭
    auto_reload: bool = Field(default=False)

    # 访问日志开关
    access_log: bool = Field(default=True)

    # 跨域设置
    cors_origins: list[str] | None = Field(default_factory=list)

    # 哨兵连接dsn，如果存在则会把错误信息推送给哨兵
    sentry_dsn: HttpUrl | None = Field(default=None)

    # 日志配置
    logger: LoggerSettings = Field(default_factory=LoggerSettings)
