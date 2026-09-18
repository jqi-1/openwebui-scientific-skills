#!/usr/bin/env python3
"""One-click installer: import all converted Open WebUI skills at once.

Open WebUI has no bulk-skill API endpoint, so this uses the official
`POST /api/v1/skills/create` endpoint once per skill (166 requests against a
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
  --insecure         allow plain HTTP when the host is not localhost (risky:
                     sends credentials/token unencrypted over the network)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "/api/v1/skills/create"
SIGNIN = "/api/v1/auths/signin"


def as_bool(value, default=True):
    """Coerce a bundle `is_active` value to bool, honoring string flags
    ("false"/"0"/"no"/empty mean inactive) that bool() would inflate to True."""
    if isinstance(value, str):
        return value.strip().lower() not in ("0", "false", "no", "")
    return bool(value) if value is not None else default


def post(url, payload, token=None, timeout=30, retries=3):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    last_transport = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode()
                # 204/empty-body 2xx is a success with no payload; a JSON
                # decode failure must not turn it into a transport error.
                return resp.status, (json.loads(body) if body.strip() else {})
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode()
            except Exception:
                body = ""
            try:
                parsed = json.loads(body) if body else {}
            except ValueError:
                parsed = {}
            # Transient server faults deserve a retry; client errors don't.
            if e.code in (500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(1 + attempt)
                continue
            return e.code, parsed
        except (OSError, TimeoutError, ValueError) as exc:
            last_transport = exc
            if attempt < retries - 1:
                time.sleep(1 + attempt)
    # Transport-level failure (unreachable, timeout, non-JSON body): report as
    # a failed request so the batch loop keeps going and the summary prints.
    return -1, {"detail": str(last_transport)}


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
    p.add_argument("--insecure", action="store_true")
    args = p.parse_args()

    url = args.url.rstrip("/")
    if not args.token and not (args.email and args.password):
        print("error: provide --token or --email/--password", file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(args.file):
        print("error: skills bundle not found:", args.file, file=sys.stderr)
        sys.exit(2)
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https"):
        print("error: unsupported URL scheme '%s'; use http(s)://" % parts.scheme,
              file=sys.stderr)
        sys.exit(2)
    if parts.scheme != "https" and parts.hostname not in (None, "localhost",
                                                          "127.0.0.1", "::1"):
        if not args.insecure:
            print("error: refusing to send credentials/token over plain HTTP "
                  "to %s; use https:// or --insecure" % url, file=sys.stderr)
            sys.exit(2)
        print("warning: sending credentials/token over plain HTTP to %s "
              "(--insecure)" % url, file=sys.stderr)

    if args.token:
        token = args.token
    else:
        print("signing in...")
        status, data = post(url + SIGNIN,
                            {"email": args.email, "password": args.password},
                            timeout=args.timeout)
        if status != 200 or not isinstance(data, dict) or "token" not in data:
            detail = data.get("detail", data) if isinstance(data, dict) else data
            print("error: signin failed (HTTP %s): %s" % (status, detail),
                  file=sys.stderr)
            sys.exit(1)
        token = data["token"]
        print("authenticated as", args.email)

    # Connectivity sanity check against a real endpoint before hammering
    # /create. /api/v1/auths/ requires token auth, so attaching the token
    # makes the check prove both reachability and validity: 200 -> server up
    # and token accepted; 401/403 -> bad token (fail fast with the real cause).
    req = urllib.request.Request(url + "/api/v1/auths/")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except OSError as e:
        print("error: cannot reach Open WebUI at %s (%s)" % (url, e), file=sys.stderr)
        sys.exit(1)
    if status in (401, 403):
        print("error: authentication failed (HTTP %s) — invalid or expired "
              "token" % status, file=sys.stderr)
        sys.exit(1)
    if status not in (200, 201, 202, 204):
        print("error: unexpected status %s from %s" % (status, url), file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        with open(args.file, encoding="utf-8") as f:
            skills = json.load(f)
        if not isinstance(skills, list):
            print("error: bundle must be a JSON array of skills", file=sys.stderr)
            sys.exit(2)
        print("dry-run: connectivity OK, would create %d skills" % len(skills))
        return

    with open(args.file, encoding="utf-8") as f:
        skills = json.load(f)
    if not isinstance(skills, list):
        print("error: bundle must be a JSON array of skills", file=sys.stderr)
        sys.exit(2)
    print(f"bundle: {len(skills)} skills from {args.file}")

    def skill_label(s):
        return s["id"] if isinstance(s, dict) and s.get("id") else str(s)

    created = skipped = failed = transport_failed = 0
    for s in skills:
        try:
            if not s.get("id"):
                raise KeyError("entry missing a non-empty id")
            payload = {
                "id": s["id"],
                "name": s["name"],
                "description": s.get("description", ""),
                "content": s["content"],
                "meta": s.get("meta", {}),
                "is_active": as_bool(s.get("is_active", True)),
                "access_grants": s.get("access_grants", []),
            }
            status, data = post(url + API, payload, token=token, timeout=args.timeout)
        except (KeyError, TypeError, AttributeError) as exc:
            # Malformed bundle entry (missing field / non-dictable object):
            # report it and keep going so the summary always prints.
            failed += 1
            print(f"  [fail] {skill_label(s)}: malformed entry ({exc})")
            continue
        if status in (200, 201, 202, 204):
            created += 1
        elif status == -1:
            # Transport failure (unreachable/timeout/non-JSON) — report it
            # separately so it is never misread as an API rejection or skip.
            transport_failed += 1
            detail = str(data.get("detail", "") if isinstance(data, dict) else data)
            print(f"  [fail] {skill_label(s)}: request error - {detail}")
        else:
            # data is a dict on request failures, but post() can surface other
            # JSON shapes from HTTPError/parse paths; never assume .get().
            detail = str(data.get("detail", "") if isinstance(data, dict) else data).lower()
            sid = str(s["id"]).lower()
            # Duplicate ids are idempotent skips; anchor on the offending id
            # as a delimited token plus an unambiguous duplicate wording
            # ("already"/"taken" — not bare "exists", which appears in
            # unrelated messages like "referenced model does not exist").
            # Token matching keeps short ids ("al") from matching inside
            # unrelated words ("already"); empty ids never skip.
            if sid and any(w in detail for w in ("taken", "already")) and re.search(
                    r"(?<![A-Za-z0-9_-])" + re.escape(sid) + r"(?![A-Za-z0-9_-])",
                    detail):
                skipped += 1  # id already exists -> idempotent
            else:
                failed += 1
                print(f"  [fail] {skill_label(s)}: {detail or data}")
    print(f"done: {created} created, {skipped} already present, "
          f"{failed + transport_failed} failed ({len(skills)} total; "
          f"re-run to resume any failed, existing skills are skipped)")
    sys.exit(1 if (failed or transport_failed) else 0)


if __name__ == "__main__":
    main()
