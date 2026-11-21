import sqlite3
import tempfile
import unittest
from pathlib import Path

from maestro import __version__, cli
from maestro.adapters import AssignmentPacket, EchoAdapter, get_registry
from maestro.checks import CheckSpec, GateRunner
from maestro.coding import coding_seed_work, coding_start
from maestro.engine import Maestro, WorkflowError

GROUND = {
    "purpose": "deliver an outcome",
    "sources": ["brief://source"],
    "constraints": [],
    "dependencies": [],
    "risks": [],
    "acceptance": ["candidate verified"],
    "next_increment": "build candidate",
    "baseline_ref": "baseline:1",
}
MOMENTUM = {
    "candidate_ref": "artifact:candidate-1",
    "outcome": "integrated candidate",
    "changed_artifacts": ["artifact:candidate-1"],
    "checks": [{"name": "smoke", "outcome": "passed"}],
    "risks": [],
}
LEARN = {
    "expected_vs_actual": "matched",
    "lessons": ["scope was right"],
    "state_updates": ["candidate recorded"],
    "next_decision": "continue",
    "evidence": ["outcome:verified"],
    "progress": 35,
}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "state.sqlite3"
        self.e = Maestro(self.db_path)
        self.w = self.e.start("project-a", "flow-a", "deliver outcome")

    def tearDown(self):
        self.tmp.cleanup()

    def to_mastery(self, wid=None, builder="builder"):
        wid = wid or self.w["id"]
        w = self.e.get(wid)
        w = self.e.ground(wid, w["revision"], GROUND)
        w = self.e.begin_momentum(wid, w["revision"])
        w = self.e.deliver(wid, w["revision"], MOMENTUM, actor=builder)
        return self.e.submit_mastery(wid, w["revision"])

    def test_version_matches_release(self):
        self.assertEqual(__version__, "0.3.0")

    def test_full_cycle_persists_progress(self):
        w = self.to_mastery()
        self.assertEqual(w["stage"], "MASTERY")
        w = self.e.review(w["id"], w["revision"], "PASS", [], ["review:evidence"])
        w = self.e.learn(w["id"], w["revision"], LEARN)
        self.assertEqual((w["stage"], w["cycle"], w["progress"]), ("GROUNDING", 2, 35))
        self.assertEqual(self.e.get(w["id"])["progress"], 35)

    def test_cycle_packet_hygiene_blocks_stale_cycle_reuse(self):
        w = self.to_mastery()
        w = self.e.review(w["id"], w["revision"], "PASS", [], ["review:evidence"])
        w = self.e.learn(w["id"], w["revision"], LEARN)
        self.assertEqual(w["packets"]["grounding"], {})
        self.assertEqual(w["packets"]["momentum"], {})
        self.assertEqual(w["packets"]["mastery"], {})
        with self.assertRaises(WorkflowError):
            self.e.begin_momentum(w["id"], w["revision"])
        w = self.e.ground(w["id"], w["revision"], GROUND)
        w = self.e.begin_momentum(w["id"], w["revision"])
        with self.assertRaises(WorkflowError):
            self.e.submit_mastery(w["id"], w["revision"])

    def test_reviewer_independence_enforced(self):
        w = self.to_mastery(builder="alice")
        with self.assertRaises(WorkflowError):
            self.e.review(w["id"], w["revision"], "PASS", [], ["review:ev"], actor="Alice")

    def test_candidate_binding_enforced(self):
        w = self.to_mastery()
        with self.assertRaises(WorkflowError):
            self.e.review(
                w["id"],
                w["revision"],
                "PASS",
                [],
                ["review:ev"],
                candidate_ref="artifact:wrong",
            )
        w = self.e.review(
            w["id"],
            w["revision"],
            "PASS",
            [],
            ["review:ev"],
            candidate_ref="artifact:candidate-1",
        )
        self.assertEqual(w["stage"], "REPETITION")

    def test_momentum_is_stage_not_role(self):
        w = self.e.ground(self.w["id"], 0, GROUND)
        w = self.e.begin_momentum(w["id"], w["revision"])
        self.e.assign(w["id"], "BUILDER", "implementation", {"deliverable": "candidate"})
        with self.assertRaises(WorkflowError):
            self.e.assign(w["id"], "MOMENTUM", "workflow", {})

    def test_fail_returns_to_momentum_and_two_failures_flag_root_cause(self):
        w = self.to_mastery()
        w = self.e.review(w["id"], w["revision"], "FAIL", [{"finding": "criterion missed"}], [])
        self.assertEqual(w["stage"], "MOMENTUM")
        self.assertEqual(w["packets"]["grounding"], GROUND)
        self.assertEqual(w["packets"]["mastery"]["verdict"], "FAIL")
        self.assertFalse(w["packets"]["mastery"]["requires_root_cause"])
        w = self.e.deliver(w["id"], w["revision"], MOMENTUM)
        w = self.e.submit_mastery(w["id"], w["revision"])
        w = self.e.review(w["id"], w["revision"], "FAIL", [{"finding": "still failing"}], [])
        self.assertEqual(w["packets"]["mastery"]["fail_count"], 2)
        self.assertTrue(w["packets"]["mastery"]["requires_root_cause"])

    def test_blocked_workflow_blocks_transitions_until_unblocked(self):
        w = self.to_mastery()
        w = self.e.review(w["id"], w["revision"], "BLOCKED", [{"blocker": "access"}], [])
        self.assertEqual(w["status"], "BLOCKED")
        with self.assertRaises(WorkflowError):
            self.e.review(w["id"], w["revision"], "PASS", [], ["review:ev"])
        w = self.e.unblock(w["id"], w["revision"])
        self.assertEqual((w["stage"], w["status"]), ("MASTERY", "ACTIVE"))

    def test_conditional_requires_findings(self):
        w = self.to_mastery()
        with self.assertRaises(WorkflowError):
            self.e.review(w["id"], w["revision"], "CONDITIONAL", [], ["review:ev"])
        w = self.e.review(
            w["id"], w["revision"], "CONDITIONAL", ["follow-up test needed"], ["review:ev"]
        )
        self.assertEqual(w["stage"], "REPETITION")

    def test_pass_rejects_empty_checks_and_assumed_checks(self):
        w = self.e.ground(self.w["id"], 0, GROUND)
        w = self.e.begin_momentum(w["id"], w["revision"])
        no_checks = dict(MOMENTUM, checks=[])
        w = self.e.deliver(w["id"], w["revision"], no_checks)
        w = self.e.submit_mastery(w["id"], w["revision"])
        with self.assertRaises(WorkflowError):
            self.e.review(w["id"], w["revision"], "PASS", [], ["review:ev"])

        w2 = self.e.start("project-a", "flow-assumed", "test assumed check")
        w2 = self.e.ground(w2["id"], 0, GROUND)
        w2 = self.e.begin_momentum(w2["id"], w2["revision"])
        assumed = dict(
            MOMENTUM,
            checks=[{"name": "smoke", "outcome": "passed", "evidence_class": "ASSUMED"}],
        )
        w2 = self.e.deliver(w2["id"], w2["revision"], assumed)
        w2 = self.e.submit_mastery(w2["id"], w2["revision"])
        with self.assertRaises(WorkflowError):
            self.e.review(w2["id"], w2["revision"], "PASS", [], ["review:ev"])

    def test_progress_cannot_move_backwards_and_rejects_bool(self):
        w = self.to_mastery()
        w = self.e.review(w["id"], w["revision"], "PASS", [], ["review:evidence"])
        with self.assertRaises(WorkflowError):
            self.e.learn(w["id"], w["revision"], dict(LEARN, progress=True))
        w = self.e.learn(w["id"], w["revision"], LEARN)
        w = self.to_mastery(w["id"])
        w = self.e.review(w["id"], w["revision"], "PASS", [], ["review:evidence-2"])
        with self.assertRaises(WorkflowError):
            self.e.learn(w["id"], w["revision"], dict(LEARN, progress=20))

    def test_stage_gate_dependencies_and_assignment_isolation(self):
        w = self.e.ground(self.w["id"], 0, GROUND)
        w = self.e.begin_momentum(w["id"], w["revision"])
        aid = self.e.assign(w["id"], "BUILDER", "impl", {"deliverable": "x"})
        self.e.assignment_transition(aid, "ACCEPTED")
        item = self.e.add_work_item(
            w["id"], w["revision"], "Build module", "code built", "BUILDER", ["tests pass"]
        )
        self.assertEqual(item["workflow_revision"], w["revision"])
        res = self.e.assignment_transition(aid, "RUNNING")
        self.assertEqual(res["status"], "RUNNING")

        w = self.e.deliver(w["id"], w["revision"], MOMENTUM)
        with self.assertRaises(WorkflowError):
            self.e.submit_mastery(w["id"], w["revision"])
        self.e.change_work_item(w["id"], item["id"], w["revision"], "IN_PROGRESS")
        self.e.change_work_item(
            w["id"], item["id"], w["revision"], "COMPLETED", ["tests:passed"]
        )
        w = self.e.submit_mastery(w["id"], w["revision"])
        with self.assertRaises(WorkflowError):
            self.e.assignment_transition(
                aid, "RETURNED", {"summary": "done", "evidence": ["ev:1"]}
            )

    def test_independent_flows_share_lifecycle_not_state(self):
        other = self.e.start("project-b", "flow-b", "different outcome")
        self.assertEqual(other["stage"], "GROUNDING")
        self.e.ground(self.w["id"], 0, GROUND)
        self.assertEqual(self.e.get(other["id"])["revision"], 0)

    def test_stale_revision_rejected(self):
        self.e.ground(self.w["id"], 0, GROUND)
        with self.assertRaises(WorkflowError):
            self.e.begin_momentum(self.w["id"], 0)

    def test_append_only_events_trigger(self):
        con = sqlite3.connect(self.db_path)
        try:
            with self.assertRaises(sqlite3.DatabaseError):
                con.execute("UPDATE events SET actor='tampered'")
            with self.assertRaises(sqlite3.DatabaseError):
                con.execute("DELETE FROM events")
        finally:
            con.close()

    def test_gate_runner_produces_verified_check(self):
        runner = GateRunner(self.tmp.name)
        results = runner.run([CheckSpec(name="py-ok", command=["python", "-c", "print('ok')"])])
        self.assertEqual(len(results), 1)
        r = results[0]
        self.assertEqual(r["outcome"], "passed")
        self.assertEqual(r["exit_code"], 0)
        self.assertEqual(r["evidence_class"], "VERIFIED")
        self.assertEqual(len(r["log_hash"]), 64)

    def test_echo_adapter_and_registry(self):
        adapter = get_registry().get("echo")
        self.assertIsInstance(adapter, EchoAdapter)
        pkt = AssignmentPacket(
            run_id="run-1",
            workflow_id=self.w["id"],
            role="BUILDER",
            capability="impl",
            workspace=self.tmp.name,
            instructions="build it",
        )
        rid = adapter.start(pkt)
        events = list(adapter.stream(rid))
        self.assertEqual(len(events), 3)
        res = adapter.result(rid)
        self.assertEqual(res.status, "completed")
        adapter.cancel(rid)
        self.assertEqual(adapter.result(rid).status, "cancelled")

    def test_coding_start_and_seed_work_requires_verified_checks(self):
        w = coding_start(
            self.e,
            "my-app",
            "Add /health",
            "Expose /health endpoint",
            workspace=self.tmp.name,
            risk="R1",
        )
        w = self.e.begin_momentum(w["id"], w["revision"])
        seeded = coding_seed_work(self.e, w["id"], w["revision"])
        self.assertEqual(len(seeded), 3)
        for item in seeded:
            self.e.change_work_item(w["id"], item["id"], w["revision"], "IN_PROGRESS")
            self.e.change_work_item(
                w["id"], item["id"], w["revision"], "COMPLETED", ["done:ok"]
            )
        w = self.e.deliver(w["id"], w["revision"], MOMENTUM, actor="codex")
        w = self.e.submit_mastery(w["id"], w["revision"])
        with self.assertRaises(WorkflowError):
            self.e.review(w["id"], w["revision"], "PASS", [], ["ok"], actor="claude")

    def test_cli_smoke_and_missing_file_error(self):
        rc = cli.main(["--db", str(self.db_path), "adapters"])
        self.assertEqual(rc, 0)
        rc = cli.main(["--db", str(self.db_path), "adapter-health", "--name", "echo"])
        self.assertEqual(rc, 0)
        rc = cli.main(
            [
                "--db",
                str(self.db_path),
                "ground",
                self.w["id"],
                "examples/nonexistent.json",
                "--revision",
                "0",
            ]
        )
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
