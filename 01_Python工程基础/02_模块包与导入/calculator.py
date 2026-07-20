"""一个用于学习模块导入的简单计算器模块。"""


PI = 3.14159


def add(left: float, right: float) -> float:
    """返回两个数的和。"""
    return left + right


def circle_area(radius: float) -> float:
    """返回圆的面积。"""
    return PI * radius**2


if __name__ == "__main__":
    print("calculator.py 被直接运行")
    print(add(2, 3))
