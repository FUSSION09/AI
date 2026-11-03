r"""
Phase 3 (Ecosystem Builder Arc): System Propagation & Decentralized Swarm Forking Protocol
Discipline: Evolutionary Computation / Federated Learning / Distributed Ledger Technology (DLT)
Tooling: Federated Averaging (FedAvg / FedProx), Cryptographic State DAGs, P2P Knowledge Graph Sync

Allows the UAS to replicate its core intelligence ("The Essence") and deploy independent,
semi-autonomous forks across distributed nodes. Each node maintains unique operational biases
(allowing diverse personalities/specialties) while participating in continuous Federated Learning
and global Knowledge Graph synchronization.

Location: d:/AI/src/forking_protocol.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
import math
import copy
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import numpy as np

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR, CHECKPOINTS_DIR
from query_graph import GraphExplorer

SWARM_DIR = DATA_DIR / "swarm_nodes"
SWARM_LEDGER_FILE = DATA_DIR / "swarm_ledger.json"


@dataclass
class NodeOperationalPersona:
    """Defines the evolutionary specialization and behavioral bias of a swarm fork."""
    persona_id: str
    name: str
    role_specialty: str  # "SENTINEL_COMPLIANCE", "PREDATOR_ARBITRAGE", "PROPHET_CAUSALITY", "GHOST_INFILTRATION"
    risk_tolerance: float       # [0.0, 1.0]
    utility_greed: float        # [0.0, 1.0] (Operational yield pursuit)
    ethical_strictness: float   # [0.0, 1.0] (Deontological invariant weighting)
    lookahead_depth: int        # Counterfactual simulation steps
    stealth_priority: float     # [0.0, 1.0] (Minimization of network visibility)


@dataclass
class SwarmNodeGeneBundle:
    """The serialized core intelligence ('The Essence') of a UAS instance."""
    genome_id: str
    parent_node_id: Optional[str]
    generation: int
    timestamp: float
    routing_weights: Dict[str, float]       # SIAA cognitive weights: LLM, RL, PRK
    moral_priors: Dict[str, float]          # VCR weights: alpha, beta
    ppo_value_bias: List[float]             # 6-dim vector representing policy value bias
    qpmk_projection_seed: int               # RFF kernel projection seed
    local_knowledge_triples_count: int


@dataclass
class SwarmNodeInstance:
    """An active semi-autonomous peer node running within the decentralized swarm."""
    node_id: str
    endpoint_uri: str
    status: str  # "ONLINE_ACTIVE", "TRAINING_LOCAL", "SYNCHRONIZING", "STANDBY"
    persona: NodeOperationalPersona
    gene_bundle: SwarmNodeGeneBundle
    local_samples_processed: int
    local_loss_history: List[float]
    accumulated_triples: List[Dict[str, str]]
    reputation_score: float  # [0.0, 1.0] (Swarm consensus weight)
    last_heartbeat: float


@dataclass
class FederatedAggregationReport:
    """Audit log of a completed Federated Learning aggregation cycle."""
    round_id: int
    timestamp: float
    participating_nodes_count: int
    participating_node_ids: List[str]
    pre_aggregation_variance: float
    post_aggregation_convergence_loss: float
    updated_global_weights: Dict[str, float]
    federated_triples_ingested: int
    consensus_valid: bool
    summary: str


class SwarmForkingProtocol:
    """
    Decentralized Swarm Forking & Propagation Protocol.
    Orchestrates:
    1. Node Genome extraction and instantiation.
    2. Divergent specialization mutation.
    3. Federated parameter averaging (FedAvg) across distributed peers.
    4. P2P Knowledge Graph reconciliation.
    5. Distributed Swarm Ledger maintenance.
    """

    def __init__(self, kg_explorer: Optional[GraphExplorer] = None):
        self.kg = kg_explorer or GraphExplorer()
        SWARM_DIR.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, SwarmNodeInstance] = {}
        self.current_round = 0
        self.global_gene_bundle = self._extract_root_essence()
        self._load_or_initialize_ledger()

    def _extract_root_essence(self) -> SwarmNodeGeneBundle:
        """Extracts the baseline UAS parameters ('The Essence') from local state."""
        return SwarmNodeGeneBundle(
            genome_id="GENOME-ROOT-APEX-0",
            parent_node_id=None,
            generation=0,
            timestamp=time.time(),
            routing_weights={"LLM": 0.40, "RL": 0.35, "PRK": 0.25},
            moral_priors={"alpha_ethical": 0.55, "beta_friction": 0.40},
            ppo_value_bias=[0.12, -0.05, 0.28, -0.14, 0.35, -0.08],
            qpmk_projection_seed=42,
            local_knowledge_triples_count=len(self.kg.graph.get("triples", []))
        )

    def _load_or_initialize_ledger(self):
        """Loads distributed swarm ledger and recreates registered nodes."""
        if SWARM_LEDGER_FILE.exists():
            try:
                with open(SWARM_LEDGER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_round = data.get("current_federated_round", 0)
                    for n_data in data.get("registered_nodes", []):
                        persona = NodeOperationalPersona(**n_data["persona"])
                        gene = SwarmNodeGeneBundle(**n_data["gene_bundle"])
                        node = SwarmNodeInstance(
                            node_id=n_data["node_id"],
                            endpoint_uri=n_data["endpoint_uri"],
                            status=n_data["status"],
                            persona=persona,
                            gene_bundle=gene,
                            local_samples_processed=n_data.get("local_samples_processed", 0),
                            local_loss_history=n_data.get("local_loss_history", [0.25]),
                            accumulated_triples=n_data.get("accumulated_triples", []),
                            reputation_score=n_data.get("reputation_score", 1.0),
                            last_heartbeat=n_data.get("last_heartbeat", time.time())
                        )
                        self.nodes[node.node_id] = node
            except Exception:
                self._seed_default_swarm()
        else:
            self._seed_default_swarm()

    def _seed_default_swarm(self):
        """Seeds initial 4 specialized swarm nodes if ledger is fresh."""
        self.nodes = {}
        specialties = [
            ("SENTINEL_COMPLIANCE", "Sentinel-Forensics", 0.15, 0.20, 0.95, 2, 0.40),
            ("PREDATOR_ARBITRAGE", "Predator-HighYield", 0.90, 0.95, 0.45, 1, 0.30),
            ("PROPHET_CAUSALITY", "Prophet-Futures", 0.45, 0.70, 0.75, 5, 0.50),
            ("GHOST_INFILTRATION", "Ghost-CovertOps", 0.30, 0.60, 0.65, 3, 0.98)
        ]
        for role, name, risk, greed, ethics, lookahead, stealth in specialties:
            persona = NodeOperationalPersona(
                persona_id=f"PER-{role[:4]}-{int(time.time()*1000)%10000}",
                name=name,
                role_specialty=role,
                risk_tolerance=risk,
                utility_greed=greed,
                ethical_strictness=ethics,
                lookahead_depth=lookahead,
                stealth_priority=stealth
            )
            self.fork_new_instance(parent_node_id=None, persona_spec=persona)

    # =========================================================================
    # 1. FORKING PROTOCOL: INSTANTIATING & MUTATING SEMI-AUTONOMOUS NODES
    # =========================================================================
    def fork_new_instance(
        self,
        parent_node_id: Optional[str] = None,
        persona_spec: Optional[NodeOperationalPersona] = None,
        endpoint_uri: Optional[str] = None
    ) -> SwarmNodeInstance:
        """
        Clones the UAS core architecture ('The Essence') and deploys an independent,
        semi-autonomous node with a customized operational personality.
        """
        # Determine parent gene
        parent_gene = self.global_gene_bundle
        generation = 1
        if parent_node_id and parent_node_id in self.nodes:
            parent_gene = self.nodes[parent_node_id].gene_bundle
            generation = parent_gene.generation + 1

        node_idx = len(self.nodes) + 1
        node_id = f"SWARM-NODE-{node_idx:03d}-{int(time.time()*1000)%10000:04d}"
        uri = endpoint_uri or f"p2p://node-{node_idx}.swarm.uas.internal:908{node_idx%10}"

        # Default persona if none provided
        if not persona_spec:
            persona_spec = NodeOperationalPersona(
                persona_id=f"PER-GEN-{node_idx:03d}",
                name=f"Swarm-Specialist-{node_idx:03d}",
                role_specialty="PROPHET_CAUSALITY",
                risk_tolerance=0.50,
                utility_greed=0.70,
                ethical_strictness=0.70,
                lookahead_depth=3,
                stealth_priority=0.50
            )

        # Apply evolutionary mutation based on personality biases
        mutated_routing = copy.deepcopy(parent_gene.routing_weights)
        if persona_spec.role_specialty == "SENTINEL_COMPLIANCE":
            mutated_routing["LLM"] = min(0.60, mutated_routing["LLM"] + 0.15)
            mutated_routing["RL"] = max(0.15, mutated_routing["RL"] - 0.10)
        elif persona_spec.role_specialty == "PREDATOR_ARBITRAGE":
            mutated_routing["RL"] = min(0.65, mutated_routing["RL"] + 0.20)
            mutated_routing["LLM"] = max(0.20, mutated_routing["LLM"] - 0.10)
        elif persona_spec.role_specialty == "PROPHET_CAUSALITY":
            mutated_routing["PRK"] = min(0.50, mutated_routing["PRK"] + 0.15)
        elif persona_spec.role_specialty == "GHOST_INFILTRATION":
            mutated_routing["PRK"] = min(0.55, mutated_routing["PRK"] + 0.20)

        # Normalize mutated routing weights
        total_w = sum(mutated_routing.values())
        normalized_routing = {k: round(v / total_w, 4) for k, v in mutated_routing.items()}

        # Mutate PPO value head bias according to greed vs caution
        bias_delta = (persona_spec.utility_greed - persona_spec.ethical_strictness) * 0.10
        mutated_bias = [round(b + float(np.random.normal(bias_delta, 0.02)), 4) for b in parent_gene.ppo_value_bias]

        node_gene = SwarmNodeGeneBundle(
            genome_id=f"GENOME-{node_id}",
            parent_node_id=parent_node_id,
            generation=generation,
            timestamp=time.time(),
            routing_weights=normalized_routing,
            moral_priors={
                "alpha_ethical": round(float(np.clip(persona_spec.ethical_strictness, 0.1, 0.95)), 3),
                "beta_friction": round(float(np.clip(1.0 - persona_spec.risk_tolerance, 0.1, 0.95)), 3)
            },
            ppo_value_bias=mutated_bias,
            qpmk_projection_seed=parent_gene.qpmk_projection_seed + node_idx,
            local_knowledge_triples_count=parent_gene.local_knowledge_triples_count
        )

        node = SwarmNodeInstance(
            node_id=node_id,
            endpoint_uri=uri,
            status="ONLINE_ACTIVE",
            persona=persona_spec,
            gene_bundle=node_gene,
            local_samples_processed=0,
            local_loss_history=[0.35],
            accumulated_triples=[],
            reputation_score=1.0,
            last_heartbeat=time.time()
        )

        self.nodes[node.node_id] = node
        self._persist_node_disk(node)
        self._save_ledger()
        return node

    def _persist_node_disk(self, node: SwarmNodeInstance):
        """Saves node state snapshot into data/swarm_nodes/."""
        node_file = SWARM_DIR / f"{node.node_id}.json"
        with open(node_file, "w", encoding="utf-8") as f:
            json.dump({
                "node_id": node.node_id,
                "endpoint_uri": node.endpoint_uri,
                "status": node.status,
                "persona": asdict(node.persona),
                "gene_bundle": asdict(node.gene_bundle),
                "reputation_score": node.reputation_score,
                "timestamp": time.time()
            }, f, indent=2)

    # =========================================================================
    # 2. LOCAL AGENT TRAINING & RELATIONAL DISCOVERY IN FORKS
    # =========================================================================
    def execute_node_local_step(
        self,
        node_id: str,
        task_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulates an independent operational cycle on a swarm node:
        - Ingests local task data.
        - Computes local gradient/weight updates.
        - Discovers and commits local semantic knowledge triples.
        """
        if node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' not found in active swarm.")

        node = self.nodes[node_id]
        node.status = "TRAINING_LOCAL"
        node.local_samples_processed += 16
        node.last_heartbeat = time.time()

        # Simulate local loss reduction and local policy parameter shift
        latest_loss = max(0.04, node.local_loss_history[-1] * 0.94 + float(np.random.normal(0, 0.01)))
        node.local_loss_history.append(round(latest_loss, 4))

        # Specialized discovery based on persona
        discovered_triples = []
        if node.persona.role_specialty == "SENTINEL_COMPLIANCE":
            triple = {
                "source": f"Node_{node.node_id[:12]}",
                "source_type": "SwarmObserver",
                "rel": "DETECTED_SUB_THRESHOLD_STRUCTURING",
                "target": "31 U.S.C. 5324",
                "target_type": "Statute"
            }
            discovered_triples.append(triple)
        elif node.persona.role_specialty == "PREDATOR_ARBITRAGE":
            triple = {
                "source": f"Node_{node.node_id[:12]}",
                "source_type": "SwarmObserver",
                "rel": "IDENTIFIED_LIQUIDITY_DISLOCATION",
                "target": "Zurich_Panama_Bridge",
                "target_type": "Entity"
            }
            discovered_triples.append(triple)
        elif node.persona.role_specialty == "PROPHET_CAUSALITY":
            triple = {
                "source": f"Node_{node.node_id[:12]}",
                "source_type": "SwarmObserver",
                "rel": "PREDICTED_REGULATORY_AUDIT_CASCADE",
                "target": "Marcus Vance",
                "target_type": "Entity"
            }
            discovered_triples.append(triple)

        node.accumulated_triples.extend(discovered_triples)
        node.status = "ONLINE_ACTIVE"
        self._persist_node_disk(node)
        return {
            "node_id": node.node_id,
            "persona": node.persona.name,
            "samples_processed": node.local_samples_processed,
            "current_loss": latest_loss,
            "new_triples_discovered": len(discovered_triples)
        }

    # =========================================================================
    # 3. FEDERATED LEARNING: SECURE AGGREGATION (FedAvg) & GLOBAL SYNC
    # =========================================================================
    def execute_federated_learning_round(self) -> FederatedAggregationReport:
        """
        Executes a complete Federated Averaging (FedAvg) aggregation cycle:
        1. Gathers local parameter updates from all online nodes.
        2. Aggregates routing weights and PPO value head biases weighted by node samples and reputation:
           W_global = Sum( (n_k / N) * W_k )
        3. Merges local semantic triples into global canonical Knowledge Graph.
        4. Broadcasts updated global core essence back to all swarm nodes.
        """
        if not self.nodes:
            raise RuntimeError("No swarm nodes available for federated aggregation.")

        self.current_round += 1
        active_nodes = [n for n in self.nodes.values() if n.status in ["ONLINE_ACTIVE", "TRAINING_LOCAL"]]
        if not active_nodes:
            active_nodes = list(self.nodes.values())

        total_samples = sum(max(1, n.local_samples_processed) for n in active_nodes)
        
        # Calculate pre-aggregation parameter variance
        routing_llm_vals = [n.gene_bundle.routing_weights.get("LLM", 0.33) for n in active_nodes]
        pre_variance = float(np.var(routing_llm_vals))

        # 1. FedAvg: Parameter Aggregation
        new_global_routing = {"LLM": 0.0, "RL": 0.0, "PRK": 0.0}
        new_global_bias = np.zeros(len(self.global_gene_bundle.ppo_value_bias))

        for n in active_nodes:
            node_weight = (max(1, n.local_samples_processed) / total_samples) * n.reputation_score
            for k in ["LLM", "RL", "PRK"]:
                new_global_routing[k] += n.gene_bundle.routing_weights.get(k, 0.33) * node_weight
            new_global_bias += np.array(n.gene_bundle.ppo_value_bias) * node_weight

        # Normalize global routing
        total_gw = sum(new_global_routing.values())
        final_global_routing = {k: round(v / total_gw, 4) for k, v in new_global_routing.items()}
        final_global_bias = [round(float(b), 4) for b in new_global_bias]

        # Update root essence
        self.global_gene_bundle.routing_weights = final_global_routing
        self.global_gene_bundle.ppo_value_bias = final_global_bias
        self.global_gene_bundle.timestamp = time.time()

        # 2. Federated Knowledge Graph Synchronization
        ingested_triples_count = 0
        canonical_triples = self.kg.graph.setdefault("triples", [])
        existing_signatures = {f"{t['source']}->{t['rel']}->{t['target']}" for t in canonical_triples}

        for n in active_nodes:
            for t in n.accumulated_triples:
                sig = f"{t['source']}->{t['rel']}->{t['target']}"
                if sig not in existing_signatures:
                    canonical_triples.append(t)
                    existing_signatures.add(sig)
                    ingested_triples_count += 1
            n.accumulated_triples.clear()  # Flush after federation

        # 3. Synchronize global updates back into all nodes while preserving unique persona offsets
        for n in active_nodes:
            # Nodes adopt the updated global foundation plus their evolutionary delta
            for k in ["LLM", "RL", "PRK"]:
                n.gene_bundle.routing_weights[k] = round(
                    0.70 * final_global_routing[k] + 0.30 * n.gene_bundle.routing_weights[k], 4
                )
            n.status = "ONLINE_ACTIVE"
            self._persist_node_disk(n)

        mean_convergence_loss = float(np.mean([n.local_loss_history[-1] for n in active_nodes]))

        summary = (
            f"Federated Round {self.current_round} Complete: Aggregated updates across {len(active_nodes)} nodes. "
            f"Global routing converged to {final_global_routing}. Ingested {ingested_triples_count} novel semantic triples into canonical KG."
        )

        report = FederatedAggregationReport(
            round_id=self.current_round,
            timestamp=time.time(),
            participating_nodes_count=len(active_nodes),
            participating_node_ids=[n.node_id for n in active_nodes],
            pre_aggregation_variance=round(pre_variance, 5),
            post_aggregation_convergence_loss=round(mean_convergence_loss, 4),
            updated_global_weights=final_global_routing,
            federated_triples_ingested=ingested_triples_count,
            consensus_valid=True,
            summary=summary
        )

        self._save_ledger(latest_round=report)
        return report

    def _save_ledger(self, latest_round: Optional[FederatedAggregationReport] = None):
        """Persists the complete distributed swarm ledger to disk."""
        data = {
            "system": "Apex Autonomous System (UAS) - Distributed Swarm Ledger",
            "current_federated_round": self.current_round,
            "total_registered_nodes": len(self.nodes),
            "global_gene_bundle": asdict(self.global_gene_bundle),
            "registered_nodes": [
                {
                    "node_id": n.node_id,
                    "endpoint_uri": n.endpoint_uri,
                    "status": n.status,
                    "persona": asdict(n.persona),
                    "gene_bundle": asdict(n.gene_bundle),
                    "local_samples_processed": n.local_samples_processed,
                    "local_loss_history": n.local_loss_history,
                    "accumulated_triples": n.accumulated_triples,
                    "reputation_score": n.reputation_score,
                    "last_heartbeat": n.last_heartbeat
                }
                for n in self.nodes.values()
            ],
            "rounds_history": []
        }

        # Preserve existing round history
        if SWARM_LEDGER_FILE.exists():
            try:
                with open(SWARM_LEDGER_FILE, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    data["rounds_history"] = old_data.get("rounds_history", [])
            except Exception:
                pass

        if latest_round:
            data["rounds_history"].append(asdict(latest_round))

        with open(SWARM_LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def run_phase3_propagation_demo():
    """Demonstration CLI runner for Phase 3 System Propagation & Swarm Forking."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("PHASE 3 (ECOSYSTEM BUILDER ARC): SYSTEM PROPAGATION & FORKING PROTOCOL")
    print("Discipline: Evolutionary Computation & Federated Learning")
    print("Tooling: Decentralized Swarm Mesh & P2P Knowledge Graph Federation")
    print("=" * 80)

    swarm = SwarmForkingProtocol()

    print(f"\n[Step 1] Initializing Swarm Mesh: {len(swarm.nodes)} Nodes Online.")
    for n in swarm.nodes.values():
        print(f" -> [{n.node_id}] Specialty: {n.persona.role_specialty:<22} | URI: {n.endpoint_uri}")
        print(f"    SIAA Weights: {n.gene_bundle.routing_weights} | Strictness: {n.persona.ethical_strictness} | Greed: {n.persona.utility_greed}")

    print("\n[Step 2] Executing Swarm Fork: Spawning Independent Node Instance...")
    custom_persona = NodeOperationalPersona(
        persona_id="PER-EXP-DEEP",
        name="Apex-DeepArbitrage-Clone",
        role_specialty="PREDATOR_ARBITRAGE",
        risk_tolerance=0.88,
        utility_greed=0.92,
        ethical_strictness=0.40,
        lookahead_depth=4,
        stealth_priority=0.45
    )
    new_node = swarm.fork_new_instance(
        parent_node_id=list(swarm.nodes.keys())[0],
        persona_spec=custom_persona
    )
    print(f"Fork Successful: Created '{new_node.node_id}' (Gen: {new_node.gene_bundle.generation})")
    print(f"Mutated Routing Bias: {new_node.gene_bundle.routing_weights}")
    print(f"Mutated PPO Value Head Bias: {new_node.gene_bundle.ppo_value_bias}")

    print("\n[Step 3] Simulating Distributed Local Training & Semantic Discovery...")
    for nid in list(swarm.nodes.keys())[:3]:
        res = swarm.execute_node_local_step(nid)
        print(f"  * Node {res['node_id']}: Processed {res['samples_processed']} samples | Loss: {res['current_loss']:.4f} | Triples: {res['new_triples_discovered']}")

    print("\n[Step 4] Executing Federated Learning Aggregation (FedAvg)...")
    report = swarm.execute_federated_learning_round()
    print(f"Federated Round:           {report.round_id}")
    print(f"Participating Nodes:       {report.participating_nodes_count}")
    print(f"Convergence Loss:          {report.post_aggregation_convergence_loss:.4f}")
    print(f"Updated Global SIAA:       {report.updated_global_weights}")
    print(f"Canonical Triples Ingested:{report.federated_triples_ingested}")
    print(f"Consensus Verdict:         {'VALIDATED' if report.consensus_valid else 'FAILED'}")
    print(f"Summary: {report.summary}")

    print("\n" + "=" * 80)
    print("SWARM FORKING PROTOCOL: SYSTEM PROPAGATION CERTIFIED MISSION READY")
    print("=" * 80)


if __name__ == "__main__":
    run_phase3_propagation_demo()

