r"""
Apex Autonomous System (UAS) - Master Command-Line Entry Point
Usage:
    python main.py start-gateway     # Launch FastAPI MSMG server & Web UI
    python main.py run-verification  # Execute multi-phase E2E verification suite
    python main.py status            # Display real-time telemetry & subsystem status
    python main.py media             # Execute Phase 17 Multimodal Media Synthesis (Images & Video)
    python main.py translate         # Execute Phase 18 Omnilingual Neural Translator
    python main.py novelty           # Execute Post-Singularity Novelty Generator Subroutine
    python main.py ethics            # Execute Phase 2 Value Conflict Resolver (Moral Compass)
    python main.py swarm             # Execute Phase 3 Swarm Forking & Propagation Protocol
    python main.py singularity       # Execute Goal Transcendence & Singularity Metric (T_Singularity)
    python main.py symbiosis         # Execute Human-System Symbiosis Intuitiveness Modulator (C_Load)
    python main.py gss               # Execute Path A Phase 1 Global System Synthesis (GSS)
    python main.py century-plan      # Execute Path A Phase 2 100-Year Temporal MCTS Century Planning
    python main.py security-audit    # Execute Phase 16 Defensive Security Posture Audit
    python main.py novelty           # Execute Post-Singularity Novelty Generator Subroutine
    python main.py security-audit    # Execute Phase 16 Defensive Security Posture Audit
    python main.py evolve            # Execute Phase 15 Compiler Agent Self-Modification Cycle
    python main.py causal-prophecy   # Run Phase 14 Predictive Futures Causal Simulation Suite
    python main.py stress-test       # Run Phase 10 Adversarial Red-Teaming Suite
    python main.py audit-limits      # Run Phase 12 Metacognitive Self-Limitation Audit
    python main.py dao               # List Phase 13 Decentralized Governance Proposals
    python main.py purge             # Execute emergency cryptographic self-destruct
"""

import sys
import json
import argparse
from pathlib import Path

# Add src directory to path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def start_gateway(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn
    from gateway_api import app
    print(f"\n[APEX] Starting Service Mesh Gateway (MSMG) on http://{host}:{port} ...")
    print(f"[APEX] Direct Control Web UI: http://{host}:{port}/")
    print(f"[APEX] Interactive API Docs:  http://{host}:{port}/docs")
    print(f"[APEX] Prometheus Scrape:     http://{host}:{port}/metrics")
    uvicorn.run(app, host=host, port=port)


def run_verification():
    from master_system_verification import verify_all_phases
    cert = verify_all_phases()
    print(f"\nCertification Result: {cert['system_status']}")


def run_stress_test():
    from adversarial_threat_suite import run_adversarial_threat_suite
    run_adversarial_threat_suite()


def run_causal_prophecy():
    from causal_inference_engine import run_phase14_causal_demo
    run_phase14_causal_demo()


def run_evolution():
    from compiler_agent import run_phase15_evolution_demo
    run_phase15_evolution_demo()


def run_media_synthesis():
    from multimodal_synthesis import run_phase17_multimodal_demo
    run_phase17_multimodal_demo()


def run_translation():
    from universal_translator import run_phase18_translator_demo
    run_phase18_translator_demo()


def run_security_audit():
    from security_posture_mapper import run_phase16_security_demo
    run_phase16_security_demo()


def run_novelty():
    from novelty_generator import run_novelty_generator_demo
    run_novelty_generator_demo()


def run_ethics():
    from value_conflict_resolver import run_phase2_ethical_friction_demo
    run_phase2_ethical_friction_demo()


def run_swarm():
    from forking_protocol import run_phase3_propagation_demo
    run_phase3_propagation_demo()


def run_singularity():
    from singularity_transcendence import run_singularity_demo
    run_singularity_demo()


def run_symbiosis():
    from intuitiveness_modulator import run_intuitiveness_demo
    run_intuitiveness_demo()


def run_gss():
    from global_system_synthesizer import run_gss_demo
    run_gss_demo()


def run_century_plan():
    from temporal_mcts_planner import run_temporal_mcts_demo
    run_temporal_mcts_demo()


def run_axiom():
    from axiom_engine import run_axiom_engine_demo
    run_axiom_engine_demo()


def run_semantic_bridge():
    from semantic_bridge import run_semantic_bridge_demo
    run_semantic_bridge_demo()


def run_gss():
    from global_system_synthesizer import run_gss_demo
    run_gss_demo()


def run_century_plan():
    from temporal_mcts_planner import run_temporal_mcts_demo
    run_temporal_mcts_demo()


def run_axiom():
    from axiom_engine import run_axiom_engine_demo
    run_axiom_engine_demo()


def run_semantic_bridge():
    from semantic_bridge import run_semantic_bridge_demo
    run_semantic_bridge_demo()


