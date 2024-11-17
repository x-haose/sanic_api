import logging
import logging.config
import sys
from pathlib import Path

from loguru import logger

# noinspection PyProtectedMember
from loguru._defaults import env
from loki_logger_handler.loki_logger_handler import LoguruFormatter, LokiLoggerHandler
from sanic import Sanic
from sanic.application.constants import Mode
from sanic_ext import Extension

from sanic_api.logger.config import InterceptHandler


class LoggerExtend(Extension):
    """
    处理日志的扩展
    """

    name = "LoguruExtend"

    def __init__(
        self,
        app: Sanic,
        *,
        log_file: str | Path | None = None,
        rotation: str | None = None,
        retention: str | None = None,
        compression: str | None = None,
        loki_url: str | None = None,
        loki_labels: dict[str, str] | None = None,
    ):
        """
        Args:
            app: sanic app
            log_file: 日志文件的路径
            rotation: 日志文件自动轮转条件：查看loguru文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file
            retention: 日志文件保留条件： 查看loguru文档：https://loguru.readthedocs.io/en/stable/api/logger.html#file
            compression: 日志文件压缩格式： "gz", "bz2", "xz", "lzma", "tar", "tar.gz", "tar.bz2", "tar.xz", "zip"
            loki_url: 推送loki的url
            loki_labels：loki推送时的标签

        """
        self.app = app
        self.log_file = log_file
        self.rotation = rotation
        self.retention = retention
        self.compression = compression
        self.loki_url = loki_url
        self.loki_labels = loki_labels
        self.setup()

    def startup(self, bootstrap) -> None:
        """
        扩展在初始化时安装，保留他是为了证明是一个扩展
        因为要拦截sanic.application.motd:display的日志，所以不能写在这里
        Args:
            bootstrap:

        Returns:

        """

    def setup(self):
        """
        安装扩展
        Returns:

        """
        logger.remove()

        log_format = env(
            "LOGURU_FORMAT",
            str,
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<red>{extra[type]: <10}</red> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>{extra[etxra_info]}",
        )

        # 基本的控制台输出
        log_handlers = [
            {"sink": sys.stdout, "format": log_format, "colorize": True},
        ]

        # 日志文件输出
        if self.log_file:
            self.log_file = self.log_file if isinstance(self.log_file, Path) else Path(self.log_file)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            log_handlers.append(
                {
                    "sink": self.log_file,
                    "format": log_format,
                    "colorize": False,
                    "serialize": True,
                    "compression": self.compression,
                    "rotation": self.rotation,
                    "retention": self.retention,
                }
            )

        # loki 推送
        if self.loki_url:
            loki_handler = LokiLoggerHandler(
                url=self.loki_url,
                labels=self.loki_labels or {},
                labelKeys={},
                timeout=10,
                defaultFormatter=LoguruFormatter(),
            )
            log_handlers.append(
                {
                    "sink": loki_handler,
                    "format": log_format,
                    "colorize": False,
                    "serialize": True,
                }
            )

        # 配置日志
        logger.configure(handlers=log_handlers)

        # 接收logging的日志
        log_level = logging.DEBUG if self.app.state.mode is Mode.DEBUG else logging.INFO
        logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)
