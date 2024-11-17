import inspect
import logging.config
from logging import LogRecord, StreamHandler

from loguru import logger
from sanic import BadRequest, Request, Sanic


class InterceptHandler(StreamHandler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        # 获取标准日志的扩展信息
        default_record = LogRecord("", 0, "", 0, "", None, None, "")
        etxra_info = {key: value for key, value in record.__dict__.items() if key not in default_record.__dict__}

        # 加入情求ID。用来识别情求链
        req_id = self._get_req_id()
        if req_id:
            etxra_info.update({"req_id": req_id})

        # 给访问日志里面加入情求体数据
        if record.name == "sanic.access":
            req_body = self._get_req_body()
            etxra_info.update({"req_body": req_body})

        # 如果没有扩展信息，则为空字符串
        etxra_info = etxra_info if etxra_info else ""

        # 如果有扩展信息，则在信息后面加个空格
        src_msg = record.getMessage()
        msg = f"{src_msg} " if etxra_info and src_msg else src_msg

        # 把标准日志的名字加入到loguru日志的type字段
        etxra_data = {"type": record.name, "etxra_info": etxra_info}
        logger.bind(**etxra_data).opt(depth=depth, exception=record.exc_info).log(level, msg)

    # noinspection PyUnresolvedReferences,PyBroadException
    @staticmethod
    def _get_req() -> Request | None:
        """
        获取请求
        """

        try:
            app = Sanic.get_app()
            req = app.request_class.get_current()
        except Exception:
            req = None
        return req

    def _get_req_id(self) -> str:
        """
        获取请求ID
        """

        req = self._get_req()
        return str(req.id) if req else ""

    def _get_req_body(self) -> dict | None:
        """
        获取请求体数据

        Returns:
            返回具有 json、query、form参数的json
        """
        req = self._get_req()
        if not req:
            return None

        data = {}
        for attr in ["args", "form"]:
            attr_data = {}
            for k, v in getattr(req, attr).items():
                if isinstance(v, list) and len(v) == 1:
                    attr_data[k] = v[0]
                else:
                    attr_data[k] = v
            if attr_data:
                data[attr] = attr_data

        try:
            if req.json:
                data["json"] = req.json
        except BadRequest:
            ...

        return data
