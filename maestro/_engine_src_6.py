SRC = """a or status not in transitions.get(a["status"], set()):
                raise WorkflowError("invalid assignment transition")
            w = db.execute(
                "SELECT * FROM workflows WHERE id=?", (a["workflow_id"],)
            ).fetchone()
            p = json.loads(a["packet"])
            if (
                not w
                or w["stage"] != a["stage"]
                or w["cycle"] != p.get("cycle", w["cycle"])
                or w["status"] != "ACTIVE"
            ):
                raise WorkflowError("stale assignment")
            if status == "RETURNED":
                if not isinstance(result, dict):
                    raise WorkflowError("return requires result object")
                _require_non_empty_str(result.get("summary"), "result.summary")
                _require_str_list(
                    result.get("evidence"), "result.evidence", allow_empty=False
                )
                p["result"] = result
            stamp = _now()
            db.execute(
                "UPDATE assignments SET status=?,packet=?,updated_at=? WHERE id=?",
                (status, _dump(p), stamp, aid),
            )
            self._event(
                db,
                a["workflow_id"],
                w["revision"],
                "ASSIGNMENT_" + status,
                a["stage"],
                a["stage"],
                actor,
                {"id": aid},
            )
        return {"id": aid, "status": status, "packet": p}

    def assignments(self, wid: str) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM assignments WHERE workflow_id=? ORDER BY created_at ASC, id ASC",
                (wid,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "stage": r["stage"],
                "role": r["role"],
                "capability": r["capability"],
                "status": r["status"],
                "packet": json.loads(r["packet"]),
            }
            for r in rows
        ]

    def events(self, wid: str) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM events WHERE workflow_id=? ORDER BY seq ASC", (wid,)
            ).fetchall()
        return [
            {
                "seq": r["seq"],
                "revision": r["revision"],
                "type": r["event_type"],
                "from": r["from_stage"],
                "to": r["to_stage"],
                "actor": r["actor"],
                "payload": json.loads(r["payload"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
"""
