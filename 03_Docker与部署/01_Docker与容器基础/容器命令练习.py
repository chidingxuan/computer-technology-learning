"""第03阶段第01课作业：组合并检查基础 Docker 容器命令。"""


def make_image_reference(repository: str, tag: str) -> str:
    """根据镜像仓库名和标签生成 ``repository:tag`` 镜像引用。"""

    repository = repository.strip()
    tag = tag.strip()
    if not repository or not tag:
        raise ValueError("镜像仓库名和标签不能为空")
    return f"{repository}:{tag}"


def parse_port_mapping(mapping: str) -> tuple[int, int]:
    """把 ``宿主机端口:容器端口`` 转换为两个整数。"""

    if mapping.count(":") != 1:
        raise ValueError("端口映射必须只包含一个冒号")

    host_text, container_text = mapping.split(":")
    try:
        host_port = int(host_text)
        container_port = int(container_text)
    except ValueError as error:
        raise ValueError("端口必须是十进制整数") from error

    if not 1 <= host_port <= 65535 or not 1 <= container_port <= 65535:
        raise ValueError("端口必须在1到65535之间")
    return host_port, container_port


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

    image = image.strip()
    container_name = container_name.strip()
    if not image or not container_name:
        raise ValueError("镜像名和容器名不能为空")
    if not 1 <= host_port <= 65535 or not 1 <= container_port <= 65535:
        raise ValueError("端口必须在1到65535之间")

    docker_run = ["docker", "run"]
    if detached:
        docker_run.append("-d")
    if auto_remove:
        docker_run.append("--rm")
    docker_run.extend(
        ["--name", container_name, "-p", f"{host_port}:{container_port}", image]
    )
    return docker_run
