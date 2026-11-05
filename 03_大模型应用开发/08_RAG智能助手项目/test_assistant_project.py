"""学生核心测试：路由编排、成功提交、固定评估。无网络和真实密钥。"""
from copy import deepcopy
import pytest
from assistant_project import run_request, save_exchange, evaluate_case
from project_support import REGISTRY, ALLOWED_NAMES


def never(*args, **kwargs):
    pytest.fail('不应调用另一条路径或无必要的外部服务')


def call(name='get_devices', raw='{"room_id":"room-a"}', cid='c1'):
    return {'id': cid, 'type': 'function', 'function': {'name': name, 'arguments': raw}}


def scripted(replies):
    seen = []
    def ask(messages):
        seen.append(deepcopy(messages))
        assert len(seen) <= len(replies), '不应多问模型或自动重试'
        return deepcopy(replies[len(seen)-1])
    return ask, seen


def test_rag_only_retrieves_and_generates_once():
    seen = []
    hits = [{'id': 'r1', 'source': 'rule.md#p1', 'text': '提前预约', 'score': 1.0}]
    def retrieve(q):
        seen.append(q)
        return hits
    def generate(messages):
        seen.append(messages)
        return {'status': 'answered', 'answer': '需提前预约。', 'citations': ['r1']}
    result = run_request('预约？', 'rag', retrieve, generate, never, {}, set())
    assert len(seen) == 2
    assert result == {'mode':'rag','status':'answered','answer':'需提前预约。',
        'sources':[{'id':'r1','source':'rule.md#p1'}], 'model_calls':1,'tool_calls':0}


def test_empty_retrieval_makes_zero_model_calls():
    result = run_request('未知', 'rag', lambda q: [], never, never, {}, set())
    assert result['status'] == 'no_evidence' and result['sources'] == []
    assert result['model_calls'] == result['tool_calls'] == 0


@pytest.mark.parametrize('reply,status', [
    ({'status':'no_answer','answer':'资料不足','citations':[]}, 'no_answer'),
    ({'status':'answered','answer':'编造','citations':['invented']}, 'invalid_citations'),
])
def test_rag_preserves_guard_result(reply, status):
    hits = [{'id':'r1','text':'规则','source':'r.md#p1'}]
    result = run_request('问题', 'rag', lambda q:hits, lambda m:reply, never, {}, set())
    assert result['status'] == status and result['sources'] == []
    assert result['model_calls'] == 1


def test_tool_reuses_loop_and_does_not_retrieve():
    ask, seen = scripted([
        {'role':'assistant','content':None,'tool_calls':[call()]},
        {'role':'assistant','content':'24台','tool_calls':[]},
    ])
    result = run_request('设备？','tool',never,never,ask,REGISTRY,ALLOWED_NAMES)
    assert result == {'mode':'tool','status':'complete','answer':'24台',
                      'sources':[], 'model_calls':2, 'tool_calls':1}
    assert seen[1][-1]['tool_call_id'] == 'c1'
    assert 'messages' not in result, '内部工具轨迹不直接作为公开响应'


@pytest.mark.parametrize('registered,error', [(False,'unknown_tool'),(True,'not_allowed')])
def test_tool_unknown_or_denied_never_executes(registered,error):
    registry={'delete_room':never} if registered else {}
    ask,seen=scripted([
        {'role':'assistant','content':None,'tool_calls':[call('delete_room','{}')]},
        {'role':'assistant','content':'操作未执行。','tool_calls':[]},
    ])
    result=run_request('删除？','tool',never,never,ask,registry,set())
    import json
    assert json.loads(seen[1][-1]['content'])=={'ok':False,'error':error}
    assert result['tool_calls']==1 and result['model_calls']==2


@pytest.mark.parametrize('budget,status,model_count', [(0,'step_limit',0),(1,'step_limit',1),(4,'repeated_call',2)])
def test_tool_preserves_stop_and_counts(budget,status,model_count):
    ask, _ = scripted([{'role':'assistant','content':None,'tool_calls':[call()]},
                      {'role':'assistant','content':None,'tool_calls':[call(cid='new')]}])
    result = run_request('设备？','tool',never,never,ask,REGISTRY,ALLOWED_NAMES,budget)
    assert result['status']==status and result['answer']=='' and result['sources']==[]
    assert result['model_calls']==model_count


@pytest.mark.parametrize('mode', ['rag','tool'])
def test_model_failure_propagates(mode):
    def fail(*args): raise TimeoutError('私有细节')
    with pytest.raises(TimeoutError):
        run_request('问题',mode,lambda q:[{'id':'r','text':'原文','source':'r.md'}],fail,fail,{},set())


@pytest.mark.parametrize('status', ['answered','complete'])
def test_save_success_once(status):
    seen=[]
    result={'status':status,'answer':'结果'}
    before=deepcopy(result)
    assert save_exchange(7,'问题',result,lambda *args:seen.append(args)) is True
    assert seen==[(7,'问题','结果')] and result==before


@pytest.mark.parametrize('status', ['no_evidence','no_answer','invalid_citations','step_limit','repeated_call'])
def test_non_success_does_not_save(status):
    assert save_exchange(7,'问题',{'status':status,'answer':'有文字也不算成功'},never) is False


def test_empty_success_does_not_save():
    assert save_exchange(7,'问题',{'status':'complete','answer':'  '},never) is False


def test_storage_failure_is_not_reported_success():
    def fail(*args): raise OSError('数据库失败')
    with pytest.raises(OSError):
        save_exchange(7,'问题',{'status':'answered','answer':'结果'},fail)


CASE={'id':'e1','expected_status':'answered','must_include':['17:00'],
      'expected_source_ids':['r1'],'max_model_calls':1}
RESULT={'status':'answered','answer':'17:00前提交','sources':[{'id':'r1','source':'r.md#p1'}],
        'model_calls':1,'tool_calls':0}


def test_evaluation_passes_fixed_case_without_mutation():
    before=deepcopy((CASE,RESULT))
    assert evaluate_case(CASE,RESULT)=={'case_id':'e1','passed':True,'failures':[]}
    assert (CASE,RESULT)==before


@pytest.mark.parametrize('change,failure', [
    ({'status':'no_answer'},'status'), ({'answer':'可随时提交'},'answer'),
    ({'sources':[{'id':'r2','source':'r.md'}]},'sources'), ({'model_calls':2},'budget'),
])
def test_evaluation_locates_each_failure(change,failure):
    assert evaluate_case(CASE,{**RESULT,**change})=={'case_id':'e1','passed':False,'failures':[failure]}


def test_evaluation_reports_all_failures_in_order():
    result={**RESULT,'status':'no_answer','answer':'其他','sources':[],'model_calls':9}
    assert evaluate_case(CASE,result)['failures']==['status','answer','sources','budget']


def test_evaluation_sources_are_set_comparison():
    case={**CASE,'expected_source_ids':['r2','r1']}
    result={**RESULT,'sources':[{'id':'r1','source':'a'},{'id':'r2','source':'b'},{'id':'r1','source':'a'}]}
    assert evaluate_case(case,result)['passed'] is True
