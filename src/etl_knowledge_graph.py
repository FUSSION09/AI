"""
Phase 2: Complete Knowledge Graph ETL & Triplestore Importer
Ingests documents from d:\AI\data\corpus, extracts entities/statutes/relationships,
and outputs both a structured triplestore (JSON) and a Cypher import script for Neo4j.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
import spacy
from spacy.matcher import Matcher

from config import BASE_DIR, DATA_DIR

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class KnowledgeGraphETL:
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687", 
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password"):
        self.uri = neo4j_uri
        self.user = neo4j_user
        self.password = neo4j_password
        self.nlp = spacy.load("en_core_web_sm")
        self._setup_statute_matcher()

    def _setup_statute_matcher(self):
        self.matcher = Matcher(self.nlp.vocab)
        # Match standard federal statutory citations: e.g., '31 U.S.C. 5324', '18 U.S.C. 1956', '15 U.S.C. 78dd-1'
        statute_pattern = [
            {"IS_DIGIT": True},
            {"LOWER": {"IN": ["u.s.c.", "usc", "cfr"]}},
            {"TEXT": {"IN": ["§", "sec.", "section"]}, "OP": "?"},
            {"TEXT": {"REGEX": r"^[0-9]+[a-z0-9\-]*$"}}
        ]
        self.matcher.add("STATUTE_CITATION", [statute_pattern])

    def extract_document(self, doc_id: str, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        entities = {}
        statutes = {}
        relationships = []

        # 1. Named Entity Extraction (People, Organizations, Jurisdictions)
        for ent in doc.ents:
            name = ent.text.strip().replace("\n", " ")
            if ent.label_ in ["PERSON", "ORG", "GPE"] and len(name) > 2:
                entities[name] = ent.label_
                relationships.append({
                    "source": doc_id,
                    "source_type": "Document",
                    "rel": "MENTIONS",
                    "target": name,
                    "target_type": "Entity"
                })

        # 2. Statutory References
        for match_id, start, end in matches:
            code = doc[start:end].text.strip()
            statutes[code] = "Statutory Authority"
            relationships.append({
                "source": doc_id,
                "source_type": "Document",
                "rel": "CITES",
                "target": code,
                "target_type": "Statute"
            })

        # 3. Relational dependencies (e.g. Entity -[TRANSFERRED/VIOLATED]-> Entity/Statute)
        for token in doc:
            if token.pos_ == "VERB":
                subj = [w.text for w in token.lefts if "subj" in w.dep_]
                obj = [w.text for w in token.rights if "obj" in w.dep_]
                if subj and obj:
                    s_str = " ".join(subj).strip()
                    o_str = " ".join(obj).strip()
                    if s_str and o_str:
                        relationships.append({
                            "source": s_str,
                            "source_type": "Entity",
                            "rel": token.lemma_.upper(),
                            "target": o_str,
                            "target_type": "Entity"
                        })

        return {
            "doc_id": doc_id,
            "entities": [{"name": k, "type": v} for k, v in entities.items()],
            "statutes": [{"code": k, "category": v} for k, v in statutes.items()],
            "relationships": relationships
        }

    def process_corpus(self, corpus_dir: Path) -> Dict[str, Any]:
        all_docs = []
        all_entities = {}
        all_statutes = {}
        all_triples = []

        print(f"[Phase 2] Ingesting document corpus from: {corpus_dir}")
        for filepath in corpus_dir.glob("*.txt"):
            doc_id = filepath.stem
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            parsed = self.extract_document(doc_id, text)
            all_docs.append({"id": doc_id, "file": filepath.name, "size": len(text)})
            
            for ent in parsed["entities"]:
                all_entities[ent["name"]] = ent["type"]
            for stat in parsed["statutes"]:
                all_statutes[stat["code"]] = stat["category"]
            all_triples.extend(parsed["relationships"])

        graph_payload = {
            "documents": all_docs,
            "entities": [{"name": k, "type": v} for k, v in all_entities.items()],
            "statutes": [{"code": k, "category": v} for k, v in all_statutes.items()],
            "triples": all_triples
        }
        return graph_payload

    def export_graph(self, graph_data: Dict[str, Any], output_json: Path, output_cypher: Path):
        # 1. Export JSON representation
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)
        print(f"[Phase 2] Knowledge Graph serialized to: {output_json}")

        # 2. Export Cypher import script for Neo4j
        cypher_lines = [
            "// Auto-generated Neo4j Triplestore Ingestion Script",
            "// Load into Neo4j Community Edition via cypher-shell\n"
        ]
        # Documents
        for d in graph_data["documents"]:
            cypher_lines.append(f"MERGE (d:Document {{id: '{d['id']}'}}) ON CREATE SET d.filename = '{d['file']}';")
        # Entities
        for e in graph_data["entities"]:
            safe_name = e["name"].replace("'", "\\'")
            cypher_lines.append(f"MERGE (e:Entity {{name: '{safe_name}'}}) ON CREATE SET e.type = '{e['type']}';")
        # Statutes
        for s in graph_data["statutes"]:
            safe_code = s["code"].replace("'", "\\'")
            cypher_lines.append(f"MERGE (s:Statute {{code: '{safe_code}'}});")
        # Triples
        for t in graph_data["triples"]:
            src = t["source"].replace("'", "\\'")
            tgt = t["target"].replace("'", "\\'")
            src_lbl = t["source_type"]
            tgt_lbl = t["target_type"]
            rel = re.sub(r'[^A-Za-z0-9_]', '_', t["rel"])
            if not rel:
                rel = "RELATED_TO"
            cypher_lines.append(
                f"MATCH (a:{src_lbl} {{name: '{src}'}}), (b:{tgt_lbl} {{name: '{tgt}'}}) "
                f"MERGE (a)-[:{rel}]->(b);"
                if src_lbl != "Document" and tgt_lbl != "Statute" else
                f"MATCH (a:{src_lbl} {{id: '{src}'}}), (b:{tgt_lbl} {{{'code' if tgt_lbl == 'Statute' else 'name'}: '{tgt}'}}) "
                f"MERGE (a)-[:{rel}]->(b);"
            )

        with open(output_cypher, "w", encoding="utf-8") as f:
            f.write("\n".join(cypher_lines))
        print(f"[Phase 2] Cypher import statements written to: {output_cypher}")


if __name__ == "__main__":
    corpus_path = DATA_DIR / "corpus"
    json_path = DATA_DIR / "knowledge_graph.json"
    cypher_path = DATA_DIR / "import_graph.cypher"

    etl = KnowledgeGraphETL()
    graph = etl.process_corpus(corpus_path)
    etl.export_graph(graph, json_path, cypher_path)
    
    print(f"\nIngestion summary:")
    print(f"- Total Documents parsed: {len(graph['documents'])}")
    print(f"- Total Unique Entities:  {len(graph['entities'])}")
    print(f"- Total Unique Statutes:  {len(graph['statutes'])}")
    print(f"- Total Triples/Edges:    {len(graph['triples'])}")
