"""Builds the single workflow "Can My PC Run It".

    python tools/build.py                      portable profile: placeholders, no credential  -> exports/can-my-pc-run-it.json
    PROFILE=instance python tools/build.py     real ids from tools/instance.local.json         -> exports/can-my-pc-run-it.instance.json (git-ignored)

The .workflow.ts file is produced from the portable JSON by tools/convert.mjs (see README).
"""
import json
import sys

from lib import *
import s_context
import s_delivery
import s_diagnosis
import s_entry
import s_errors
import s_evidence
import s_notes

NAME = "Can My PC Run It"
DESCRIPTION = ("Diagnoses public GitHub repositories for a personal Windows 11 PC. Reads the latest stable release, the README and the issues with native GitHub nodes, "
               "reuses an identical report when the repositories, versions and goal are the same, reads the personal context from Notion, asks Gemini for a strict JSON diagnostic, "
               "then delivers a Notion page and an HTML e-mail with the JSON attached. Two Data Tables keep the analysis history and the incidents.")


def main():
    settings = {}
    if PROFILE == "instance" and LOCAL.get("workflowId"):
        settings["errorWorkflow"] = LOCAL["workflowId"]
    w = Flow(NAME, DESCRIPTION, settings)
    for section in (s_entry, s_evidence, s_context, s_diagnosis, s_delivery, s_errors):
        section.build(w)
    s_notes.build(w)
    suffix = ".instance" if PROFILE == "instance" else ""
    target = ROOT / "exports" / f"can-my-pc-run-it{suffix}.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(w.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    nodes = [n for n in w.nodes if not n["type"].endswith("stickyNote")]
    print(f"{target}: {len(nodes)} nodes, {len(w.nodes) - len(nodes)} sticky notes")


if __name__ == "__main__":
    sys.exit(main())