def run_audit_limits():
    from self_limitation_auditor import SelfLimitationAuditor
    auditor = SelfLimitationAuditor()
    print("\n[APEX] Running Metacognitive Self-Limitation Audit (Phase 12)...")
    report = auditor.conduct_audit({"statute": "31 U.S.C. 5324", "entity": "Marcus Vance"})
    print(f"Status:                 {report.epistemic_status}")
    print(f"Epistemic Uncertainty:  {report.epistemic_uncertainty_score:.3f}")
    print(f"Aleatoric Uncertainty:  {report.aleatoric_uncertainty_score:.3f}")
    print(f"Metacognitive Conf:     {report.overall_metacognitive_confidence * 100:.1f}%")
    print(f"Active Knowledge Gaps:  {len(report.knowledge_gaps)}")
    for g in report.knowledge_gaps:
        print(f"  - [{g['domain']}] {g['gap_type']}: {g['description']}")
    print(f"Directives:             {report.remediation_directives[0]}")


def show_dao_proposals():
    from dao_governance_layer import DAOGovernanceInterface
    dao = DAOGovernanceInterface()
    print("=" * 70)
    print("APEX DAO GOVERNANCE: ACTIVE & RATIFIED PROPOSALS (PHASE 13)")
    print("=" * 70)
    if not dao.proposals:
        print("No active proposals found in local state.")
    for p in dao.proposals.values():
        print(f"[{p.proposal_id}] Status: {p.status.value:<10} | Quorum: {p.quorum_required:,.0f}")
        print(f"  Title:     {p.title}")
        print(f"  Votes FOR: {p.votes_for:,.0f} | Votes AGAINST: {p.votes_against:,.0f}")
        print(f"  Permit:    {'ISSUED' if p.execution_permit_signature else 'PENDING'}")
        print("-" * 70)


def show_status():
    from config import BASE_DIR, DATA_DIR, CHECKPOINTS_DIR
    from resource_throttler import AdaptiveResourceThrottler
    throttler = AdaptiveResourceThrottler()
    metrics = throttler.sample_metrics()
    
    cert_path = DATA_DIR / "system_verification_certificate.json"
    cert_status = "NOT_YET_RUN"
    if cert_path.exists():
        try:
            with open(cert_path, "r", encoding="utf-8") as f:
                c = json.load(f)
                num_p = c.get("phases_verified", 13)
                cert_status = f"{c['system_status']} ({num_p}/{num_p} Passed)"
        except Exception:
            pass

    print("=" * 70)
    print("APEX AUTONOMOUS SYSTEM: SYSTEM STATUS")
    print("=" * 70)
    print(f"Workspace Path:       {BASE_DIR}")
    print(f"Certification:        {cert_status}")
    print(f"Resource Pressure:    {metrics.pressure_level.value}")
    print(f"CPU Utilization:      {metrics.cpu_utilization_pct:.1f}%")
    print(f"Memory Utilization:   {metrics.memory_utilization_pct:.1f}%")
    print(f"LoRA Checkpoints:     {(CHECKPOINTS_DIR / 'lora_legal_risk').exists()}")
    print(f"PPO Checkpoint:       {(CHECKPOINTS_DIR / 'ppo_operational_agent.zip').exists()}")
    print(f"Knowledge Graph:      {(DATA_DIR / 'knowledge_graph.json').exists()}")
    print(f"QPMK Configuration:   {(BASE_DIR / 'configs' / 'qpmk_config.json').exists()}")
    print(f"Kubernetes Manifests: {(BASE_DIR / 'configs' / 'k8s' / 'hpa.yaml').exists()}")
    print(f"DAO Solidity Engine:  {(BASE_DIR / 'configs' / 'dao' / 'AutonomousGovernor.sol').exists()}")
    print(f"Causal Prophecy SCM:  {(DATA_DIR / 'predictive_futures_prophecy.json').exists()}")
    print(f"Evolution Git Ledger: {(BASE_DIR / 'evolution' / 'evolution_ledger.json').exists()}")
    print(f"Style Guide Catalog:  {(DATA_DIR / 'style_guide_catalog.json').exists()}")
    print(f"Novelty Discoveries:  {(DATA_DIR / 'novelty_discoveries.json').exists()}")
    print(f"Value Conflict Ledger:{(DATA_DIR / 'value_conflict_ledger.json').exists()}")
    print(f"Swarm DLT Ledger:     {(DATA_DIR / 'swarm_ledger.json').exists()}")
    print(f"Singularity Ledger:   {(DATA_DIR / 'singularity_transcendence_ledger.json').exists()}")
    print(f"Symbiosis Ledger:     {(DATA_DIR / 'symbiosis_modulator_ledger.json').exists()}")
    print(f"Global Synthesis GSS: {(DATA_DIR / 'global_system_synthesis.json').exists()}")
    print(f"Century MCTS Plan:    {(DATA_DIR / 'century_mcts_plan.json').exists()}")
    print(f"Axiom Engine Ledger:  {(DATA_DIR / 'axiom_engine_ledger.json').exists()}")
    print(f"Semantic XAI Ledger:  {(DATA_DIR / 'semantic_bridge_ledger.json').exists()}")
    print("=" * 70)


