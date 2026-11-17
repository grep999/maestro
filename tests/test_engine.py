import tempfile
import unittest
from pathlib import Path
from maestro.engine import Maestro, WorkflowError

GROUND={"purpose":"deliver an outcome","sources":["brief://source"],"constraints":[],"dependencies":[],"risks":[],"acceptance":["candidate verified"],"next_increment":"build candidate","baseline_ref":"baseline:1"}
MOMENTUM={"candidate_ref":"artifact:candidate-1","outcome":"integrated candidate","changed_artifacts":["artifact:candidate-1"],"checks":[{"name":"smoke","outcome":"passed"}],"risks":[]}
LEARN={"expected_vs_actual":"matched","lessons":["scope was right"],"state_updates":["candidate recorded"],"next_decision":"continue","evidence":["outcome:verified"],"progress":35}

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.e=Maestro(Path(self.tmp.name)/"state.sqlite3")
        self.w=self.e.start("project-a","flow-a","deliver outcome")
    def tearDown(self): self.tmp.cleanup()
    def to_mastery(self):
        w=self.e.ground(self.w["id"],self.w["revision"],GROUND)
        w=self.e.begin_momentum(w["id"],w["revision"])
        w=self.e.deliver(w["id"],w["revision"],MOMENTUM)
        return self.e.submit_mastery(w["id"],w["revision"])
    def test_full_cycle_persists_progress(self):
        w=self.to_mastery()
        self.assertEqual(w["stage"],"MASTERY")
        w=self.e.review(w["id"],w["revision"],"PASS",[],["review:evidence"])
        w=self.e.learn(w["id"],w["revision"],LEARN)
        self.assertEqual((w["stage"],w["cycle"],w["progress"]),("GROUNDING",2,35))
        self.assertEqual(self.e.get(w["id"])["progress"],35)
    def test_momentum_is_stage_not_role(self):
        w=self.e.ground(self.w["id"],0,GROUND)
        w=self.e.begin_momentum(w["id"],w["revision"])
        self.e.assign(w["id"],"BUILDER","implementation",{"deliverable":"candidate"})
        with self.assertRaises(WorkflowError):
            self.e.assign(w["id"],"MOMENTUM","workflow",{})
    def test_fail_returns_to_momentum_and_retains_context(self):
        w=self.to_mastery()
        w=self.e.review(w["id"],w["revision"],"FAIL",[{"finding":"criterion missed"}],[])
        self.assertEqual(w["stage"],"MOMENTUM")
        self.assertEqual(w["packets"]["grounding"],GROUND)
        self.assertEqual(w["packets"]["mastery"]["verdict"],"FAIL")
    def test_blocked_review_can_resume_same_stage(self):
        w=self.to_mastery()
        w=self.e.review(w["id"],w["revision"],"BLOCKED",[{"blocker":"access"}],[])
        self.assertEqual(w["status"],"BLOCKED")
        w=self.e.unblock(w["id"],w["revision"])
        self.assertEqual((w["stage"],w["status"]),("MASTERY","ACTIVE"))
    def test_progress_cannot_move_backwards(self):
        w=self.to_mastery()
        w=self.e.review(w["id"],w["revision"],"PASS",[],["review:evidence"])
        w=self.e.learn(w["id"],w["revision"],LEARN)
        w=self.e.ground(w["id"],w["revision"],GROUND)
        w=self.e.begin_momentum(w["id"],w["revision"])
        w=self.e.deliver(w["id"],w["revision"],MOMENTUM)
        w=self.e.submit_mastery(w["id"],w["revision"])
        w=self.e.review(w["id"],w["revision"],"PASS",[],["review:evidence-2"])
        with self.assertRaises(WorkflowError):
            self.e.learn(w["id"],w["revision"],dict(LEARN,progress=20))
    def test_stage_gate_and_dependencies(self):
        item=self.e.add_work_item(self.w["id"],0,"Ground research","verify sources","RESEARCHER",["source checked"])
        with self.assertRaises(WorkflowError):
            self.e.ground(self.w["id"],1,GROUND)
        w=self.e.change_work_item(self.w["id"],item["id"],1,"IN_PROGRESS")
        w=self.e.change_work_item(self.w["id"],item["id"],w["workflow_revision"],"COMPLETED",["source:verified"])
        w=self.e.ground(self.w["id"],w["workflow_revision"],GROUND)
        self.assertEqual(w["stage"],"GROUNDING")
    def test_independent_flows_share_lifecycle_not_state(self):
        other=self.e.start("project-b","flow-b","different outcome")
        self.assertEqual(other["stage"],"GROUNDING")
        self.e.ground(self.w["id"],0,GROUND)
        self.assertEqual(self.e.get(other["id"])["revision"],0)
    def test_stale_revision_rejected(self):
        self.e.ground(self.w["id"],0,GROUND)
        with self.assertRaises(WorkflowError):
            self.e.begin_momentum(self.w["id"],0)

if __name__=="__main__": unittest.main()
