"""真实HTTP固定评估：启动服务且完成作业后显式--live；默认不发送请求。"""
import argparse
import json
import time
from urllib.parse import urlparse
from pathlib import Path
import httpx
from assistant_project import evaluate_case


def run_suite(base_url: str) -> list[dict]:
    if urlparse(base_url).hostname not in {'localhost','127.0.0.1'}:
        raise ValueError('本课仅连接本机教学服务')
    cases=json.loads((Path(__file__).parent/'evaluation_cases.json').read_text(encoding='utf-8'))
    rows=[]
    with httpx.Client(base_url=base_url,timeout=180,trust_env=False) as client:
        for case in cases:
            created=client.post('/conversations',json={'title':case['id']})
            created.raise_for_status()
            cid=created.json()['id']; start=time.monotonic()
            response=client.post(f'/assistant/conversations/{cid}/messages',
                json={'question':case['question'],'mode':case['mode']})
            row={'case_id':case['id'],'http_status':response.status_code,
                 'elapsed_seconds':round(time.monotonic()-start,2)}
            if response.status_code==200:
                result=response.json()
                row.update({'result':result,'assessment':evaluate_case(case,result)})
            else:
                row['assessment']={'case_id':case['id'],'passed':False,'failures':['http']}
            rows.append(row)
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true',help='明确允许本机HTTP引发真实模型请求')
    parser.add_argument('--base-url',default='http://127.0.0.1:8008')
    args=parser.parse_args()
    if not args.live:
        print('未联网。完成作业并启动服务后加--live；每次运行会重跑全部6例，可能计费。')
    else:
        report=run_suite(args.base_url)
        print(json.dumps({'cases':report,'passed':sum(r['assessment']['passed'] for r in report),
                          'total':len(report)},ensure_ascii=False,indent=2))
