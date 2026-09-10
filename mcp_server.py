import json
import sys
from client import DeadlockDetector

detector = DeadlockDetector()

def handle_rpc(line):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        rid = req.get("id")
        
        if method == "tools/list":
            tools = [
                {"name": "add_wait", "description": "Add wait edge from waiter to holder"},
                {"name": "check_deadlock", "description": "Detect deadlock cycles and select victim"}
            ]
            return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
        elif method == "tools/call":
            tname = params.get("name")
            args = params.get("arguments", {})
            if tname == "add_wait":
                detector.add_wait(args["waiter"], args["holder"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"status": "edge_added"}})
            elif tname == "check_deadlock":
                cycle = detector.find_cycle()
                victim = detector.select_victim(cycle) if cycle else None
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"deadlock": bool(cycle), "cycle": cycle, "victim": victim}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(handle_rpc(line.strip()), flush=True)
