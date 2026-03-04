#!/usr/bin/env python3
import json, os, sys, urllib.request

q = sys.argv[1] if len(sys.argv) > 1 else ""
if not q:
    print("Usage: search.py query")
    sys.exit(2)

key = os.environ.get("TAVILY_API_KEY", "")
if not key:
    print("Missing TAVILY_API_KEY")
    sys.exit(1)

body = {"api_key": key, "query": q, "max_results": 5, "include_answer": True}
data = json.dumps(body).encode()
req = urllib.request.Request("https://api.tavily.com/search", data=data, headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())

ans = resp.get("answer", "")
if ans:
    print("Answer:", ans)
    print("---")

for r in resp.get("results", []):
    print("-", r.get("title", ""))
    print(" ", r.get("url", ""))
    c = r.get("content", "")
    if c:
        print(" ", c[:300])
    print()
