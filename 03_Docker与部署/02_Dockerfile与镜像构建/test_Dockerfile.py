"""第03阶段第02课Dockerfile作业测试。"""

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

import pytest


LESSON_DIR = Path(__file__).parent
DOCKERFILE = LESSON_DIR / "Dockerfile"
DOCKERIGNORE = LESSON_DIR / ".dockerignore"


def meaningful_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_dockerfile_uses_required_base_image():
    assert "FROM python:3.14-slim" in meaningful_lines(DOCKERFILE)


def test_dockerfile_sets_workdir():
    assert "WORKDIR /app" in meaningful_lines(DOCKERFILE)


def test_dockerfile_copies_only_application_file():
    lines = meaningful_lines(DOCKERFILE)
    assert "COPY status_app.py ." in lines
    assert not any(line in {"COPY . .", "ADD . ."} for line in lines)


def test_dockerfile_exposes_application_port():
    assert "EXPOSE 8000" in meaningful_lines(DOCKERFILE)


def test_dockerfile_uses_exec_form_cmd():
    cmd_lines = [line for line in meaningful_lines(DOCKERFILE) if line.startswith("CMD ")]
    assert len(cmd_lines) == 1
    command = json.loads(cmd_lines[0].removeprefix("CMD "))
    assert command == ["python", "status_app.py"]


@pytest.mark.parametrize("entry", [".git", ".venv", "__pycache__", "*.pyc"])
def test_dockerignore_excludes_local_files(entry):
    assert entry in meaningful_lines(DOCKERIGNORE)


def test_status_app_starts_and_answers_health_request():
    process = subprocess.Popen(
        [sys.executable, "status_app.py"],
        cwd=LESSON_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        for _ in range(30):
            try:
                with urlopen("http://127.0.0.1:8000/health", timeout=0.2) as response:
                    assert response.status == 200
                    assert json.load(response) == {"status": "ok"}
                    break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("status_app.py未能在8000端口启动")
    finally:
        process.terminate()
        process.wait(timeout=3)
