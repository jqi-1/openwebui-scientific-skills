#!/usr/bin/env python3
"""One-click installer: import all converted Open WebUI skills at once.

Open WebUI has no bulk-skill API endpoint, so this uses the official
`POST /api/v1/skills/create` endpoint once per skill (163 requests against a
local instance, a couple of seconds total). The skills.json in this repo is
the exact payload the built-in "Import JSON" button would create, so the
result is identical to a manual bulk import — without any UI clicks.

Usage:
  # With an existing API token (JWT):
  python3 install_to_openwebui.py --url http://localhost:8080 --token eyJ...

  # Or let the script authenticate with admin credentials:
  python3 install_to_openwebui.py --url http://localhost:8080 \
      --email admin@example.com --password '...'

Options:
  --url BASE_URL     Open WebUI root (default: http://localhost:8080)
  --token TOKEN      Bearer JWT. Overrides --email/--password if set.
  --email / --password   Admin credentials; the script signs in and uses the
                     returned token.
  --file PATH        skills bundle to install (default: openwebui/skills.json)
  --timeout SECS     per-request timeout (default 30)
  --dry-run          validate connectivity + bundle without creating skills
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "/api/v1/skills/create"
SIGNIN = "/api/v1/auths/signin"


def post(url, payload, token=None, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ""
        return e.code, (json.loads(body) if body else {})


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default="http://localhost:8080", help="Open WebUI root")
    p.add_argument("--token", default=None)
    p.add_argument("--email", default=None)
    p.add_argument("--password", default=None)
    p.add_argument("--file", default="openwebui/skills.json")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    url = args.url.rstrip("/")
    if not args.token and not (args.email and args.password):
        print("error: provide --token or --email/--password", file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(args.file):
        print("error: skills bundle not found:", args.file, file=sys.stderr)
        sys.exit(2)

    if args.token:
        token = args.token
    else:
        print("signing in...")
        status, data = post(url + SIGNIN,
                            {"email": args.email, "password": args.password},
                            timeout=args.timeout)
        if status != 200 or not isinstance(data, dict) or "token" not in data:
            print("error: signin failed (HTTP %s): %s" % (status, data.get("detail", data)),
                  file=sys.stderr)
            sys.exit(1)
        token = data["token"]
        print("authenticated as", args.email)

    # Connectivity sanity check against a real endpoint before hammering /create.
    # /api/v1/auths/ is behind token auth, so 401/403 also prove the server is
    # up (that is the normal case for --token mode).
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url + "/api/v1/auths/"),
                timeout=args.timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except urllib.error.URLError as e:
        print("error: cannot reach Open WebUI at %s (%s)" % (url, e), file=sys.stderr)
        sys.exit(1)
    if status not in (200, 201, 202, 204, 401, 403):
        print("error: unexpected status %s from %s" % (status, url), file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        n = len(json.load(open(args.file, encoding="utf-8")))
        print("dry-run: connectivity OK, would create %d skills" % n)
        return

    with open(args.file, encoding="utf-8") as f:
        skills = json.load(f)
    if not isinstance(skills, list):
        print("error: bundle must be a JSON array of skills", file=sys.stderr)
        sys.exit(2)
    print(f"bundle: {len(skills)} skills from {args.file}")

    created = skipped = failed = 0
    for s in skills:
        payload = {
            "id": s["id"],
            "name": s["name"],
            "description": s.get("description", ""),
            "content": s["content"],
            "meta": s.get("meta", {}),
            "is_active": bool(s.get("is_active", True)),
            "access_grants": [],
        }
        status, data = post(url + API, payload, token=token, timeout=args.timeout)
        if status == 200:
            created += 1
        else:
            detail = data.get("detail")
            if detail and ("taken" in str(detail).lower()
                           or "already" in str(detail).lower()):
                skipped += 1  # id already exists -> idempotent
            else:
                failed += 1
                print(f"  [fail] {s['id']}: {detail}")
    print(f"done: {created} created, {skipped} already present, {failed} failed "
          f"({len(skills)} total)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
