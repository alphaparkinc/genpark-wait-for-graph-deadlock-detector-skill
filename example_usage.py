import sys
from client import DeadlockDetector

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def run():
    print(">>> Demonstrating Wait-For Graph Deadlock Detection...")
    wfg = DeadlockDetector()
    wfg.register_txn("T1", timestamp=100, cost=50)
    wfg.register_txn("T2", timestamp=105, cost=30)
    wfg.register_txn("T3", timestamp=110, cost=10)

    # T1 waits for T2, T2 waits for T3
    wfg.add_wait("T1", "T2")
    wfg.add_wait("T2", "T3")
    assert wfg.find_cycle() is None
    print("No deadlock in linear chain T1 -> T2 -> T3")

    # T3 waits for T1 (Cycle!)
    wfg.add_wait("T3", "T1")
    cycle = wfg.find_cycle()
    print(f"Deadlock detected! Cycle: {cycle}")
    assert cycle is not None

    victim = wfg.select_victim(cycle, policy="youngest")
    print(f"Selected victim by youngest timestamp: {victim}")
    assert victim == "T3"

    wfg.remove_txn(victim)
    assert wfg.find_cycle() is None
    print(f"Cycle resolved after aborting victim {victim}")
    print("[PASS] Wait-For Graph Deadlock Detector verified.")

if __name__ == "__main__":
    run()
