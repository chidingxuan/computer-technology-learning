"""第03阶段第01课作业测试。"""

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).with_name("容器命令练习.py")
SPEC = importlib.util.spec_from_file_location("container_command_exercise", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
exercise = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exercise)


@pytest.mark.parametrize(
    ("repository", "tag", "expected"),
    [
        ("python", "3.14-slim", "python:3.14-slim"),
        ("library/nginx", "stable", "library/nginx:stable"),
        ("  demo-api  ", "  v1  ", "demo-api:v1"),
    ],
)
def test_make_image_reference(repository, tag, expected):
    assert exercise.make_image_reference(repository, tag) == expected


@pytest.mark.parametrize(
    ("repository", "tag"),
    [("", "latest"), ("python", ""), ("   ", "v1"), ("demo", "   ")],
)
def test_make_image_reference_rejects_blank_parts(repository, tag):
    with pytest.raises(ValueError):
        exercise.make_image_reference(repository, tag)


@pytest.mark.parametrize(
    ("mapping", "expected"),
    [("8000:8000", (8000, 8000)), ("8080:80", (8080, 80)), ("1:65535", (1, 65535))],
)
def test_parse_port_mapping(mapping, expected):
    assert exercise.parse_port_mapping(mapping) == expected


@pytest.mark.parametrize(
    "mapping",
    ["8000", "8000:80:8", "left:80", "8000:right", "0:80", "8000:65536"],
)
def test_parse_port_mapping_rejects_invalid_input(mapping):
    with pytest.raises(ValueError):
        exercise.parse_port_mapping(mapping)


def test_build_run_command_default_options():
    assert exercise.build_run_command("demo-api:v1", "demo", 8080, 8000) == [
        "docker",
        "run",
        "-d",
        "--name",
        "demo",
        "-p",
        "8080:8000",
        "demo-api:v1",
    ]


def test_build_run_command_auto_remove_and_foreground():
    assert exercise.build_run_command(
        "hello-world:latest",
        "hello-demo",
        9000,
        80,
        detached=False,
        auto_remove=True,
    ) == [
        "docker",
        "run",
        "--rm",
        "--name",
        "hello-demo",
        "-p",
        "9000:80",
        "hello-world:latest",
    ]


def test_build_run_command_supports_both_flags():
    command = exercise.build_run_command(
        "demo:v2", "demo-2", 3000, 3000, detached=True, auto_remove=True
    )
    assert command[:4] == ["docker", "run", "-d", "--rm"]
    assert command[-1] == "demo:v2"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"image": "", "container_name": "demo", "host_port": 8000, "container_port": 80},
        {"image": "demo", "container_name": " ", "host_port": 8000, "container_port": 80},
        {"image": "demo", "container_name": "demo", "host_port": 0, "container_port": 80},
        {"image": "demo", "container_name": "demo", "host_port": 8000, "container_port": 70000},
    ],
)
def test_build_run_command_rejects_invalid_input(kwargs):
    with pytest.raises(ValueError):
        exercise.build_run_command(**kwargs)


def test_build_run_command_does_not_execute_docker(monkeypatch):
    """作业只生成参数列表，不能在测试过程中启动真实容器。"""

    def fail_if_called(*args, **kwargs):
        raise AssertionError("build_run_command不应执行外部命令")

    monkeypatch.setattr("subprocess.run", fail_if_called)
    result = exercise.build_run_command("demo:v1", "demo", 8080, 80)
    assert result[-1] == "demo:v1"
