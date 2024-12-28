import sentry_sdk
from sanic import Sanic, text
from sanic.log import logger
from sanic.worker.loader import AppLoader
from sanic_ext import Extend
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from sanic_api import LoggerExtend
from sanic_api.api import Request
from sanic_api.config import DefaultSettings, RunModeEnum


class BaseApp:
    name: str = "sanic-server"
    settings: DefaultSettings

    def __init__(self, settings: DefaultSettings):
        self.settings = settings

    @classmethod
    def run(cls, settings: DefaultSettings = None):
        """
        运行服务
        Args:
            settings: 设置，为空就使用默认设置

        Returns:

        """
        if not cls.name:
            raise ValueError("请设置服务名称！")

        settings = settings or DefaultSettings()
        self = cls(settings)
        loader = AppLoader(factory=self._create_app)
        app = loader.load()

        # 服务配置
        # 开发模式下workers指定为1，自动重载根据配置决定，默认关闭，跨域设置为允许所有跨域
        # 生产模式下使用fast模型，自动指定最多的workers，自定重载强制关闭，跨域使用配置中的跨域列表
        # 默认启用sanic_ext里面的后台日志记录器
        motd_display = {"envornment": settings.envornment}
        config = {"access_log": settings.access_log, "motd_display": motd_display}
        if settings.mode == RunModeEnum.DEBNUG:
            config.update({"auto_reload": settings.auto_reload, "workers": 1, "debug": True})
        else:
            config.update({"fast": True, "auto_reload": False})

        app.prepare(settings.host, settings.port, **config)
        Sanic.serve(primary=app, app_loader=loader)

    def _create_app(self):
        """
        创建app的内部工厂方法
        Returns:

        """
        app = Sanic(self.name, configure_logging=False, request_class=Request)

        self._setup_logger(app)
        self._setup_config(app)

        app.main_process_stop(self._main_process_stop)
        app.main_process_start(self._main_process_start)
        app.before_server_start(self._before_server_start)
        app.before_server_stop(self._before_server_stop)
        app.after_server_start(self._after_server_start)
        app.after_server_stop(self._after_server_stop)
        return app

    async def _main_process_start(self, app: Sanic):
        """
        主进程启动的内部方法
        Args:
            app:

        Returns:

        """
        logger.info("主进程启动")
        await self.main_process_start(app)

    async def _main_process_stop(self, app: Sanic):
        """
        主进程停止的内部方法
        Args:
            app:

        Returns:

        """
        logger.info("主进程停止")
        await self.main_process_stop(app)

    async def _before_server_start(self, app: Sanic):
        """
        工作进程启动之前的内部方法。
        设置路由写在这里是因为sanic_ext是会在before_server_start阶段对路由设置_cors属性
        Args:
            app:

        Returns:

        """
        logger.info(f"工作进程 {app.m.pid} 即将启动")

        await self._setup_route(app)
        await self.before_server_start(app)

    async def _before_server_stop(self, app: Sanic):
        """
        服务停止之前的内部方法
        Args:
            app:

        Returns:

        """
        logger.info(f"工作进程 {app.m.pid} 即将停止")
        await self.before_server_stop(app)

    async def _after_server_start(self, app: Sanic):
        """
        服务启动之后的内部方法
        Args:
            app:

        Returns:

        """
        logger.info(f"工作进程 {app.m.pid} 启动完毕")
        await self.after_server_start(app)

    async def _after_server_stop(self, app: Sanic):
        """
        服务停止之后的内部方法
        Args:
            app:

        Returns:

        """
        logger.info(f"工作进程 {app.m.pid} 停止")
        await self.after_server_stop(app)

    def _setup_config(self, app: Sanic):
        """
        设置配置
        Args:
            app: Sanic App

        Returns:

        """
        app.config.LOGGING = True
        self._setup_cors(app)

    def _setup_cors(self, app: Sanic):
        """
        设置跨域: 开发模式下允许所有跨域，生产模式下使用配置中的跨域列表
        Args:
            app: Sanic App

        Returns:

        """
        if self.settings.mode == RunModeEnum.DEBNUG:
            app.config.CORS_ORIGINS = "*"
            app.config.CORS_SEND_WILDCARD = True
        else:
            app.config.CORS_ORIGINS = ",".join(self.settings.cors_origins)

    async def _setup_route(self, app: Sanic):
        """
        设置路由和蓝图的内部方法，自动设置一个ping的路由
        Args:
            app: Sanic App

        Returns:

        """
        app.add_route(self._ping, "ping", methods=["GET", "POST"])
        await self.setup_route(app)

    def _setup_logger(self, app: Sanic):
        """
        设置日志
        Args:
            app: Sanic App

        Returns:

        """
        log_config = self.settings.logger
        log_ext = LoggerExtend(
            app,
            log_file=log_config.file,
            rotation=log_config.rotation,
            retention=log_config.retention,
            compression=log_config.compression,
            loki_url=log_config.loki_url,
            loki_labels={"Application": self.name, "Envornment": self.settings.envornment},
        )
        Extend.register(log_ext)

    def _setup_sentry(self, _app: Sanic):
        """
        如果存在sentryURL配置，则自动设置sentry哨兵
        Args:
            _app: Sanic App

        Returns:

        """
        if self.settings.sentry_dsn is None:
            return

        sentry_sdk.init(
            dsn=self.settings.sentry_dsn,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for tracing.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
            integrations=[AsyncioIntegration()],
        )

    async def _ping(self, _request):
        return text("ok")

    async def main_process_start(self, app: Sanic):
        """
        主进程启动的方法
        Args:
            app: Sanic App

        Returns:

        """

    async def main_process_stop(self, app: Sanic):
        """
        主进程停止的方法
        Args:
            app: Sanic App

        Returns:

        """

    async def before_server_start(self, app: Sanic):
        """
        工作进程启动之前的方法。
        Args:
            app: Sanic App

        Returns:

        """

    async def before_server_stop(self, app: Sanic):
        """
        工作进程停止之前的方法。
        Args:
            app: Sanic App

        Returns:

        """

    async def after_server_start(self, app: Sanic):
        """
        工作进程启动之后的方法。
        Args:
            app: Sanic App

        Returns:

        """

    async def after_server_stop(self, app: Sanic):
        """
        工作进程停止之后的方法。
        Args:
            app: Sanic App

        Returns:

        """

    async def setup_route(self, app: Sanic):
        """
        继承此方法去设置蓝图及路由
        Args:
            app: Sanic App

        Returns:

        """
