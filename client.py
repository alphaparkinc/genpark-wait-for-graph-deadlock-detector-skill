class DeadlockDetector:
    """
    Wait-For Graph (WFG) Deadlock Detector.
    Tracks txn dependencies on resource holders and discovers wait cycles using Tarjan/DFS.
    """
    def __init__(self):
        self.graph = {} # waiter -> set of holders
        self.txn_metadata = {} # txn_id -> {"timestamp": int, "cost": int}

    def register_txn(self, txn_id, timestamp=0, cost=1):
        self.txn_metadata[txn_id] = {"timestamp": timestamp, "cost": cost}

    def add_wait(self, waiter, holder):
        if waiter not in self.graph:
            self.graph[waiter] = set()
        self.graph[waiter].add(holder)

    def remove_wait(self, waiter, holder):
        if waiter in self.graph:
            self.graph[waiter].discard(holder)
            if not self.graph[waiter]:
                del self.graph[waiter]

    def remove_txn(self, txn_id):
        self.graph.pop(txn_id, None)
        for waiter in list(self.graph.keys()):
            self.graph[waiter].discard(txn_id)
            if not self.graph[waiter]:
                del self.graph[waiter]
        self.txn_metadata.pop(txn_id, None)

    def find_cycle(self):
        visited = set()
        rec_stack = []

        def dfs(node):
            visited.add(node)
            rec_stack.append(node)
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    res = dfs(neighbor)
                    if res:
                        return res
                elif neighbor in rec_stack:
                    idx = rec_stack.index(neighbor)
                    return rec_stack[idx:] # return exact cycle
            rec_stack.pop()
            return None

        for n in list(self.graph.keys()):
            if n not in visited:
                cycle = dfs(n)
                if cycle:
                    return cycle
        return None

    def select_victim(self, cycle, policy="youngest"):
        """
        Victim selection policies:
        - 'youngest': Abort txn with largest timestamp
        - 'lowest_cost': Abort txn with minimum invested work
        """
        if policy == "youngest":
            return max(cycle, key=lambda t: self.txn_metadata.get(t, {}).get("timestamp", 0))
        elif policy == "lowest_cost":
            return min(cycle, key=lambda t: self.txn_metadata.get(t, {}).get("cost", 1))
        return cycle[0]
