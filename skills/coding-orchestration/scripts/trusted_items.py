#!/usr/bin/env python3
"""Reduce GitHub issues or PRs (REST JSON) to what the improver may read. Stdlib only.

usage: trusted_items.py <api-json-file> > items.json
Anyone can open an issue or PR on a public repo, and the agent that reads these can run code, so only repo
members' items reach it at all: OWNER, MEMBER or COLLABORATOR authors keep their number, title and body;
everything else is dropped, titles included (a title is text an attacker chooses). The cost is that the
builder can't see non-members' open PRs, so it may duplicate one; a human reviews every PR anyway.
Pull requests listed by the issues endpoint are dropped (they come from the pulls endpoint).
"""
from __future__ import annotations

import json
import sys

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}


def reduce(items: list[dict]) -> list[dict]:
    out = []
    for it in items:
        if "pull_request" in it and "head" not in it:  # an issues-endpoint entry that is really a PR
            continue
        if it.get("author_association") in TRUSTED:
            out.append({"number": it["number"], "title": it["title"], "body": it.get("body") or ""})
    return out


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.dumps(reduce(json.load(f)), indent=1))
