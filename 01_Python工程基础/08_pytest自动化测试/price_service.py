"""第八课作业：实现一个可测试的价格计算函数。"""


def calculate_total(
    prices: list[int | float],
    discount: int | float = 0,
) -> float:
    """计算商品折扣后的总价。

    要求：
    1. prices必须是列表，否则抛出TypeError。
    2. 每个价格必须是int或float，且不能是bool，否则抛出TypeError。
    3. 每个价格必须大于等于0，否则抛出ValueError。
    4. discount必须是int或float，且不能是bool，否则抛出TypeError。
    5. discount必须在0～1之间，否则抛出ValueError。
    6. 返回sum(prices) * (1 - discount)，并使用round(..., 2)保留两位小数。
    7. 空列表的总价是0.0。
    """
    # TODO：请完成函数
    if not isinstance(prices, list):
        raise TypeError("prices不是列表")

    for i in prices:
        if (not isinstance(i,int) and not isinstance(i, float)) or isinstance(i, bool):
            raise TypeError("prices中元素类型错误")
        if i < 0:
            raise ValueError("prices中元素必须大于等于0")
        
    if (not isinstance(discount,int)and not isinstance(discount, float)) or isinstance(discount, bool):
            raise TypeError("discount必须是int或者float")

    if not (0 <= discount <= 1):
         raise ValueError("discount数值不对")
    if len(prices) == 0:
         return 0.0
    price_sum = sum(prices) * (1 - discount)
    return round(price_sum, 2)
