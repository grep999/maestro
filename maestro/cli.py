import argparse, json, sys
from pathlib import Path
from .engine import Maestro, WorkflowError

def packet(value):
    p=Path(value)
    try: raw=p.read_text(encoding="utf-8") if p.is_file() else value
    except OSError: raw=value
    obj=json.loads(raw)
    if not isinstance(obj,dict): raise WorkflowError("packet must be a JSON object")
    return obj

def main(argv=None):
    p=argparse.ArgumentParser(prog="maestro",description="Project-agnostic workflow orchestration")
    p.add_argument("--db",default=".maestro/state.sqlite3"); s=p.add_subparsers(dest="cmd",required=True)
    x=s.add_parser("start"); x.add_argument("project_id"); x.add_argument("title"); x.add_argument("objective"); x.add_argument("--baseline")
    x=s.add_parser("show"); x.add_argument("wid")
    x=s.add_parser("list"); x.add_argument("--project")
    for cmd in ("ground","deliver","learn"):
        x=s.add_parser(cmd); x.add_argument("wid"); x.add_argument("packet"); x.add_argument("--revision",type=int,required=True)
    for cmd in ("begin-momentum","submit-mastery","unblock"):
        x=s.add_parser(cmd); x.add_argument("wid"); x.add_argument("--revision",type=int,required=True)
    x=s.add_parser("review"); x.add_argument("wid"); x.add_argument("verdict",choices=["PASS","FAIL","BLOCKED","CONDITIONAL"]); x.add_argument("--revision",type=int,required=True); x.add_argument("--findings",default="[]"); x.add_argument("--evidence",default="[]")
    x=s.add_parser("cancel"); x.add_argument("wid"); x.add_argument("reason"); x.add_argument("--revision",type=int,required=True)
    x=s.add_parser("add-work"); x.add_argument("wid"); x.add_argument("title"); x.add_argument("outcome"); x.add_argument("role"); x.add_argument("--acceptance",required=True); x.add_argument("--dependencies",default="[]"); x.add_argument("--revision",type=int,required=True)
    x=s.add_parser("start-work"); x.add_argument("wid"); x.add_argument("item"); x.add_argument("--revision",type=int,required=True)
    x=s.add_parser("complete-work"); x.add_argument("wid"); x.add_argument("item"); x.add_argument("--revision",type=int,required=True); x.add_argument("--evidence",required=True)
    x=s.add_parser("work-items"); x.add_argument("wid")
    x=s.add_parser("assign"); x.add_argument("wid"); x.add_argument("role"); x.add_argument("capability"); x.add_argument("packet")
    x=s.add_parser("assignment"); x.add_argument("aid"); x.add_argument("status",choices=["ACCEPTED","RUNNING","RETURNED","CANCELLED"]); x.add_argument("--result")
    x=s.add_parser("assignments"); x.add_argument("wid")
    x=s.add_parser("events"); x.add_argument("wid")
    a=p.parse_args(argv); e=Maestro(a.db)
    try:
        if a.cmd=="start": out=e.start(a.project_id,a.title,a.objective,a.baseline)
        elif a.cmd=="show": out=e.get(a.wid)
        elif a.cmd=="list": out=e.list(a.project)
        elif a.cmd=="ground": out=e.ground(a.wid,a.revision,packet(a.packet))
        elif a.cmd=="begin-momentum": out=e.begin_momentum(a.wid,a.revision)
        elif a.cmd=="deliver": out=e.deliver(a.wid,a.revision,packet(a.packet))
        elif a.cmd=="submit-mastery": out=e.submit_mastery(a.wid,a.revision)
        elif a.cmd=="review": out=e.review(a.wid,a.revision,a.verdict,json.loads(a.findings),json.loads(a.evidence))
        elif a.cmd=="learn": out=e.learn(a.wid,a.revision,packet(a.packet))
        elif a.cmd=="unblock": out=e.unblock(a.wid,a.revision)
        elif a.cmd=="cancel": out=e.cancel(a.wid,a.revision,a.reason)
        elif a.cmd=="add-work": out=e.add_work_item(a.wid,a.revision,a.title,a.outcome,a.role,json.loads(a.acceptance),json.loads(a.dependencies))
        elif a.cmd=="start-work": out=e.change_work_item(a.wid,a.item,a.revision,"IN_PROGRESS")
        elif a.cmd=="complete-work": out=e.change_work_item(a.wid,a.item,a.revision,"COMPLETED",json.loads(a.evidence))
        elif a.cmd=="work-items": out=e.work_items(a.wid)
        elif a.cmd=="assign": out={"assignment_id":e.assign(a.wid,a.role,a.capability,packet(a.packet))}
        elif a.cmd=="assignment": out=e.assignment_transition(a.aid,a.status,packet(a.result) if a.result else None)
        elif a.cmd=="assignments": out=e.assignments(a.wid)
        elif a.cmd=="events": out=e.events(a.wid)
        print(json.dumps(out,indent=2,default=lambda o:o.__dict__))
        return 0
    except (WorkflowError,ValueError,OSError) as ex:
        print("maestro: "+str(ex),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
