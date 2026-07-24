"""第四课作业：为用户查询函数补充类型标注并完成实现。"""


USERS: list[dict[str, object]] = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Charlie", "active": True},
]


def find_user(user_id: int) -> dict[str,object] | None:
    """根据用户ID返回用户；找不到时返回None。

    要求：
    1. 给参数和返回值添加准确的类型标注。
    2. user_id 必须是整数且不能是 bool，否则抛出 TypeError。
    3. 找到相同 id 的用户时返回该用户字典。
    4. 找不到时返回 None。
    """
    # TODO：请补充类型标注并完成函数
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise TypeError("user_id不是整数")
    for i in range(len(USERS)):
        user = USERS[i]
        if user["id"] == user_id:
            return user
    return None

        


def get_active_names(users: list[dict[str, object]]) -> list[str]:
    """返回所有启用用户的姓名列表。

    要求：
    1. 给参数和返回值添加准确的类型标注。
    2. 使用列表推导式或普通循环均可。
    3. 对本题给定的数据，返回 ["Alice", "Charlie"]。
    """
    # TODO：请补充类型标注并完成函数
    names: list[str] = []
    for i in range(len(users)):
        if users[i]["active"]:
            names.append(users[i]["name"])
    return names


if __name__ == "__main__":
    print(find_user(1))
    print(find_user(999))
    print(get_active_names(USERS))
