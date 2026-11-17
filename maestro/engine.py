"""Persistent, project-agnostic Maestro workflow engine."""
from __future__ import annotations
import json, sqlite3, uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("GROUNDING", "MOMENTUM", "MASTERY", "REPETITION")
ROLES = ("ORCHESTRATOR", "ARCHITECT", "RESEARCHER", "BUILDER", "INDEPENDENT_REVIEWER", "DOMAIN_SPECIALIST")
VERDICTS = ("PASS", "FAIL", "BLOCKED", "CONDITIONAL")

class WorkflowError(Exception):
    pass

def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _dump(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

class Maestro:
    """One durable state machine for any number of independent project flows."""
    def __init__(self, database=".maestro/state.sqlite3"):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workflows(
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, objective TEXT NOT NULL,
              stage TEXT NOT NULL CHECK(stage IN ('GROUNDING','MOMENTUM','MASTERY','REPETITION')),
              status TEXT NOT NULL CHECK(status IN ('ACTIVE','BLOCKED','COMPLETED','CANCELLED')),
              revision INTEGER NOT NULL DEFAULT 0, cycle INTEGER NOT NULL DEFAULT 1,
              progress INTEGER NOT NULL DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
              baseline_ref TEXT, grounding TEXT NOT NULL DEFAULT '{}', momentum TEXT NOT NULL DEFAULT '{}',
              mastery TEXT NOT NULL DEFAULT '{}', repetition TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT, workflow_id TEXT NOT NULL REFERENCES workflows(id),
              revision INTEGER NOT NULL, event_type TEXT NOT NULL, from_stage TEXT, to_stage TEXT,
              actor TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
              BEGIN SELECT RAISE(ABORT,'event history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
              BEGIN SELECT RAISE(ABORT,'event history is append-only'); END;
            CREATE TABLE IF NOT EXISTS work_items(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL REFERENCES workflows(id), stage TEXT NOT NULL,
              title TEXT NOT NULL, outcome TEXT NOT NULL, owner_role TEXT NOT NULL, status TEXT NOT NULL,
              dependencies TEXT NOT NULL, acceptance TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '[]',
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS assignments(
              id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL REFERENCES workflows(id), stage TEXT NOT NULL,
              role TEXT NOT NULL, capability TEXT NOT NULL, status TEXT NOT NULL,
              packet TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            """)
            cols = {r[1] for r in db.execute("PRAGMA table_info(workflows)")}
            if "cycle" not in cols:
                db.execute("ALTER TABLE workflows ADD COLUMN cycle INTEGER NOT NULL DEFAULT 1")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.database, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        cur = db.execute("PRAGMA journal_mode=WAL"); cur.close()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _event(self, db, wid, rev, kind, old, new, actor, payload):
        db.execute("INSERT INTO events(workflow_id,revision,event_type,from_stage,to_stage,actor,payload,created_at) VALUES(?,?,?,?,?,?,?,?)",
                   (wid,rev,kind,old,new,actor,_dump(payload),_now()))

    def get(self, wid):
        with self._db() as db:
            r = db.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
        if not r: raise WorkflowError("unknown workflow: " + wid)
        return self._snapshot(r)

    def _snapshot(self, r):
        return {"id":r["id"],"project_id":r["project_id"],"title":r["title"],"objective":r["objective"],
                "stage":r["stage"],"status":r["status"],"revision":r["revision"],"cycle":r["cycle"],
                "progress":r["progress"],"baseline_ref":r["baseline_ref"],
                "packets":{k:json.loads(r[k]) for k in ("grounding","momentum","mastery","repetition")},
                "created_at":r["created_at"],"updated_at":r["updated_at"]}

    def list(self, project_id=None):
        with self._db() as db:
            rows = db.execute("SELECT * FROM workflows"+(" WHERE project_id=?" if project_id else "")+" ORDER BY updated_at DESC",
                              (project_id,) if project_id else ()).fetchall()
        return [self._snapshot(r) for r in rows]

    def start(self, project_id, title, objective, baseline_ref=None, actor="human"):
        if not all(isinstance(x,str) and x.strip() for x in (project_id,title,objective)):
            raise WorkflowError("project_id, title and objective are required")
        wid, stamp = str(uuid.uuid4()), _now()
        with self._db() as db:
            db.execute("INSERT INTO workflows(id,project_id,title,objective,stage,status,baseline_ref,created_at,updated_at) VALUES(?,?,?,?,'GROUNDING','ACTIVE',?,?,?)",
                       (wid,project_id,title,objective,baseline_ref,stamp,stamp))
            self._event(db,wid,0,"WORKFLOW_STARTED",None,"GROUNDING",actor,{"objective":objective})
        return self.get(wid)

    def _mutate(self,wid,rev,actor,kind,payload,stage=None,status=None,progress=None,cycle=None,packet=None,baseline_ref=None):
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r=db.execute("SELECT * FROM workflows WHERE id=?",(wid,)).fetchone()
            if not r: raise WorkflowError("unknown workflow: "+wid)
            if r["revision"]!=rev: raise WorkflowError(f"stale revision: expected {rev}, current {r['revision']}")
            if r["status"] in ("COMPLETED","CANCELLED"): raise WorkflowError("workflow is "+r["status"])
            old=r["stage"]; new=stage or old; n=rev+1
            fields={"stage":new,"status":status or r["status"],"progress":r["progress"] if progress is None else progress,
                    "cycle":r["cycle"] if cycle is None else cycle,"updated_at":_now()}
            if packet: fields[packet[0]]= _dump(packet[1])
            if baseline_ref is not None: fields["baseline_ref"]=baseline_ref
            sql="UPDATE workflows SET "+",".join(k+"=?" for k in fields)+" ,revision=? WHERE id=? AND revision=?"
            cur=db.execute(sql,tuple(fields.values())+(n,wid,rev))
            if cur.rowcount!=1: raise WorkflowError("concurrent update; reload workflow")
            self._event(db,wid,n,kind,old,new,actor,payload)
        return self.get(wid)

    def _stage_clear(self,wid,stage):
        with self._db() as db:
            rows=db.execute("SELECT title,status FROM work_items WHERE workflow_id=? AND stage=?",(wid,stage)).fetchall()
        pending=[f"{r['title']} ({r['status']})" for r in rows if r["status"]!="COMPLETED"]
        if pending: raise WorkflowError("incomplete "+stage+" work items: "+"; ".join(pending))

    def ground(self,wid,rev,p,actor="orchestrator"):
        keys=("purpose","sources","constraints","dependencies","risks","acceptance","next_increment")
        missing=[k for k in keys if k not in p or p[k] is None]
        if missing: raise WorkflowError("grounding packet missing: "+", ".join(missing))
        for k in ("sources","constraints","dependencies","risks","acceptance"):
            if not isinstance(p[k],list): raise WorkflowError(k+" must be a list")
        if not p["sources"] or not p["acceptance"] or not p["purpose"] or not p["next_increment"]:
            raise WorkflowError("grounding requires purpose, sources, acceptance and next increment")
        self._stage_clear(wid,"GROUNDING")
        w=self.get(wid)
        if w["stage"]!="GROUNDING": raise WorkflowError("ground only in GROUNDING")
        return self._mutate(wid,rev,actor,"GROUNDING_ACCEPTED",p,packet=("grounding",p),baseline_ref=p.get("baseline_ref"))

    def begin_momentum(self,wid,rev,actor="orchestrator"):
        w=self.get(wid)
        if w["stage"]!="GROUNDING" or not w["packets"]["grounding"]: raise WorkflowError("Momentum requires Grounding")
        self._stage_clear(wid,"GROUNDING")
        return self._mutate(wid,rev,actor,"MOMENTUM_BEGAN",{"increment":w["packets"]["grounding"]["next_increment"]},stage="MOMENTUM")

    def deliver(self,wid,rev,p,actor="builder"):
        for k in ("candidate_ref","outcome","changed_artifacts","checks","risks"):
            if k not in p or p[k] is None: raise WorkflowError("Momentum packet missing: "+k)
        if not p["candidate_ref"] or not p["outcome"]: raise WorkflowError("candidate_ref and outcome required")
        for k in ("changed_artifacts","checks","risks"):
            if not isinstance(p[k],list): raise WorkflowError(k+" must be a list")
        for c in p["checks"]:
            if not isinstance(c,dict) or not c.get("name") or c.get("outcome") not in ("passed","failed","skipped","not_run"):
                raise WorkflowError("each check needs a name and valid outcome")
        w=self.get(wid)
        if w["stage"]!="MOMENTUM": raise WorkflowError("deliver only in MOMENTUM")
        return self._mutate(wid,rev,actor,"MOMENTUM_DELIVERED",p,packet=("momentum",p))

    def submit_mastery(self,wid,rev,actor="orchestrator"):
        w=self.get(wid)
        if w["stage"]!="MOMENTUM" or not w["packets"]["momentum"]: raise WorkflowError("Mastery requires Momentum candidate")
        self._stage_clear(wid,"MOMENTUM")
        p={"candidate_ref":w["packets"]["momentum"]["candidate_ref"],"acceptance":w["packets"]["grounding"]["acceptance"]}
        return self._mutate(wid,rev,actor,"MASTERY_SUBMITTED",p,stage="MASTERY")

    def review(self,wid,rev,verdict,findings,evidence,actor="independent_reviewer"):
        v=verdict.upper()
        if v not in VERDICTS: raise WorkflowError("invalid Mastery verdict")
        if not isinstance(findings,list) or not isinstance(evidence,list): raise WorkflowError("findings/evidence must be lists")
        w=self.get(wid)
        if w["stage"]!="MASTERY": raise WorkflowError("review only in MASTERY")
        self._stage_clear(wid,"MASTERY")
        if v in ("PASS","CONDITIONAL") and not evidence: raise WorkflowError("accepted verdict requires evidence")
        if v=="PASS":
            bad=[c.get("name","unnamed") for c in w["packets"]["momentum"].get("checks",[]) if c.get("required",True) and c.get("outcome")!="passed"]
            if bad: raise WorkflowError("required Momentum checks not passed: "+", ".join(bad))
        p={"verdict":v,"findings":findings,"evidence":evidence,"candidate_ref":w["packets"]["momentum"]["candidate_ref"]}
        if v=="FAIL":
            if not findings: raise WorkflowError("FAIL requires findings")
            return self._mutate(wid,rev,actor,"MASTERY_FAILED",p,stage="MOMENTUM",packet=("mastery",p))
        if v=="BLOCKED":
            if not findings: raise WorkflowError("BLOCKED requires blocker")
            return self._mutate(wid,rev,actor,"MASTERY_BLOCKED",p,status="BLOCKED",packet=("mastery",p))
        return self._mutate(wid,rev,actor,"MASTERY_REVIEWED",p,stage="REPETITION",packet=("mastery",p))

    def learn(self,wid,rev,p,actor="orchestrator"):
        for k in ("expected_vs_actual","lessons","state_updates","next_decision","evidence"):
            if k not in p or p[k] is None: raise WorkflowError("Repetition packet missing: "+k)
        if not p["evidence"] or not isinstance(p["lessons"],list) or not isinstance(p["state_updates"],list):
            raise WorkflowError("Repetition requires lessons, state updates and evidence")
        w=self.get(wid)
        if w["stage"]!="REPETITION": raise WorkflowError("learn only in REPETITION")
        self._stage_clear(wid,"REPETITION")
        complete=p.get("objective_complete",False)
        progress=p.get("progress",w["progress"])
        if not isinstance(complete,bool) or not isinstance(progress,int) or not 0<=progress<=100: raise WorkflowError("invalid completion/progress")
        if progress<w["progress"]: raise WorkflowError("objective progress cannot move backwards")
        if complete and progress not in (w["progress"],100): raise WorkflowError("completed objective progress must be 100")
        return self._mutate(wid,rev,actor,"WORKFLOW_COMPLETED" if complete else "CYCLE_LEARNED",p,
            stage="REPETITION" if complete else "GROUNDING",status="COMPLETED" if complete else "ACTIVE",
            progress=100 if complete else progress,cycle=w["cycle"] if complete else w["cycle"]+1,packet=("repetition",p))

    def unblock(self,wid,rev,actor="orchestrator"):
        w=self.get(wid)
        if w["status"]!="BLOCKED": raise WorkflowError("workflow is not blocked")
        return self._mutate(wid,rev,actor,"WORKFLOW_UNBLOCKED",{},status="ACTIVE")

    def cancel(self,wid,rev,reason,actor="human"):
        if not reason.strip(): raise WorkflowError("cancellation requires reason")
        return self._mutate(wid,rev,actor,"WORKFLOW_CANCELLED",{"reason":reason},status="CANCELLED")

    def add_work_item(self,wid,rev,title,outcome,owner_role,acceptance,dependencies=None):
        role=owner_role.upper(); deps=dependencies or []
        if role not in ROLES or not title.strip() or not outcome.strip() or not acceptance: raise WorkflowError("invalid work item")
        w=self.get(wid)
        if w["status"]!="ACTIVE": raise WorkflowError("workflow is not active")
        allowed={"ARCHITECT":{"GROUNDING","MOMENTUM"},"RESEARCHER":{"GROUNDING","MOMENTUM","MASTERY"},
                 "BUILDER":{"MOMENTUM"},"INDEPENDENT_REVIEWER":{"MASTERY"},"DOMAIN_SPECIALIST":set(STAGES),"ORCHESTRATOR":set(STAGES)}
        if w["stage"] not in allowed[role]: raise WorkflowError(f"{role} not allowed in {w['stage']}")
        iid,stamp=str(uuid.uuid4()),_now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            f=db.execute("SELECT * FROM workflows WHERE id=?",(wid,)).fetchone()
            if f["revision"]!=rev: raise WorkflowError("stale revision")
            known={r[0] for r in db.execute("SELECT id FROM work_items WHERE workflow_id=?",(wid,))}
            if set(deps)-known: raise WorkflowError("unknown dependency")
            db.execute("INSERT INTO work_items VALUES(?,?,?,?,?,?,'READY',?,?, '[]',?,?)",
                       (iid,wid,w["stage"],title,outcome,role,_dump(deps),_dump(acceptance),stamp,stamp))
            n=rev+1; db.execute("UPDATE workflows SET revision=?,updated_at=? WHERE id=?",(n,stamp,wid))
            self._event(db,wid,n,"WORK_ITEM_CREATED",w["stage"],w["stage"],"orchestrator",{"id":iid,"title":title})
        return {"id":iid,"workflow_revision":n,"stage":w["stage"]}

    def change_work_item(self,wid,iid,rev,status,evidence=None):
        evidence=evidence or []; stamp=_now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            f=db.execute("SELECT * FROM workflows WHERE id=?",(wid,)).fetchone()
            if not f or f["revision"]!=rev: raise WorkflowError("unknown workflow or stale revision")
            item=db.execute("SELECT * FROM work_items WHERE id=? AND workflow_id=?",(iid,wid)).fetchone()
            if not item or item["stage"]!=f["stage"]: raise WorkflowError("unknown or stale work item")
            allowed={"READY":"IN_PROGRESS","IN_PROGRESS":"COMPLETED"}
            if allowed.get(item["status"])!=status: raise WorkflowError("invalid work-item transition")
            if status=="IN_PROGRESS":
                deps=json.loads(item["dependencies"])
                for dep in deps:
                    r=db.execute("SELECT status FROM work_items WHERE id=? AND workflow_id=?",(dep,wid)).fetchone()
                    if not r or r["status"]!="COMPLETED": raise WorkflowError("work-item dependency incomplete")
            if status=="COMPLETED" and not evidence: raise WorkflowError("completion requires evidence")
            n=rev+1; db.execute("UPDATE work_items SET status=?,evidence=?,updated_at=? WHERE id=?",(status,_dump(evidence),stamp,iid))
            db.execute("UPDATE workflows SET revision=?,updated_at=? WHERE id=?",(n,stamp,wid))
            self._event(db,wid,n,"WORK_ITEM_"+status,f["stage"],f["stage"],"human",{"id":iid,"evidence":evidence})
        return {"id":iid,"status":status,"workflow_revision":n}

    def work_items(self,wid):
        with self._db() as db: rows=db.execute("SELECT * FROM work_items WHERE workflow_id=? ORDER BY created_at",(wid,)).fetchall()
        return [{"id":r["id"],"stage":r["stage"],"title":r["title"],"outcome":r["outcome"],"owner_role":r["owner_role"],
                 "status":r["status"],"dependencies":json.loads(r["dependencies"]),"acceptance":json.loads(r["acceptance"]),
                 "evidence":json.loads(r["evidence"])} for r in rows]

    def _stage_clear(self,wid,stage):
        with self._db() as db: rows=db.execute("SELECT title,status FROM work_items WHERE workflow_id=? AND stage=?",(wid,stage)).fetchall()
        todo=[r["title"] for r in rows if r["status"]!="COMPLETED"]
        if todo: raise WorkflowError("incomplete "+stage+" work: "+", ".join(todo))

    def assign(self,wid,role,capability,packet):
        role=role.upper(); w=self.get(wid)
        allowed={"ARCHITECT":{"GROUNDING","MOMENTUM"},"RESEARCHER":{"GROUNDING","MOMENTUM","MASTERY"},
                 "BUILDER":{"MOMENTUM"},"INDEPENDENT_REVIEWER":{"MASTERY"},"DOMAIN_SPECIALIST":set(STAGES)}
        if role not in allowed or w["stage"] not in allowed[role] or w["status"]!="ACTIVE": raise WorkflowError("role not allowed in current stage")
        aid,stamp=str(uuid.uuid4()),_now()
        dispatch={"workflow_id":wid,"project_id":w["project_id"],"stage":w["stage"],"workflow_revision":w["revision"],
                  "role":role,"capability":capability,"expected_output":packet,"permission_boundary":"least_privilege"}
        with self._db() as db:
            db.execute("INSERT INTO assignments VALUES(?,?,?,?,?,'PROPOSED',?,?,?)",(aid,wid,w["stage"],role,capability,_dump(dispatch),stamp,stamp))
            self._event(db,wid,w["revision"],"ASSIGNMENT_PROPOSED",w["stage"],w["stage"],"orchestrator",{"id":aid,"role":role})
        return aid

    def assignment_transition(self,aid,status,result=None):
        transitions={"PROPOSED":{"ACCEPTED","CANCELLED"},"ACCEPTED":{"RUNNING","CANCELLED"},"RUNNING":{"RETURNED"}}
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            a=db.execute("SELECT * FROM assignments WHERE id=?",(aid,)).fetchone()
            if not a or status not in transitions.get(a["status"],set()): raise WorkflowError("invalid assignment transition")
            w=db.execute("SELECT * FROM workflows WHERE id=?",(a["workflow_id"],)).fetchone(); p=json.loads(a["packet"])
            if w["stage"]!=a["stage"] or w["status"]!="ACTIVE" or w["revision"]!=p["workflow_revision"]: raise WorkflowError("stale assignment")
            if status=="RETURNED":
                if not result or not result.get("summary") or "evidence" not in result: raise WorkflowError("return requires summary and evidence")
                p["result"]=result
            stamp=_now(); db.execute("UPDATE assignments SET status=?,packet=?,updated_at=? WHERE id=?",(status,_dump(p),stamp,aid))
            self._event(db,a["workflow_id"],w["revision"],"ASSIGNMENT_"+status,a["stage"],a["stage"],"orchestrator",{"id":aid})
        return {"id":aid,"status":status,"packet":p}

    def assignments(self,wid):
        with self._db() as db: rows=db.execute("SELECT * FROM assignments WHERE workflow_id=? ORDER BY created_at",(wid,)).fetchall()
        return [{"id":r["id"],"stage":r["stage"],"role":r["role"],"capability":r["capability"],"status":r["status"],"packet":json.loads(r["packet"])} for r in rows]

    def events(self,wid):
        with self._db() as db: rows=db.execute("SELECT * FROM events WHERE workflow_id=? ORDER BY seq",(wid,)).fetchall()
        return [{"seq":r["seq"],"revision":r["revision"],"type":r["event_type"],"from":r["from_stage"],"to":r["to_stage"],
                 "actor":r["actor"],"payload":json.loads(r["payload"]),"created_at":r["created_at"]} for r in rows]