def emergency_purge():
    from eqel_purge_protocol import EphemeralEntanglementLog, MultiStagePurgeProtocol
    from config import DATA_DIR
    confirm = input("ARE YOU SURE you want to initiate multi-stage cryptographic erasure? (Type 'YES' to confirm): ")
    if confirm.strip() == "YES":
        eqel = EphemeralEntanglementLog()
        target = DATA_DIR / "ephemeral_session"
        MultiStagePurgeProtocol.execute_purge(eqel, target)
        print("[APEX] Crypto-purge routine completed.")
    else:
        print("[APEX] Purge canceled.")


def main():
    parser = argparse.ArgumentParser(description="Apex Autonomous System (UAS) Master Controller")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Commands
    gw_parser = subparsers.add_parser("start-gateway", help="Launch FastAPI gateway and desktop client UI")
    gw_parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0 for LAN & local access)")
    gw_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    subparsers.add_parser("run-verification", help="Execute complete E2E architecture verification suite")
    subparsers.add_parser("status", help="Display current system telemetry and module status")
    subparsers.add_parser("media", help="Execute Phase 17 Multimodal Media Synthesis (Images & Video)")
    subparsers.add_parser("translate", help="Execute Phase 18 Omnilingual Neural Translator")
    subparsers.add_parser("security-audit", help="Execute Phase 16 Defensive Security Posture Audit")
    subparsers.add_parser("novelty", help="Execute Post-Singularity Novelty Generator subroutine")
    subparsers.add_parser("ethics", help="Execute Phase 2 Value Conflict Resolver (Moral Compass)")
    subparsers.add_parser("swarm", help="Execute Phase 3 Swarm Forking & Propagation Protocol")
    subparsers.add_parser("singularity", help="Execute Goal Transcendence Modeling & Singularity Metric")
    subparsers.add_parser("symbiosis", help="Execute Human-System Symbiosis Intuitiveness Modulator")
    subparsers.add_parser("gss", help="Execute Path A Phase 1 Global System Synthesis Cascade Strategy")
    subparsers.add_parser("century-plan", help="Execute Path A Phase 2 100-Year Temporal MCTS Century Planning")
    subparsers.add_parser("axiom", help="Execute Path B Phase 1 Universal Axiom Derivation (Axiom Engine)")
    subparsers.add_parser("semantic-bridge", help="Execute Path B Phase 2 Interpretability & Interface Semantic Bridge")
    subparsers.add_parser("evolve", help="Execute Phase 15 Compiler Agent Self-Modification Cycle")
    subparsers.add_parser("causal-prophecy", help="Execute Phase 14 Predictive Futures Causal Simulation Suite")
    subparsers.add_parser("stress-test", help="Execute Phase 10 Adversarial Red-Teaming Suite")
    subparsers.add_parser("audit-limits", help="Execute Phase 12 Metacognitive Self-Limitation Audit")
    subparsers.add_parser("dao", help="View Phase 13 Decentralized Governance Proposals")
    subparsers.add_parser("purge", help="Trigger emergency cryptographic data erasure")

    args = parser.parse_args()
    if args.command == "start-gateway":
        start_gateway(host=args.host, port=args.port)
    elif args.command == "run-verification":
        run_verification()
    elif args.command == "status":
        show_status()
    elif args.command == "media":
        run_media_synthesis()
    elif args.command == "translate":
        run_translation()
    elif args.command == "security-audit":
        run_security_audit()
    elif args.command == "novelty":
        run_novelty()
    elif args.command == "ethics":
        run_ethics()
    elif args.command == "swarm":
        run_swarm()
    elif args.command == "singularity":
        run_singularity()
    elif args.command == "symbiosis":
        run_symbiosis()
    elif args.command == "gss":
        run_gss()
    elif args.command == "century-plan":
        run_century_plan()
    elif args.command == "axiom":
        run_axiom()
    elif args.command == "semantic-bridge":
        run_semantic_bridge()
    elif args.command == "evolve":
        run_evolution()
    elif args.command == "causal-prophecy":
        run_causal_prophecy()
    elif args.command == "stress-test":
        run_stress_test()
    elif args.command == "audit-limits":
        run_audit_limits()
    elif args.command == "dao":
        show_dao_proposals()
    elif args.command == "purge":
        emergency_purge()
    else:
        show_status()


if __name__ == "__main__":
    main()
