"""练习 01：函数参数与可变对象。"""


def add_tag(tag: str, tags=None):
    """添加一个标签并返回标签列表。

    要求：
    1. 没有传入 tags 时，创建一个新列表。
    2. 传入 tags 时，在调用者传入的列表上添加。
    3. 暂时不要修改函数名。
    """
    # TODO: 请在这里完成代码
    if tags is None:
        tags = []
        tags.append(tag)
        
    else:
        tags.append(tag)
    return tags
 

def add_score(name: str, score: int, scores=None):
    """向成绩字典中写入一条记录并返回字典。

    要求：
    1. 没有传入 scores 时，创建一个新字典。
    2. 传入 scores 时，在调用者传入的字典中写入。
    3. 暂时不用验证参数是否合法。
    """
    # TODO: 请在这里完成代码
    if scores is None:
        scores = {}
        scores[name] = score
        
    else:
        scores[name] = score
    return scores



if __name__ == "__main__":
    first_tags = add_tag("python")
    second_tags = add_tag("fastapi")

    print(first_tags)   # 期望：["python"]
    print(second_tags)  # 期望：["fastapi"]

    existing_tags = ["backend"]
    result_tags = add_tag("api", existing_tags)
    print(existing_tags)  # 期望：["backend", "api"]
    print(result_tags)    # 期望：["backend", "api"]

    first_scores = add_score("Alice", 90)
    second_scores = add_score("Bob", 85)

    print(first_scores)   # 期望：{"Alice": 90}
    print(second_scores)  # 期望：{"Bob": 85}
