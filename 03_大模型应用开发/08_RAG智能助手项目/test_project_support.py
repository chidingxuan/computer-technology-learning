"""教师接线回归：不把HTTP成功冒充模型质量；全部离线。"""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import pytest
from fastapi.testclient import TestClient
import assistant_project as hw
from project_api import create_app, AskBody
from project_support import store_pair, retrieve_lab


@contextmanager
def no_network_ports():
    class Ports:
        def generate(self,*args): pytest.fail('教师HTTP测试不得联网')
        def ask(self,*args): pytest.fail('教师HTTP测试不得联网')
    yield Ports()


def test_old_health_and_conversation_routes_survive(tmp_path):
    with TestClient(create_app(tmp_path/'test.sqlite3',no_network_ports)) as client:
        assert client.get('/health').json()['status']=='ok'
        response=client.post('/conversations',json={'title':'实验记录'})
        assert response.status_code==201 and response.json()['id']==1
        assert client.get('/conversations/1/messages').json()==[]


@pytest.mark.parametrize('body', [
    {'question':'问题','mode':'unknown'}, {'question':'问题','mode':None},
    {'mode':'rag'}, {'question':'问题','allowed_names':['delete_room']},
])
def test_invalid_body_rejected_before_service(tmp_path,monkeypatch,body):
    monkeypatch.setattr(hw,'run_request',lambda *a,**k:pytest.fail('不应进入服务层'))
    with TestClient(create_app(tmp_path/'test.sqlite3',no_network_ports)) as client:
        assert client.post('/assistant/conversations/1/messages',json=body).status_code==422


def test_unknown_conversation_is_404(tmp_path):
    with TestClient(create_app(tmp_path/'test.sqlite3',no_network_ports)) as client:
        assert client.post('/assistant/conversations/9/messages',json={'question':'问题'}).status_code==404


def test_todo_is_501_not_missing_environment(tmp_path,monkeypatch):
    def todo(*args,**kwargs): raise NotImplementedError
    monkeypatch.setattr(hw,'run_request',todo)
    with TestClient(create_app(tmp_path/'test.sqlite3',no_network_ports)) as client:
        client.post('/conversations',json={'title':'测试'})
        r=client.post('/assistant/conversations/1/messages',json={'question':'问题'})
        assert r.status_code==501


def test_upstream_error_is_502_without_private_detail(tmp_path,monkeypatch):
    def fail(*a,**k): raise TimeoutError('secret upstream detail')
    monkeypatch.setattr(hw,'run_request',fail)
    with TestClient(create_app(tmp_path/'test.sqlite3',no_network_ports)) as client:
        client.post('/conversations',json={'title':'测试'})
        r=client.post('/assistant/conversations/1/messages',json={'question':'问题'})
        assert r.status_code==502 and 'secret' not in r.text
        assert client.get('/conversations/1/messages').json()==[]


def test_pair_transaction_rolls_back_both_rows(tmp_path):
    path=tmp_path/'test.sqlite3'
    with TestClient(create_app(path,no_network_ports)) as client:
        client.post('/conversations',json={'title':'测试'})
        with pytest.raises(sqlite3.IntegrityError): store_pair(path,1,'问题','长'*2001)
        assert client.get('/conversations/1/messages').json()==[]


def test_two_apps_do_not_touch_old_database(tmp_path):
    a,b=tmp_path/'a.sqlite3',tmp_path/'b.sqlite3'
    with TestClient(create_app(a,no_network_ports)) as client:
        client.post('/conversations',json={'title':'仅A'})
    with TestClient(create_app(b,no_network_ports)) as client:
        assert client.get('/conversations').json()==[]


def test_lexical_baseline_and_known_unknown_are_explicit():
    assert retrieve_lab('实验预约须在什么时候提交？')[0]['id']=='rules-p1'
    assert retrieve_lab('量子企鹅住在火星哪里？')==[]


def test_mode_omitted_defaults_rag():
    assert AskBody(question='问题').mode=='rag'
