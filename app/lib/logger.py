import logging


class CustomLogger(logging.Logger):
    FORMAT = "[%(asctime)s] %(levelname)-6s %(filename)s+%(lineno)-4d %(name)s: [%(thread)d] %(message)s"
    DATE_FORMAT = "%H:%M:%S"

    def __init__(self, name: str, level: int) -> None:
        super().__init__(name, level)
        self._init_stdout_handler()

    def _init_stdout_handler(self) -> None:
        formatter = logging.Formatter(self.FORMAT, datefmt=self.DATE_FORMAT)
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def init_file_handler(self, filename: str) -> None:
        formatter = logging.Formatter(self.FORMAT, datefmt=self.DATE_FORMAT)
        handler = logging.FileHandler(filename, delay=False)
        handler.setLevel(self.level)
        handler.setFormatter(formatter)
        self.addHandler(handler)


def get_logger(name: str, level: int = logging.NOTSET) -> CustomLogger:
    return CustomLogger(name, level)
