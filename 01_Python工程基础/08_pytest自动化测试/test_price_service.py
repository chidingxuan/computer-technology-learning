"""第八课作业：price_service的自动化测试。"""

import pytest

from price_service import calculate_total


def test_calculate_total_without_discount():
    """普通价格求和。"""
    assert calculate_total([10, 20, 30]) == 60.0


def test_calculate_total_with_discount():
    """应用折扣。"""
    assert calculate_total([100, 50], discount=0.2) == 120.0


def test_calculate_total_empty_prices():
    """空列表。"""
    assert calculate_total([]) == 0.0


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 100.0),
        (0.25, 75.0),
        (1, 0.0),
    ],
)
def test_calculate_total_discount_cases(discount, expected):
    """使用一组数据重复测试折扣边界。"""
    assert calculate_total([100], discount=discount) == expected


def test_calculate_total_rejects_negative_price():
    """负数价格应该抛出ValueError。"""
    with pytest.raises(ValueError):
        calculate_total([10, -1])


# TODO：请自己补充至少三个测试：
# 1. prices不是列表时抛出TypeError；
# 2. price是True时抛出TypeError；
# 3. discount大于1时抛出ValueError。
