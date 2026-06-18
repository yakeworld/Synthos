#!/usr/bin/env python3
"""
promote-track-a.py — Track A Promotion Script (Phase 3, v3.18)
==============================================================
Call from Autonomous Core Researcher cron: python3 promote-track-a.py
Scans _knowledge_only/ for directories with paper.tex but NOT in paper-queue.json,
then promotes them to Track A:
  - mv _knowledge_only/<dir> ../<dir>
  - Creates index.md (source=promoted_from_track_b)
  - Syncs paper.tex to 01-manuscript/
  - Adds entry to paper-queue.json (honouring existing state.json values)
  - Updates research-queue.json

Usage: python3 scripts/promote-track-a.py
Run from: outputs/papers/

Exits with code 0 regardless of how many promotions happened.
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone

PAPERS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE = os.path.join(PAPERS, "_knowledge_only")
PAPER_QUEUE = os.path.join(PAPERS, "paper-queue.json")
RESEARCH_QUEUE = os.path.join(KNOWLEDGE, "research-queue.json")


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_existing_state(dir_path):
    """Read state.json for quality_score, gate_status, and stage."""
    state_path = os.path.join(dir_path, "state.json")
    if not os.path.exists(state_path):
        return {"quality_score": 60, "gate_status": "PENDING", "stage": "unknown",
                "d10a": None, "steps_completed": []}
    try:
        with open(state_path) as f:
            s = json.load(f)
        return {
            "quality_score": s.get("quality_score", 60),
            "gate_status": s.get("gate_status", "PENDING"),
            "stage": s.get("stage", "unknown"),
            "d10a": s.get("d8_d10a_scan", {}).get("d10a", None),
            "steps_completed": s.get("steps_completed", []),
        }
    except (json.JSONDecodeError, FileNotFoundError):
        return {"quality_score": 60, "gate_status": "PENDING", "stage": "unknown",
                "d10a": None, "steps_completed": []}


def promote(name):
    """Promote one candidate from _knowledge_only/ to papers/."""
    src = os.path.join(KNOWLEDGE, name)
    dst = os.path.join(PAPERS, name)

    if os.path.exists(dst):
        print(f"  WARNING: {name} already exists in papers/ -- skip")
        return False

    state = get_existing_state(src)
    print(f"  state.json: qs={state['quality_score']}, gate={state['gate_status']}, "
          f"stage={state['stage']}, D10a={state.get('d10a', 'N/A')}%")

    # Move directory
    shutil.move(src, dst)
    print(f"  MOVED: _knowledge_only/{name} -> {name}")

    # Create index.md if absent
    index_path = os.path.join(dst, "index.md")
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write("---\n")
            f.write("source: promoted_from_track_b\n")
            f.write(f"promoted_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
            f.write(f"state: qs={state['quality_score']}, gate={state['gate_status']}, "
                    f"stage={state['stage']}\n")
            f.write("---\n")
        print(f"  index.md created")

    # Ensure 01-manuscript/paper.tex exists
    root_tex = os.path.join(dst, "paper.tex")
    dst_tex = os.path.join(dst, "01-manuscript", "paper.tex")
    if os.path.exists(root_tex) and not os.path.exists(dst_tex):
        os.makedirs(os.path.dirname(dst_tex), exist_ok=True)
        shutil.copy2(root_tex, dst_tex)
        print(f"  paper.tex synced to 01-manuscript/")

    # Add to paper-queue.json -- honour existing state
    paper_queue = load_json(PAPER_QUEUE)
    if paper_queue is None:
        print(f"  WARNING: paper-queue.json not found")
        return True

    existing_ids = {p["paper_id"] for p in paper_queue.get("papers", [])}
    if name not in existing_ids:
        entry = {
            "paper_id": name,
            "status": "completed" if state["gate_status"] == "PASS" else "pending",
            "current_step": state.get("stage", "unknown"),
            "quality_score": state["quality_score"],
            "gate_status": state["gate_status"],
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": {
                "track_a_promotion": (
                    f"Promoted from _knowledge_only/. state.json: "
                    f"qs={state['quality_score']}, gate={state['gate_status']}, "
                    f"stage={state['stage']}, D10a={state.get('d10a', 'N/A')}%"
                )
            }
        }
        if state.get("steps_completed"):
            entry["steps_completed"] = state["steps_completed"]

        paper_queue.setdefault("papers", []).append(entry)
        paper_queue["papers"].sort(key=lambda x: x["paper_id"])
        save_json(PAPER_QUEUE, paper_queue)
        print(f"  Added to paper-queue.json (qs={state['quality_score']}, "
              f"gate={state['gate_status']})")
    else:
        print(f"  Already in paper-queue.json")

    return True


def main():
    """Run Phase 3 promotion for all eligible _knowledge_only candidates."""
    if not os.path.isdir(KNOWLEDGE):
        print("No _knowledge_only/ directory found. Nothing to promote.")
        return 0

    paper_queue = load_json(PAPER_QUEUE)
    track_a_ids = {p["paper_id"] for p in paper_queue.get("papers", [])} if paper_queue else set()

    candidates = []
    for entry in sorted(os.listdir(KNOWLEDGE)):
        entry_path = os.path.join(KNOWLEDGE, entry)
        if not os.path.isdir(entry_path) or entry.startswith("_"):
            continue
        if entry in track_a_ids:
            continue

        has_tex = (os.path.exists(os.path.join(entry_path, "paper.tex")) or
                   os.path.exists(os.path.join(entry_path, "01-manuscript", "paper.tex")))
        if has_tex:
            candidates.append(entry)

    if not candidates:
        print("No candidates found for Track A promotion.")
        return 0

    print(f"Found {len(candidates)} candidate(s) with paper.tex in _knowledge_only/:")

    promoted = []
    for name in candidates:
        print(f"\nFile: {name}")
        if promote(name):
            promoted.append(name)

    # Update research-queue.json
    research_queue = load_json(RESEARCH_QUEUE)
    if research_queue:
        research_queue.setdefault("promoted_to_track_a", [])
        for name in promoted:
            dst_path = os.path.join(PAPERS, name)
            state = get_existing_state(dst_path) if os.path.isdir(dst_path) else {}
            entry = (f"{name} "
                     f"(qs={state.get('quality_score','?')}, "
                     f"gate={state.get('gate_status','?')}, "
                     f"D10a={state.get('d10a','N/A')}%, "
                     f"stage={state.get('stage','?')})")
            research_queue["promoted_to_track_a"].append(entry)

        research_queue["candidates"] = [
            c for c in research_queue.get("candidates", [])
            if c["candidate_id"] not in promoted
        ]

        research_queue["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        save_json(RESEARCH_QUEUE, research_queue)
        print(f"\nresearch-queue.json updated")

    print(f"\nSummary: {len(promoted)}/{len(candidates)} promoted")
    for p in promoted:
        print(f"  Promoted: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
