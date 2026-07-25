"""第六课练习：检查程序运行时使用的Python和第三方依赖。"""

import sys

import requests


def environment_info() -> dict[str, str]:
    """返回当前Python解释器及requests版本信息。

    TODO：
    返回下面结构，不要把实际路径和版本号写死：

    {
        "python_executable": 当前Python解释器路径,
        "requests_version": 当前requests版本,
    }

    提示：
    - 当前解释器路径：sys.executable
    - requests版本：requests.__version__
    """
    pass


if __name__ == "__main__":
    info = environment_info()
    print("Python解释器：", info["python_executable"])
    print("requests版本：", info["requests_version"])
