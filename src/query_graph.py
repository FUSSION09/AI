"""
Phase 2: Graph Retrieval & Semantic Traversal Engine
Allows semantic lookup of entities, citing documents, and interconnected statutes.
"""

import json
from pathlib import Path
from config import DATA_DIR

GRAPH_JSON = DATA_DIR / "knowledge_graph.json"

class GraphExplorer:
    def __init__(self, graph_path: Path = GRAPH_JSON):
        with open(graph_path, "r", encoding="utf-8") as f:
            self.graph = json.load(f)

    def find_entity_connections(self, entity_name: str):
        print(f"\n[Graph Query] Querying relationships for entity: '{entity_name}'")
        matches = []
        for t in self.graph["triples"]:
            if entity_name.lower() in t["source"].lower() or entity_name.lower() in t["target"].lower():
                matches.append(t)
        return matches

    def find_statutory_violations(self, statute_code: str):
        print(f"\n[Graph Query] Querying citations & violations for statute: '{statute_code}'")
        citing_docs = []
        for t in self.graph["triples"]:
            if t["target_type"] == "Statute" and statute_code.lower() in t["target"].lower():
                citing_docs.append(t["source"])
        return citing_docs

if __name__ == "__main__":
    explorer = GraphExplorer()
    print("Graph Explorer initialized.")
    
    # Query Marcus Vance connections
    rels = explorer.find_entity_connections("Marcus Vance")
    for r in rels:
        print(f" -> [{r['source_type']}] {r['source']}  --({r['rel']})-->  [{r['target_type']}] {r['target']}")

    # Query 31 U.S.C. 5324 citations
    docs = explorer.find_statutory_violations("31 U.S.C. 5324")
    print(f" -> Documents citing 31 U.S.C. 5324: {docs}")

