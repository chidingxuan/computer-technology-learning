"""第七课作业：从环境变量读取应用配置。"""

import logging
import os

from dotenv import load_dotenv


VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings:
    """保存应用运行所需的配置。"""

    def __init__(self, app_name: str, log_level: str, api_key: str):
        self.app_name = app_name
        self.log_level = log_level
        self.api_key = api_key

    def masked_api_key(self) -> str:
        """返回适合日志显示的脱敏密钥。

        要求：
        - 如果密钥长度不超过8，全部返回星号；
        - 否则保留前4位和后4位，中间使用"..."；
        - 例如："abcd12345678wxyz" -> "abcd...wxyz"。
        """
        # TODO：请完成
        pass


def load_settings() -> Settings:
    """读取并验证环境变量。

    要求：
    1. 调用 load_dotenv()，允许从本地.env文件读取配置。
    2. APP_NAME缺省时使用"ai-learning-app"。
    3. LOG_LEVEL缺省时使用"INFO"，并统一转换为大写。
    4. LOG_LEVEL必须属于VALID_LOG_LEVELS，否则抛出ValueError。
    5. LLM_API_KEY必须存在且不是空白字符串，否则抛出RuntimeError。
    6. 返回Settings实例。
    """
    # TODO：请完成
    pass


def configure_logging(log_level: str) -> None:
    """配置根日志记录器。

    要求：
    - 使用logging.basicConfig()；
    - 将字符串日志级别转换为logging中的级别值；
    - 日志格式包含时间、级别和消息。
    """
    # TODO：请完成
    pass


if __name__ == "__main__":
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger(__name__)
    logger.info("应用启动：%s", settings.app_name)
    logger.info("API密钥：%s", settings.masked_api_key())
