import logging
import sys
from typing import Optional
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlignedColorFormatter(logging.Formatter):
    """
    Formatter tùy chỉnh với căn chỉnh thẳng hàng và mã màu ANSI
    """

    # Mã màu ANSI
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Xanh lá
        "WARNING": "\033[33m",   # Vàng
        "ERROR": "\033[31m",     # Đỏ
        "CRITICAL": "\033[41m",  # Nền đỏ cho critical
        "RESET": "\033[0m",      # Reset về màu mặc định
    }
    
    # Độ rộng cố định cho mỗi phần của log
    LEVEL_WIDTH = 9      # Độ rộng cho log level
    TIME_WIDTH = 24      # Độ rộng cho thời gian (YYYY-MM-DD HH:MM:SS)
    NAME_WIDTH = 24      # Độ rộng cho tên logger

    def format(self, record: logging.LogRecord) -> str:
        # Lưu levelname gốc
        levelname = record.levelname
        
        # Thêm màu vào levelname và căn chỉnh
        colored_level = ""
        if levelname in self.COLORS:
            # Tạo chuỗi log level với màu và căn lề
            colored_level = f"{self.COLORS[levelname]}{levelname:<{self.LEVEL_WIDTH}}{self.COLORS['RESET']}"
        else:
            colored_level = f"{levelname:<{self.LEVEL_WIDTH}}"
        
        # Định dạng thời gian
        time_str = self.formatTime(record, self.datefmt)
        time_part = f"{time_str:<{self.TIME_WIDTH}}"
        
        # Định dạng tên logger, cắt ngắn nếu quá dài
        name_part = f"{record.name:<{self.NAME_WIDTH}}"
        if len(record.name) > self.NAME_WIDTH:
            name_part = f"{record.name[:self.NAME_WIDTH-3]}...:"
        
        # Lấy thông điệp
        message = record.getMessage()
        
        # Tạo thông điệp định dạng theo yêu cầu [log level] [time] [name] [message]
        result = f"{colored_level} {time_part} {name_part} {message}"
        
        return result


def setup_logger(
    name: str, level: LogLevel = LogLevel.INFO, log_file: Optional[str] = None
) -> logging.Logger:
    """Tạo và cấu hình logger với định dạng căn chỉnh

    Args:
        name: Tên của logger
        level: Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Đường dẫn đến file log (nếu muốn lưu log vào file)

    Returns:
        logging.Logger: Logger đã được cấu hình
    """
    # Tạo logger
    logger = logging.getLogger(name)

    # Xóa các handler cũ nếu có
    if logger.handlers:
        logger.handlers.clear()

    # Thiết lập mức độ log
    logger.setLevel(getattr(logging, level))

    # Sử dụng formatter mới với căn chỉnh
    formatter = AlignedColorFormatter(datefmt="%Y-%m-%d %H:%M:%S")

    # Handler cho console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler cho file (nếu có)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        # Sử dụng formatter không màu cho file log
        file_formatter = logging.Formatter(
            fmt="%(levelname)-9s %(asctime)s %(name)-20s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger