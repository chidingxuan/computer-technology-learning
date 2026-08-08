"""第03阶段第01课作业：组合并检查基础 Docker 容器命令。"""


def make_image_reference(repository: str, tag: str) -> str:
    """根据镜像仓库名和标签生成 ``repository:tag`` 镜像引用。"""

    # TODO 1：实现镜像引用生成。
    # repository和tag去除首尾空白后都不能为空，否则抛出ValueError。
    # 返回格式必须是 repository:tag。
    raise NotImplementedError


def parse_port_mapping(mapping: str) -> tuple[int, int]:
    """把 ``宿主机端口:容器端口`` 转换为两个整数。"""

    # TODO 2：实现端口映射解析。
    # 输入必须只包含一个冒号，两侧必须是十进制整数。
    # 两个端口都必须在1到65535之间，不符合要求时抛出ValueError。
    raise NotImplementedError


def build_run_command(
    image: str,
    container_name: str,
    host_port: int,
    container_port: int,
    *,
    detached: bool = True,
    auto_remove: bool = False,
) -> list[str]:
    """返回可交给命令执行器的 ``docker run`` 参数列表。"""

    # TODO 3：实现命令列表生成。
    # 固定开头：docker run
    # detached为True时加入-d；auto_remove为True时加入--rm。
    # 然后依次加入--name、容器名、-p、端口映射，最后放镜像名。
    # image和container_name去除首尾空白后不能为空。
    # 端口必须在1到65535之间，非法输入抛出ValueError。
    raise NotImplementedError
