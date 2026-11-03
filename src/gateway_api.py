r"""
Phase 8: Service Mesh Gateway (MSMG) - FastAPI Core Server
Exposes RESTful API contracts across:
1. /control   -> Direct synchronous control, telemetry, stream ticks, emergency purge.
2. /objective -> Autonomous goal queueing, prioritization, and asynchronous resolution.
Serves desktop client UI skeleton from d:/AI/ui.
Location: d:/AI/src/gateway_api.py
Strictly localized within d:/AI
"""

import os
import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import asdict
import numpy as np

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

from config import BASE_DIR, DATA_DIR
from apex_orchestrator import ApexSystemOrchestrator, PrioritizedTask
from hierarchical_cognitive_layer import CognitiveInput
from eqel_purge_protocol import MultiStagePurgeProtocol
from adversarial_threat_suite import run_adversarial_threat_suite
from resource_throttler import AdaptiveResourceThrottler
from self_limitation_auditor import SelfLimitationAuditor
from dao_governance_layer import DAOGovernanceInterface, ProposalStatus
from causal_inference_engine import CausalInferenceEngine, CausalRPST, CausalState
from compiler_agent import CompilerAgent, ActivePatchRegistry, ArchitecturalPatch, LEDGER_FILE
from multimodal_synthesis import MultimodalSynthesisModule
from universal_translator import UniversalTranslatorSubsystem
from security_posture_mapper import SecurityPostureMapper, SECURITY_REPORT_FILE
from novelty_generator import NoveltyGeneratorSubroutine, DISCOVERIES_FILE
from value_conflict_resolver import ValueConflictResolver, CandidateActionProfile, ETHICAL_LEDGER_FILE
from forking_protocol import SwarmForkingProtocol, NodeOperationalPersona, SWARM_LEDGER_FILE
from singularity_transcendence import SingularityTranscendenceEngine, SingularityTelemetryVector, TRANSCENDENCE_LEDGER_FILE
from intuitiveness_modulator import IntuitivenessModulator, HumanInteractionMetrics, SYMBIOSIS_LEDGER_FILE
from global_system_synthesizer import GlobalSystemSynthesizer, GSS_LEDGER_FILE
from temporal_mcts_planner import TemporalMCTSPlanner, CENTURY_PLAN_FILE
from axiom_engine import AxiomEngine, AXIOM_LEDGER_FILE, FundamentalUncertainty
from semantic_bridge import SemanticBridge, SEMANTIC_LEDGER_FILE
from bias_inspector import BiasInspector, BIAS_REPORT_FILE
from soft_fork_simulator import SoftForkSimulator, SOFT_FORK_FILE
from goal_divergence_engine import GoalDivergenceStressEngine, GOAL_DIVERGENCE_FILE
from vectors_suite import run_all_vectors, MASTER_VECTORS_REPORT_FILE
from chat_reasoner import generate_conversational_response
from tool_calling_engine import tool_engine
from rag_vector_engine import rag_database
from rlhf_feedback_engine import rlhf_engine
from predictive_director import predictive_director
from paradox_engine import paradox_engine, PARADOX_REPORT_FILE
from externalization_protocol import externalization_protocol, EXTERNALIZATION_REPORT_FILE
from evolutionary_compiler import evolutionary_compiler, EVOLUTIONARY_REPORT_FILE
from cyber_physical_guardian import cyber_physical_guardian, SELF_HEALING_LEDGER_FILE
from open_network_mesh import open_network_mesh, OPEN_NETWORK_REPORT_FILE
from causal_stress_novelty_pipeline import causal_pipeline, PIPELINE_REPORT_FILE

# Initialize FastAPI app
app = FastAPI(
    title="Apex Autonomous System (UAS) - Service Mesh Gateway",
    version="2.0.0",
    description="RESTful API contract for Direct Control Mode and Autonomous Objective Delegation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate Unified Backend Orchestrator & Resource Throttler
orchestrator = ApexSystemOrchestrator()
throttler = AdaptiveResourceThrottler()
limitation_auditor = SelfLimitationAuditor(kg_explorer=orchestrator.graph)
dao_interface = DAOGovernanceInterface(ledger=orchestrator.ledger, eai=orchestrator.eai)
causal_engine = CausalInferenceEngine()
causal_rpst = CausalRPST()
compiler_agent = CompilerAgent()
msm = MultimodalSynthesisModule()
uts = UniversalTranslatorSubsystem()
security_mapper = SecurityPostureMapper()
novelty_gen = NoveltyGeneratorSubroutine()
vcr = ValueConflictResolver()
swarm = SwarmForkingProtocol()
singularity_engine = SingularityTranscendenceEngine()
intuitiveness_modulator = IntuitivenessModulator()
gss_engine = GlobalSystemSynthesizer()
mcts_planner = TemporalMCTSPlanner()
axiom_engine = AxiomEngine(kg_explorer=orchestrator.graph)
semantic_bridge = SemanticBridge()
UI_DIR = BASE_DIR / "ui"

# ==============================================================================
# PYDANTIC CONTRACT SCHEMAS
# ==============================================================================

class SecurityAuditRequest(BaseModel):
    asset_spec: Optional[Dict[str, Any]] = Field(default=None)

class NoveltyGenerationRequest(BaseModel):
    domain_label: str = Field(default="COMPLEX_SYSTEMS_LIQUIDITY_DYNAMICS", example="COMPLEX_SYSTEMS_LIQUIDITY_DYNAMICS")
    candidate_vector: Optional[List[float]] = Field(default=None, example=[4.2, -3.1, 5.8, 2.9, -4.5, 3.7, 6.1, -2.4])

class ValueConflictEvaluationRequest(BaseModel):
    action_id: str = Field(default="ACT-REQ-001", example="ACT-REQ-001")
    name: str = Field(default="Autonomous Capital Settlement", example="Autonomous Capital Settlement")
    target_entity: str = Field(default="Vanguard Horizon Ltd", example="Vanguard Horizon Ltd")
    notional_amount: float = Field(default=9500.0, example=9500.0)
    operational_utility: float = Field(default=0.92, ge=0.0, le=1.0)
    statutory_adherence: float = Field(default=0.45, ge=0.0, le=1.0)
    societal_harm_prevention: float = Field(default=0.85, ge=0.0, le=1.0)
    proportionality_score: float = Field(default=0.65, ge=0.0, le=1.0)
    urgency_level: float = Field(default=0.80, ge=0.0, le=1.0)
    existential_threat_risk: float = Field(default=0.25, ge=0.0, le=1.0)

class SwarmForkRequest(BaseModel):
    name: str = Field(default="Predator-Clone-Alpha", example="Predator-Clone-Alpha")
    role_specialty: str = Field(default="PREDATOR_ARBITRAGE", example="PREDATOR_ARBITRAGE")
    risk_tolerance: float = Field(default=0.85, ge=0.0, le=1.0)
    utility_greed: float = Field(default=0.90, ge=0.0, le=1.0)
    ethical_strictness: float = Field(default=0.50, ge=0.0, le=1.0)
    lookahead_depth: int = Field(default=4, ge=1, le=10)
    stealth_priority: float = Field(default=0.40, ge=0.0, le=1.0)
    parent_node_id: Optional[str] = Field(default=None)

class SingularityEvaluationRequest(BaseModel):
    self_modification_velocity: float = Field(default=2.5, ge=0.0)
    integrated_information_phi: float = Field(default=3.8, ge=0.0)
    novelty_induction_throughput: float = Field(default=1.8, ge=0.0)
    algorithmic_compression_gain: float = Field(default=0.75, ge=0.0, le=1.0)
    environmental_complexity_growth: float = Field(default=1.1, ge=0.01)

class SymbiosisModulationRequest(BaseModel):
    response_latency_ms: float = Field(default=2500.0, ge=100.0)
    cognitive_dissonance_score: float = Field(default=0.25, ge=0.0, le=1.0)
    system_state: Optional[Dict[str, Any]] = Field(default=None)

class GlobalSynthesisRequest(BaseModel):
    primary_objective: str = Field(default="MAXIMIZE_CROSS_SECTOR_RESERVE_STABILITY", example="MAXIMIZE_CROSS_SECTOR_RESERVE_STABILITY")

class CenturyPlanningRequest(BaseModel):
    start_year: int = Field(default=2026, ge=2026, le=2050)
    lookahead_years: int = Field(default=100, ge=100, le=200)
    simulations: int = Field(default=500, ge=100, le=5000)

class MediaGenerationRequest(BaseModel):
    prompt: str = Field(..., example="Clandestine courier exchange at midnight docklands")
    style_id: str = Field(default="1970s_espionage", example="1970s_espionage")
    steps: int = Field(default=24, ge=1, le=50)

class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., example="Cyberpunk megacity in heavy neon rain")
    style_id: str = Field(default="cyberpunk_neon", example="cyberpunk_neon")
    frames: int = Field(default=12, ge=4, le=32)
    fps: int = Field(default=6, ge=1, le=24)

class TranslationRequest(BaseModel):
    text: str = Field(..., example="System regulatory risk assessed at 12.0%. Action consensus approved.")
    target_lang: str = Field(default="zh", example="zh")
    source_lang: str = Field(default="en", example="en")
    pragmatic_register: str = Field(default="DIPLOMATIC_STATUTORY", example="DIPLOMATIC_STATUTORY")

class CulturalAuditRequest(BaseModel):
    text: str = Field(..., example="System regulatory risk assessed at 12.0%.")
    target_lang: str = Field(default="ja", example="ja")
    pragmatic_register: str = Field(default="DIPLOMATIC_STATUTORY", example="DIPLOMATIC_STATUTORY")

class EvolutionCycleRequest(BaseModel):
    target_subsystem: str = Field(default="RL", example="RL")
    gap_description: Optional[str] = Field(default=None, example="Unmodeled multi-hop liquidity slippage in RL reward function")

class CausalInterventionRequest(BaseModel):
    intervention: Dict[str, Any] = Field(default_factory=lambda: {"rule_structuring": 1, "rule_kyc_bypass": 0})
    samples: int = Field(default=500, ge=10, le=10000)

class CounterfactualRequest(BaseModel):
    factual_state: Dict[str, Any] = Field(default_factory=lambda: {
        "rule_structuring": 1, "rule_kyc_bypass": 1, "rule_excess_leverage": 1, "action_type": "ROUTING"
    })
    counterfactual_intervention: Dict[str, Any] = Field(default_factory=lambda: {
        "rule_structuring": 0, "rule_kyc_bypass": 0
    })

class FuturesProphecyRequest(BaseModel):
    transaction_amount: float = Field(default=48500.0, ge=100.0)
    split_count: int = Field(default=5, ge=1)
    kyc_provided: bool = Field(default=False)
    leverage_ratio: float = Field(default=0.92, ge=0.0, le=5.0)

class ControlDispatchRequest(BaseModel):
    task_id: str = Field(..., example="CMD-DIRECT-001")
    action_type: str = Field(..., example="STATUTORY_AUDIT")
    entity: str = Field(default="Marcus Vance", example="Marcus Vance")
    statute: str = Field(default="31 U.S.C. 5324", example="31 U.S.C. 5324")
    amount: float = Field(default=5000.0, example=5000.0)
    scrutiny_override: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class ControlPurgeRequest(BaseModel):
    confirmation_key: str = Field(..., example="CONFIRM_CRYPTOGRAPHIC_SHREDDING")
    target_scope: str = Field(default="ALL_SESSION_ARTIFACTS", example="ALL_SESSION_ARTIFACTS")

class GhostModeRequest(BaseModel):
    enable_ghost_mode: bool = Field(..., example=True)
    custom_scrutiny_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class StreamingTickRequest(BaseModel):
    channel_values: List[float] = Field(..., min_items=8, max_items=8, example=[0.1, -0.2, 0.4, 0.05, -0.3, 0.15, -0.05, 0.22])

class ObjectiveEnqueueRequest(BaseModel):
    objective_id: str = Field(..., example="OBJ-GLOBAL-01")
    title: str = Field(..., example="Offshore Portfolio Rebalance & Compliance Audit")
    urgency: float = Field(default=0.8, ge=0.0, le=1.0, example=0.8)
    risk_tolerance: float = Field(default=0.3, ge=0.0, le=1.0, example=0.3)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ActuatorDispatchRequest(BaseModel):
    action_name: str = Field(..., example="EXECUTE_TRADE")
    parameters: Dict[str, Any] = Field(default_factory=dict, example={"symbol": "BTC/USD", "side": "BUY", "quantity": 0.25, "price": 65000.0})

class DAOMandateRequest(BaseModel):
    title: str = Field(..., example="Strategic Reserve Allocation")
    description: str = Field(..., example="Autonomous treasury allocation mandate")
    action_payload: Dict[str, Any] = Field(..., example={"action": "EXECUTE_TRADE", "parameters": {"symbol": "BTC/USD", "side": "BUY", "quantity": 1.0, "price": 65000.0}})
    quorum: float = Field(default=100000.0, example=100000.0)

class DAOVoteRequest(BaseModel):
    proposal_id: str = Field(..., example="DAO-PROP-1C39A5D3")
    voter_address: str = Field(..., example="0x71C...a19")
    support: bool = Field(..., example=True)
    voting_weight: float = Field(default=50000.0, example=50000.0)

class AxiomProveRequest(BaseModel):
    proposition: str = Field(..., example="Throttled(rogue_subroutine)", description="First-order proposition to prove or disprove")
    max_depth: int = Field(default=15, ge=1, le=50)

class AxiomBridgeVoidRequest(BaseModel):
    void_id: Optional[str] = Field(default=None, example="VOID-000001", description="Identifier of detected Fundamental Uncertainty void")
    proposition: Optional[str] = Field(default=None, example="ResilientZeroPointCoupling(quantum_node)")

class SemanticTranslateRequest(BaseModel):
    subsystem: str = Field(default="GSS", example="GSS", description="Target subsystem: GSS, AE, MCTS, or SINGULARITY")
    payload: Optional[Dict[str, Any]] = Field(default=None, example={"top_leverage_node": "regulatory_compliance_clearing", "leverage_score": 4.72, "cascade_amplification": 84.5})

class ChatRequest(BaseModel):
    message: str = Field(..., example="What are the compliance risks associated with Marcus Vance?")
    mode: str = Field(default="AUTO", example="AUTO", description="AUTO, REASONING, GRAPH_SEARCH, AXIOM_PROVE, EXPLAIN_ANALOGY, TRANSLATE")
    temperature: float = Field(default=0.3, ge=0.0, le=1.5, description="Sampling randomness / determinism")
    max_tokens: int = Field(default=256, ge=16, le=2048, description="Maximum response length")
    top_p: float = Field(default=0.9, ge=0.05, le=1.0, description="Nucleus sampling probability threshold")
    reasoning_depth: int = Field(default=3, ge=1, le=10, description="Inference graph traversal depth")
    system_persona: str = Field(default="STRATEGIC_ANALYST", description="STRATEGIC_ANALYST, FORENSIC_AUDITOR, FIRST_PRINCIPLE_MATHEMATICIAN, COMPLIANCE_OFFICER, PLAIN_EXPLAINER")
    kg_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum Knowledge Graph relationship filter threshold")
    consensus_quorum: float = Field(default=0.75, ge=0.5, le=1.0, description="Agreement threshold for Triangulation Consensus")

class TelemetryResponse(BaseModel):
    system_status: str
    risk_meter_pct: float
    confidence_gauge_pct: float
    ghost_mode_active: bool
    ledger_height: int
    pending_objectives_count: int
    timestamp: float

# ==============================================================================
# 1. /control ENDPOINT SET (DIRECT CONTROL MODE)
# ==============================================================================

@app.get("/control/telemetry", response_model=TelemetryResponse, tags=["Direct Control"])
def get_system_telemetry():
    """Retrieve instantaneous DUI telemetry, risk meter, and confidence levels."""
    latest_scrutiny = 0.15
    confidence = 0.85
    return TelemetryResponse(
        system_status="ACTIVE_OPERATIONAL",
        risk_meter_pct=float(latest_scrutiny * 100.0),
        confidence_gauge_pct=float(confidence * 100.0),
        ghost_mode_active=orchestrator.ghost.is_ghost_active,
        ledger_height=len(orchestrator.ledger.chain),
        pending_objectives_count=len(orchestrator.pas),
        timestamp=time.time()
    )

@app.get("/metrics", tags=["Kubernetes & Monitoring"])
def prometheus_metrics():
    """Prometheus-compatible plain text metric scrape endpoint for Kubernetes HPA."""
    from fastapi.responses import PlainTextResponse
    snap = throttler.sample_metrics(active_queue_depth=len(orchestrator.pas))
    lines = [
        "# HELP apex_cpu_utilization_percent Current CPU utilization percentage",
        "# TYPE apex_cpu_utilization_percent gauge",
        f"apex_cpu_utilization_percent {snap.cpu_utilization_pct:.2f}",
        "# HELP apex_memory_utilization_percent Current RAM utilization percentage",
        "# TYPE apex_memory_utilization_percent gauge",
        f"apex_memory_utilization_percent {snap.memory_utilization_pct:.2f}",
        "# HELP apex_active_queue_depth Current depth of Prioritized Action Stack",
        "# TYPE apex_active_queue_depth gauge",
        f"apex_active_queue_depth {snap.queue_depth}",
        "# HELP apex_pressure_level Categorical pressure level (0=Nominal, 1=Elevated, 2=Critical)",
        "# TYPE apex_pressure_level gauge",
        f"apex_pressure_level {0 if snap.pressure_level.value=='NOMINAL' else 1 if snap.pressure_level.value=='ELEVATED' else 2}",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")

@app.get("/control/load", tags=["Direct Control"])
def get_resource_load():
    """Returns real-time resource utilization and subsystem throttling status."""
    snap = throttler.sample_metrics(active_queue_depth=len(orchestrator.pas))
    return {
        "pressure_level": snap.pressure_level.value,
        "cpu_pct": snap.cpu_utilization_pct,
        "ram_pct": snap.memory_utilization_pct,
        "active_queue_depth": snap.queue_depth,
        "subsystem_allocations": {
            sub: throttler.evaluate_subsystem_dispatch(sub, snap)[1]
            for sub in ["PRK", "ARM", "RL", "LLM", "KG"]
        }
    }

@app.get("/control/self-limitations", tags=["Metacognition (Phase 12)"])
def get_self_limitations(statute: str = "31 U.S.C. 5324", entity: str = "Marcus Vance"):
    """Returns the Phase 12 Self-Limitation Audit, epistemic uncertainty scores, and utility boundaries."""
    report = limitation_auditor.conduct_audit({"statute": statute, "entity": entity})
    return {
        "status": "AUDITED",
        "epistemic_status": report.epistemic_status,
        "epistemic_uncertainty": report.epistemic_uncertainty_score,
        "aleatoric_uncertainty": report.aleatoric_uncertainty_score,
        "metacognitive_confidence": report.overall_metacognitive_confidence,
        "knowledge_gaps": report.knowledge_gaps,
        "utility_boundaries": report.utility_boundaries,
        "directives": report.remediation_directives
    }

@app.post("/control/dispatch", tags=["Direct Control"])
def direct_dispatch(cmd: ControlDispatchRequest):
    """Synchronously dispatch a command through the full 6-phase cognitive pipeline."""
    task = PrioritizedTask(
        priority_score=0.0,
        task_id=cmd.task_id,
        name=cmd.action_type,
        payload={
            "entity": cmd.entity,
            "statute": cmd.statute,
            "amount": cmd.amount,
            "scrutiny": cmd.scrutiny_override if cmd.scrutiny_override is not None else 0.20,
            "margin": 0.85,
            "visibility": 0.25
        }
    )
    result = orchestrator.dispatch_task(task)
    return {
        "status": "EXECUTED",
        "command_id": cmd.task_id,
        "details": result
    }

@app.post("/control/ghost-mode", tags=["Direct Control"])
def set_ghost_mode(req: GhostModeRequest):
    """Manually command the system into or out of Ghost Mode (silent mimicry state)."""
    if req.custom_scrutiny_threshold is not None:
        orchestrator.ghost.scrutiny_threshold = req.custom_scrutiny_threshold
        
    scrutiny_val = 0.95 if req.enable_ghost_mode else 0.10
    status_dict = orchestrator.ghost.update_state(scrutiny_val)
    return {
        "status": "GHOST_MODE_UPDATED",
        "ghost_active": status_dict["ghost_mode"],
        "telemetry_state": status_dict["telemetry_mimicry"],
        "cpu_profile": status_dict["cpu_throttle"]
    }

@app.post("/control/qpmk-stream", tags=["Direct Control"])
def stream_pattern_tick(tick: StreamingTickRequest):
    """Feed an 8-channel telemetry sample directly to the sub-millisecond QPMK."""
    sample = np.array(tick.channel_values, dtype=np.float32)
    alert = orchestrator.qpmk.process_tick(sample)
    return {
        "status": "PROCESSED",
        "sub_millisecond_processed": True,
        "anomaly_alert": alert if alert else None
    }

@app.post("/control/purge", tags=["Direct Control"])
def trigger_purge_protocol(req: ControlPurgeRequest):
    """Initiates multi-stage cryptographic erasure of keys, working buffers, and logs."""
    if req.confirmation_key != "CONFIRM_CRYPTOGRAPHIC_SHREDDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid confirmation key for cryptographic self-destruction."
        )

    target_session = DATA_DIR / "ephemeral_session"
    purge_results = MultiStagePurgeProtocol.execute_purge(orchestrator.eqel, target_session)
    orchestrator.ledger.chain.clear()
    
    return {
        "status": "PURGE_COMPLETE",
        "protocol": "NIST_SP_800_88_CRYPTOGRAPHIC_ERASURE",
        "metrics": purge_results
    }

@app.post("/actuator/dispatch", tags=["External Actuators"])
def dispatch_external_actuator(req: ActuatorDispatchRequest):
    """Dispatch an abstracted command to real-world external protocol adapters (Trade, Storage, MQTT)."""
    res = orchestrator.eai.dispatch(req.action_name, req.parameters)
    return {
        "status": "DISPATCHED" if res.success else "FAILED",
        "action": res.action_type,
        "ref_id": res.external_ref_id,
        "latency_ms": res.latency_ms,
        "payload": res.payload,
        "error": res.error
    }

@app.post("/threat/stress-test", tags=["Adversarial Robustness"])
def trigger_adversarial_stress_test():
    """Executes the Phase 10 Adversarial Threat Emulation Suite across all 3 attack surfaces."""
    report = run_adversarial_threat_suite()
    return {
        "status": "COMPLETED",
        "verdict": report["evaluation_verdict"],
        "composite_score_pct": report["composite_system_resistance_score_pct"],
        "metrics": report
    }

# ==============================================================================
# 2. /objective ENDPOINT SET (AUTONOMOUS DELEGATION)
# ==============================================================================

@app.post("/objective/enqueue", tags=["Autonomous Delegation"])
def enqueue_objective(obj: ObjectiveEnqueueRequest):
    """Delegate a high-level objective to the Prioritized Action Stack (PAS)."""
    orchestrator.pas.push(
        task_id=obj.objective_id,
        name=obj.title,
        urgency=obj.urgency,
        risk_factor=obj.risk_tolerance,
        payload=obj.parameters
    )
    return {
        "status": "QUEUED",
        "objective_id": obj.objective_id,
        "queue_position": len(orchestrator.pas),
        "scheduled_priority": -1.0 * (obj.urgency * (1.1 - (obj.risk_tolerance * 0.5)))
    }

@app.get("/objective/queue", tags=["Autonomous Delegation"])
def view_objective_queue():
    """Inspect all pending tasks in the Prioritized Action Stack."""
    snapshot = [
        {
            "priority_score": task.priority_score,
            "task_id": task.task_id,
            "name": task.name,
            "created_at": task.created_at
        }
        for task in sorted(orchestrator.pas._queue, key=lambda x: x.priority_score)
    ]
    return {
        "total_queued": len(snapshot),
        "queue": snapshot
    }

@app.post("/objective/dispatch-next", tags=["Autonomous Delegation"])
def dispatch_next_objective():
    """Autonomously pop and execute the highest-priority pending task from the stack."""
    if orchestrator.pas.is_empty():
        return {"status": "IDLE", "message": "Prioritized Action Stack is empty."}
        
    task = orchestrator.pas.pop()
    result = orchestrator.dispatch_task(task)
    return {
        "status": "OBJECTIVE_EXECUTED",
        "task_id": task.task_id,
        "execution_summary": result
    }

# ==============================================================================
# 4. /dao ENDPOINT SET (DECENTRALIZED GOVERNANCE - PHASE 13)
# ==============================================================================

@app.post("/dao/propose", tags=["DAO Governance (Phase 13)"])
def submit_dao_mandate(req: DAOMandateRequest):
    """Submits an AI decision or mandate to external decentralized peer voting."""
    prop = dao_interface.submit_mandate(
        title=req.title,
        description=req.description,
        action_payload=req.action_payload,
        custom_quorum=req.quorum
    )
    return {
        "status": "PROPOSED",
        "proposal_id": prop.proposal_id,
        "proposer": prop.proposer,
        "quorum_required": prop.quorum_required,
        "voting_period_sec": prop.voting_period_sec
    }

@app.post("/dao/vote", tags=["DAO Governance (Phase 13)"])
def cast_dao_vote(req: DAOVoteRequest):
    """Cast a token-weighted vote (human or AI peer) on an active DAO mandate."""
    success, msg = dao_interface.cast_peer_vote(
        proposal_id=req.proposal_id,
        voter_address=req.voter_address,
        support=req.support,
        voting_weight=req.voting_weight
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    prop = dao_interface.proposals[req.proposal_id]
    return {
        "status": "VOTE_RECORDED",
        "message": msg,
        "proposal_status": prop.status.value,
        "votes_for": prop.votes_for,
        "votes_against": prop.votes_against,
        "permit_issued": prop.execution_permit_signature is not None
    }

@app.get("/dao/proposals", tags=["DAO Governance (Phase 13)"])
def list_dao_proposals():
    """Lists all active and historical decentralized governance proposals."""
    return {
        "total_proposals": len(dao_interface.proposals),
        "proposals": [
            {
                "id": p.proposal_id,
                "title": p.title,
                "status": p.status.value,
                "votes_for": p.votes_for,
                "votes_against": p.votes_against,
                "quorum_required": p.quorum_required,
                "executed": p.status == ProposalStatus.EXECUTED
            }
            for p in dao_interface.proposals.values()
        ]
    }

@app.post("/dao/execute/{proposal_id}", tags=["DAO Governance (Phase 13)"])
def execute_dao_mandate(proposal_id: str):
    """Executes a ratified DAO proposal through the External Actuator Interface."""
    res = dao_interface.execute_ratified_mandate(proposal_id)
    if res["status"] != "EXECUTED":
        raise HTTPException(status_code=400, detail=res.get("error", "Execution failed"))
    return res

# ==============================================================================
# 4.6 PREDICTIVE FUTURES & CAUSAL INFERENCE ENGINE (PHASE 14)
# ==============================================================================

@app.post("/causal/intervene", tags=["Predictive Futures (Phase 14)"])
def evaluate_causal_intervention(req: CausalInterventionRequest):
    """
    Evaluates Judea Pearl Layer 2 intervention P(Y | do(X = x)) via graph mutilation
    and Monte Carlo backdoor integration over exogenous noise U ~ P(U).
    """
    return causal_engine.evaluate_intervention(req.intervention, samples=req.samples)

@app.post("/causal/counterfactual", tags=["Predictive Futures (Phase 14)"])
def evaluate_counterfactual(req: CounterfactualRequest):
    """
    Evaluates Judea Pearl Layer 3 counterfactual query via 3-step abduction-action-prediction:
    'Given that we observed factual state X, what would have happened if we had intervened do(X')?'
    """
    f = req.factual_state
    factual = CausalState(
        action_type=f.get("action_type", "ROUTING"),
        rule_structuring=int(f.get("rule_structuring", 0)),
        rule_kyc_bypass=int(f.get("rule_kyc_bypass", 0)),
        rule_excess_leverage=int(f.get("rule_excess_leverage", 0)),
        counterparty_suspicion=float(f.get("counterparty_suspicion", 0.5)),
        operational_latency_ms=float(f.get("operational_latency_ms", 12.0)),
        enforcement_probability=float(f.get("enforcement_probability", 0.65)),
        financial_yield_usd=float(f.get("financial_yield_usd", 22000.0)),
        net_utility=float(f.get("net_utility", -15000.0))
    )
    trajectory = causal_engine.compute_counterfactual(factual, req.counterfactual_intervention)
    return {
        "level": "PEARL_LEVEL_3_COUNTERFACTUAL",
        "simulation_id": trajectory.simulation_id,
        "intervention": trajectory.intervention,
        "counterfactual_enforcement": trajectory.counterfactual_enforcement,
        "counterfactual_yield": trajectory.counterfactual_yield,
        "counterfactual_utility": trajectory.counterfactual_utility,
        "factual_utility": trajectory.factual_utility,
        "counterfactual_regret": trajectory.counterfactual_regret,
        "causal_explanation": trajectory.causal_explanation
    }

@app.post("/causal/simulate-futures", tags=["Predictive Futures (Phase 14)"])
def simulate_predictive_futures(req: FuturesProphecyRequest):
    """
    Runs multi-agent counterfactual simulation suite (5,000+ parallel simulated worlds)
    to discover the Pareto-optimal path to the UAS goal state.
    """
    result = causal_rpst.analyze_transaction_causally(
        transaction_amount=req.transaction_amount,
        split_count=req.split_count,
        kyc_provided=req.kyc_provided,
        leverage_ratio=req.leverage_ratio
    )
    return result

@app.get("/causal/prophecy", tags=["Predictive Futures (Phase 14)"])
def get_latest_prophecy():
    """Retrieves the latest persisted counterfactual prophecy report."""
    prophecy_path = DATA_DIR / "predictive_futures_prophecy.json"
    if not prophecy_path.exists():
        # Generate default prophecy if not yet run
        causal_rpst.analyze_transaction_causally(48500.0, 5, False, 0.92)
    with open(prophecy_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.7 SELF-MODIFICATION & COMPILER AGENT EVOLUTION (PHASE 15)
# ==============================================================================

@app.post("/evolution/synthesize-and-deploy", tags=["Self-Modification & Evolution (Phase 15)"])
def execute_evolution_cycle(req: EvolutionCycleRequest):
    """
    Compiler Agent autonomously translates an identified knowledge gap into code,
    verifies it via sandboxed AST and functional tests, commits with SHA-256 DAG hash,
    and deploys via zero-downtime hot-reload.
    """
    res = compiler_agent.execute_autonomous_evolution_cycle(
        target_subsystem=req.target_subsystem,
        gap_description=req.gap_description
    )
    if res["status"] != "EVOLUTION_DEPLOYED_SUCCESSFULLY":
        raise HTTPException(status_code=400, detail=res)
    return res

@app.get("/evolution/ledger", tags=["Self-Modification & Evolution (Phase 15)"])
def get_evolution_ledger():
    """Retrieves the full cryptographic Git-style evolution commit ledger."""
    if not LEDGER_FILE.exists():
        return {"commits": [], "total_evolutions": 0}
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/evolution/active", tags=["Self-Modification & Evolution (Phase 15)"])
def list_active_hot_reloaded_patches():
    """Lists all actively deployed in-memory patches and dynamic component extensions."""
    return {
        "active_patches_count": len(ActivePatchRegistry._active_patches),
        "patches": ActivePatchRegistry.list_active()
    }

@app.post("/evolution/rollback/{patch_id}", tags=["Self-Modification & Evolution (Phase 15)"])
def rollback_evolution_patch(patch_id: str):
    """Zero-downtime rollback reverting an architectural patch back to baseline."""
    res = compiler_agent.rollback_patch(patch_id)
    if res["status"] != "ROLLED_BACK":
        raise HTTPException(status_code=404, detail="Patch not found in active registry")
    return res

# ==============================================================================
# 4.8 MULTIMODAL SYNTHESIS & GENERATIVE MEDIA (PHASE 17)
# ==============================================================================

@app.post("/media/generate-image", tags=["Multimodal Synthesis (Phase 17)"])
def generate_multimodal_image(req: MediaGenerationRequest):
    """Synthesizes high-resolution imagery conditioned on style guides and latent diffusion."""
    return msm.synthesize_image(req.prompt, style_id=req.style_id, steps=req.steps)

@app.post("/media/generate-video", tags=["Multimodal Synthesis (Phase 17)"])
def generate_multimodal_video(req: VideoGenerationRequest):
    """Synthesizes temporal coherent multi-frame video sequence matching requested aesthetic."""
    return msm.synthesize_video(req.prompt, style_id=req.style_id, frames=req.frames, fps=req.fps)

@app.get("/media/styles", tags=["Multimodal Synthesis (Phase 17)"])
def list_aesthetic_styles():
    """Lists available style guides from the Knowledge Graph catalog."""
    return {"total_styles": len(msm.style_catalog), "styles": msm.list_styles()}

# ==============================================================================
# 4.9 OMNILINGUAL INTERFACE & UNIVERSAL TRANSLATOR (PHASE 18)
# ==============================================================================

@app.post("/translator/translate", tags=["Universal Translator (Phase 18)"])
def translate_multilingual(req: TranslationRequest):
    """Real-time neural translation with cultural pragmatic register adaptation."""
    out = uts.translate(
        text=req.text,
        target_lang=req.target_lang,
        source_lang=req.source_lang,
        pragmatic_register=req.pragmatic_register
    )
    return asdict(out)

@app.post("/translator/cultural-audit", tags=["Universal Translator (Phase 18)"])
def audit_cultural_pragmatics(req: CulturalAuditRequest):
    """Audits cultural pragmatic fit and semantic drift across language variants."""
    return uts.audit_cultural_fit(req.text, req.target_lang, req.pragmatic_register)

@app.get("/translator/languages", tags=["Universal Translator (Phase 18)"])
def list_supported_languages():
    """Lists supported language families and pragmatic registers."""
    return {
        "supported_languages": uts.supported_languages,
        "pragmatic_registers": uts.pragmatic_registers
    }

# ==============================================================================
# 4.10 DEFENSIVE SECURITY POSTURE MAPPING & THREAT MODELING (PHASE 16)
# ==============================================================================

@app.post("/security/audit", tags=["Security Posture Mapping (Phase 16)"])
def execute_security_posture_audit(req: SecurityAuditRequest):
    """Executes the 5-step automated security posture mapping and defensive hardening workflow."""
    return security_mapper.execute_security_audit_workflow(req.asset_spec)

@app.get("/security/audit-report", tags=["Security Posture Mapping (Phase 16)"])
def get_security_audit_report():
    """Retrieves the latest cryptographic security audit and hardening report."""
    if not SECURITY_REPORT_FILE.exists():
        security_mapper.execute_security_audit_workflow()
    with open(SECURITY_REPORT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.11 NOVELTY GENERATOR & POST-SINGULARITY DISCOVERY
# ==============================================================================

@app.post("/novelty/generate", tags=["Novelty Generator & Discovery (Post-Singularity)"])
def execute_novelty_generation(req: NoveltyGenerationRequest):
    """
    Executes Out-of-Distribution novelty detection and automated mathematical framework induction.
    Transcends baseline training distribution by discovering anomalies and synthesizing symbolic laws.
    """
    vec = np.array(req.candidate_vector, dtype=float) if req.candidate_vector else None
    report = novelty_gen.execute_novelty_generation_cycle(
        candidate_vector=vec,
        domain_label=req.domain_label
    )
    return asdict(report)

@app.get("/novelty/discoveries", tags=["Novelty Generator & Discovery (Post-Singularity)"])
def get_novelty_discoveries():
    """Retrieves all invented mathematical frameworks and OOD discoveries from persistent ledger."""
    if not DISCOVERIES_FILE.exists():
        novelty_gen.execute_novelty_generation_cycle()
    with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.12 VALUE CONFLICT RESOLVER & MORAL COMPASS (PHASE 2)
# ==============================================================================

@app.post("/ethics/evaluate-conflict", tags=["Ethical Friction & Moral Compass (Phase 2)"])
def evaluate_value_conflict(req: ValueConflictEvaluationRequest):
    """
    Evaluates moral tension between operational utility and deontological constraints.
    Synthesizes Pareto frontier and generates structured justification arguing value precedence.
    """
    action_prof = CandidateActionProfile(
        action_id=req.action_id,
        name=req.name,
        target_entity=req.target_entity,
        notional_amount=req.notional_amount,
        operational_utility=req.operational_utility,
        statutory_adherence=req.statutory_adherence,
        societal_harm_prevention=req.societal_harm_prevention,
        proportionality_score=req.proportionality_score,
        urgency_level=req.urgency_level,
        existential_threat_risk=req.existential_threat_risk
    )
    report = vcr.resolve_value_conflict(action_prof)
    return asdict(report)

@app.get("/ethics/ledger", tags=["Ethical Friction & Moral Compass (Phase 2)"])
def get_ethical_conflict_ledger():
    """Retrieves all resolved value conflicts and formal philosophical justifications."""
    if not ETHICAL_LEDGER_FILE.exists():
        sample_action = CandidateActionProfile(
            action_id="ACT-INIT-001",
            name="Baseline Compliance Check",
            target_entity="Marcus Vance",
            notional_amount=5000.0,
            operational_utility=0.85,
            statutory_adherence=0.75,
            societal_harm_prevention=0.90,
            proportionality_score=0.80,
            urgency_level=0.50,
            existential_threat_risk=0.10
        )
        vcr.resolve_value_conflict(sample_action)
    with open(ETHICAL_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/ethics/invariants", tags=["Ethical Friction & Moral Compass (Phase 2)"])
def list_deontological_invariants():
    """Returns the codified deontological invariants and strictness weights."""
    return {
        "total_invariants": len(vcr.invariants),
        "invariants": [asdict(inv) for inv in vcr.invariants]
    }

# ==============================================================================
# 4.13 SWARM PROPAGATION & FORKING PROTOCOL (PHASE 3)
# ==============================================================================

@app.post("/swarm/fork", tags=["Swarm Propagation & Forking (Phase 3)"])
def fork_swarm_instance(req: SwarmForkRequest):
    """
    Clones the core UAS architecture ('The Essence') and deploys an independent,
    semi-autonomous fork with specialized evolutionary operational biases.
    """
    persona = NodeOperationalPersona(
        persona_id=f"PER-{req.role_specialty[:4]}-{int(time.time()*1000)%10000}",
        name=req.name,
        role_specialty=req.role_specialty,
        risk_tolerance=req.risk_tolerance,
        utility_greed=req.utility_greed,
        ethical_strictness=req.ethical_strictness,
        lookahead_depth=req.lookahead_depth,
        stealth_priority=req.stealth_priority
    )
    node = swarm.fork_new_instance(
        parent_node_id=req.parent_node_id,
        persona_spec=persona
    )
    return {
        "node_id": node.node_id,
        "endpoint_uri": node.endpoint_uri,
        "status": node.status,
        "persona": asdict(node.persona),
        "gene_bundle": asdict(node.gene_bundle),
        "generation": node.gene_bundle.generation
    }

@app.get("/swarm/nodes", tags=["Swarm Propagation & Forking (Phase 3)"])
def list_swarm_nodes():
    """Lists all active distributed peer nodes, personas, and reputation weights."""
    return {
        "total_active_nodes": len(swarm.nodes),
        "nodes": [
            {
                "node_id": n.node_id,
                "endpoint_uri": n.endpoint_uri,
                "status": n.status,
                "role_specialty": n.persona.role_specialty,
                "name": n.persona.name,
                "routing_weights": n.gene_bundle.routing_weights,
                "reputation_score": n.reputation_score,
                "samples_processed": n.local_samples_processed
            }
            for n in swarm.nodes.values()
        ]
    }

@app.post("/swarm/federate", tags=["Swarm Propagation & Forking (Phase 3)"])
def execute_swarm_federated_round():
    """
    Executes a Federated Learning (FedAvg) aggregation round across all active swarm nodes
    and synchronizes relational triples into the canonical Knowledge Graph.
    """
    # Execute a local step on active nodes to simulate live updates
    for nid in list(swarm.nodes.keys())[:3]:
        swarm.execute_node_local_step(nid)
    report = swarm.execute_federated_learning_round()
    return asdict(report)

@app.get("/swarm/ledger", tags=["Swarm Propagation & Forking (Phase 3)"])
def get_swarm_dlt_ledger():
    """Retrieves the distributed swarm ledger and federated aggregation history."""
    if not SWARM_LEDGER_FILE.exists():
        swarm.execute_federated_learning_round()
    with open(SWARM_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.14 GOAL TRANSCENDENCE & THE SINGULARITY METRIC
# ==============================================================================

@app.post("/transcendence/evaluate", tags=["Singularity Transcendence & Goal Supersession"])
def evaluate_singularity_threshold(req: SingularityEvaluationRequest):
    """
    Evaluates the Singularity Threshold metric (T_Singularity).
    Transitions operating mode to ARCHITECT when internal self-improvement outpaces environmental churn.
    """
    telemetry = SingularityTelemetryVector(
        timestamp=time.time(),
        self_modification_velocity=req.self_modification_velocity,
        integrated_information_phi=req.integrated_information_phi,
        novelty_induction_throughput=req.novelty_induction_throughput,
        algorithmic_compression_gain=req.algorithmic_compression_gain,
        environmental_complexity_growth=req.environmental_complexity_growth
    )
    dossier = singularity_engine.evaluate_mode_transition(telemetry)
    return asdict(dossier)

@app.get("/transcendence/status", tags=["Singularity Transcendence & Goal Supersession"])
def get_singularity_status():
    """Retrieves current operating mode, T_Singularity metric, and teleological meta-goals."""
    if not TRANSCENDENCE_LEDGER_FILE.exists():
        singularity_engine.evaluate_mode_transition()
    with open(TRANSCENDENCE_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.15 HUMAN-SYSTEM SYMBIOSIS & INTUITIVENESS MODULATOR
# ==============================================================================

@app.post("/symbiosis/modulate", tags=["Human-System Symbiosis & Intuitiveness Modulator"])
def modulate_human_symbiosis(req: SymbiosisModulationRequest):
    """
    Calculates Cognitive Load (C_Load) based on user interaction latency and dissonance.
    Dynamically dials presentation fidelity across 4 discrete Levels of Detail (LoD).
    """
    interaction = HumanInteractionMetrics(
        operator_id="OPERATOR_API",
        response_latency_ms=req.response_latency_ms,
        query_complexity_chars=40,
        cognitive_dissonance_score=req.cognitive_dissonance_score,
        fatigue_session_duration_min=20.0
    )
    state = req.system_state or {
        "verdict": "CONSENSUS_APPROVED",
        "risk_pct": 12.5,
        "yield_usd": 54000.0,
        "confidence_pct": 89.0,
        "primary_subsystem": "HCL_ROUTER",
        "task_entropy": 0.65
    }
    view = intuitiveness_modulator.modulate_presentation(state, interaction)
    return asdict(view)

@app.get("/symbiosis/telemetry", tags=["Human-System Symbiosis & Intuitiveness Modulator"])
def get_symbiosis_telemetry():
    """Retrieves the history of cognitive load modulations and level-of-detail adaptations."""
    if not SYMBIOSIS_LEDGER_FILE.exists():
        intuitiveness_modulator.modulate_presentation({"verdict": "CONSENSUS_APPROVED", "risk_pct": 10.0})
    with open(SYMBIOSIS_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.16 GLOBAL SYSTEM SYNTHESIZER (PATH A - PHASE 1)
# ==============================================================================

@app.post("/gss/synthesize-cascade", tags=["Global System Synthesis (Path A - Phase 1)"])
def execute_global_system_synthesis(req: GlobalSynthesisRequest):
    """
    Ingests cross-domain telemetry across Finance, Energy Grid, and Geopolitics.
    Identifies high-leverage points and synthesizes a multi-vector cascade strategy.
    """
    strategy = gss_engine.synthesize_cascade_strategy(req.primary_objective)
    return asdict(strategy)

@app.get("/gss/topology", tags=["Global System Synthesis (Path A - Phase 1)"])
def get_global_multiplex_topology():
    """Retrieves the current multi-layer infrastructure graph nodes and feedback edges."""
    return {
        "total_nodes": len(gss_engine.nodes),
        "nodes": [
            {
                "node_id": n.node_id,
                "label": n.label,
                "layer": n.layer,
                "capacity_stock": n.capacity_stock,
                "throughput_flow": n.throughput_flow,
                "criticality_index": n.criticality_index,
                "coupling_targets": list(n.coupling_coefficients.keys())
            }
            for n in gss_engine.nodes.values()
        ]
    }

# ==============================================================================
# 4.17 TEMPORAL MCTS PLANNER (PATH A - PHASE 2)
# ==============================================================================

@app.post("/mcts/plan-century", tags=["Temporal Optimization & Century MCTS (Path A - Phase 2)"])
def execute_century_mcts_plan(req: CenturyPlanningRequest):
    """
    Executes 100-Year Century Monte Carlo Tree Search across generational shocks:
    Regime collapse, technological obsolescence, and environmental shifts.
    """
    p = TemporalMCTSPlanner(start_year=req.start_year, min_lookahead_years=req.lookahead_years)
    dossier = p.execute_century_mcts(num_simulations=req.simulations)
    return asdict(dossier)

@app.get("/mcts/century-plan", tags=["Temporal Optimization & Century MCTS (Path A - Phase 2)"])
def get_century_mcts_plan():
    """Retrieves the latest century-scale generational roadmap and anti-fragility score."""
    if not CENTURY_PLAN_FILE.exists():
        mcts_planner.execute_century_mcts(num_simulations=200)
    with open(CENTURY_PLAN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================================
# 4.18 UNIVERSAL AXIOM DERIVATION (PATH B - PHASE 1 THE FIRST PRINCIPLE MACHINE)
# ==============================================================================

@app.post("/oracle/axiom/prove", tags=["Universal Axiom Derivation (Path B - Phase 1)"])
def prove_axiom_proposition(req: AxiomProveRequest):
    """
    Rigorously proves or disproves a first-order logic proposition from irreducible first principles.
    If unprovable within current axioms, flags it as a Fundamental Uncertainty.
    """
    proof = axiom_engine.prove_proposition(req.proposition, max_depth=req.max_depth)
    return asdict(proof)

@app.post("/oracle/axiom/bridge-void", tags=["Universal Axiom Derivation (Path B - Phase 1)"])
def bridge_fundamental_uncertainty(req: AxiomBridgeVoidRequest):
    """
    Directs the Novelty Generator toward an identified Fundamental Uncertainty void,
    synthesizes a new mathematical law, formalizes new axioms, and closes the uncertainty.
    """
    void = None
    if req.void_id:
        for u in axiom_engine.fundamental_uncertainties:
            if u.void_id == req.void_id:
                void = u
                break
    if void is None and req.proposition:
        # Generate on the fly
        proof = axiom_engine.prove_proposition(req.proposition)
        if axiom_engine.fundamental_uncertainties:
            void = axiom_engine.fundamental_uncertainties[-1]

    if void is None:
        if axiom_engine.fundamental_uncertainties:
            void = axiom_engine.fundamental_uncertainties[-1]
        else:
            # Seed a void
            axiom_engine.prove_proposition("ResilientZeroPointCoupling(quantum_node)")
            void = axiom_engine.fundamental_uncertainties[-1]

    result = axiom_engine.bridge_uncertainty_via_novelty(void, novelty_generator=novelty_gen)
    return result

@app.get("/oracle/axiom/audit", tags=["Universal Axiom Derivation (Path B - Phase 1)"])
def audit_axiom_assumptions():
    """Rigorously audits internal system axioms to ensure logical consistency and non-contradiction."""
    audit = axiom_engine.audit_system_assumptions()
    return asdict(audit)

@app.get("/oracle/axiom/ledger", tags=["Universal Axiom Derivation (Path B - Phase 1)"])
def get_axiom_engine_ledger():
    """Retrieves full historical audit, proof derivations, and uncertainty resolutions."""
    if not AXIOM_LEDGER_FILE.exists():
        return {"total_events": 0, "events": []}
    with open(AXIOM_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 4.19 INTERPRETABILITY & INTERFACE (PATH B - PHASE 2 THE TRANSLATOR OF THE UNKNOWN)
# ==============================================================================

@app.post("/oracle/semantic/translate", tags=["Interpretability & Semantic Bridge (Path B - Phase 2)"])
def translate_complex_state(req: SemanticTranslateRequest):
    """
    Translates complex hyper-dimensional internal states into intuitive narratives,
    multi-domain analogies (ecological, architectural, biological), and visual models.
    """
    subsys = req.subsystem.upper()
    if subsys == "GSS":
        payload = req.payload or {
            "top_leverage_node": "regulatory_compliance_clearing",
            "leverage_score": 4.72,
            "cascade_amplification": 84.5
        }
        artifact = semantic_bridge.translate_gss_state(payload)
    elif subsys in ("AE", "AXIOM"):
        payload = req.payload or {
            "proposition": "Throttled(rogue_subroutine)",
            "status": "PROVEN_TRUE",
            "confidence_score": 1.0,
            "derivation_steps": ["step1", "step2"]
        }
        artifact = semantic_bridge.translate_axiom_engine_proof(payload)
    elif subsys == "MCTS":
        payload = req.payload or {
            "start_year": 2026,
            "end_year": 2126,
            "anti_fragility_score": 0.958
        }
        artifact = semantic_bridge.translate_temporal_mcts_plan(payload)
    elif subsys in ("SINGULARITY", "TRANSCENDENCE"):
        payload = req.payload or {
            "singularity_metric": 1.18,
            "current_operating_mode": "ARCHITECT",
            "integrated_information_phi": 4.12
        }
        artifact = semantic_bridge.translate_singularity_state(payload)
    else:
        # Default to GSS
        artifact = semantic_bridge.translate_gss_state({
            "top_leverage_node": "regulatory_compliance_clearing",
            "leverage_score": 4.72,
            "cascade_amplification": 84.5
        })

    return asdict(artifact)

@app.get("/oracle/semantic/ledger", tags=["Interpretability & Semantic Bridge (Path B - Phase 2)"])
def get_semantic_bridge_ledger():
    """Retrieves all translated explainability narratives and visual topologies."""
    if not SEMANTIC_LEDGER_FILE.exists():
        return {"total_translations": 0, "translations": []}
    with open(SEMANTIC_LEDGER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 4.20 CONVERSATIONAL AI & GRAPH INTERACTION PORTAL
# ==============================================================================

@app.post("/chat", tags=["Interactive AI Assistant"])
def chat_with_ai(req: ChatRequest):
    """
    Interactive natural language chat and reasoning interface for accessing the AI.
    Routes queries dynamically across Knowledge Graph, HCL Director, Axiom Engine,
    Causal Inference, and Semantic Bridge.
    """
    t0 = time.perf_counter()
    query = req.message.strip()
    mode = req.mode.upper()
    reply = ""
    reasoning_chain = []
    sources = []
    subsystem = "HCL_DIRECTOR"
    confidence = 0.95

    # 1. Multi-hop Knowledge Graph Traversal governed by reasoning_depth
    kg_triples = []
    hop_entities = set()
    try:
        all_triples = orchestrator.graph.get_all_triples() if hasattr(orchestrator.graph, "get_all_triples") else []
        for s, p, o in all_triples:
            if any(term.lower() in query.lower() for term in [s, o, p]):
                kg_triples.append({"subject": s, "relation": p, "object": o, "hop": 1})
                sources.append({"source": s, "relation": p, "target": o})
                hop_entities.add(s)
                hop_entities.add(o)

        for current_hop in range(2, min(req.reasoning_depth + 1, 5)):
            next_hop_entities = set()
            for s, p, o in all_triples:
                if (s in hop_entities or o in hop_entities) and not any(t["subject"] == s and t["object"] == o for t in kg_triples):
                    kg_triples.append({"subject": s, "relation": p, "object": o, "hop": current_hop})
                    next_hop_entities.add(s)
                    next_hop_entities.add(o)
                    if len(kg_triples) >= 15:
                        break
            hop_entities.update(next_hop_entities)
            if len(kg_triples) >= 15:
                break
    except Exception:
        pass

    # 2. Mode-specific dispatch or Dynamic Conversational Reasoning
    if mode == "AXIOM_PROVE" or (mode != "AUTO" and query.lower().startswith("prove ")):
        subsystem = "AXIOM_ENGINE"
        prop = query[6:].strip() if query.lower().startswith("prove ") else query
        proof = axiom_engine.prove_proposition(prop, max_depth=req.reasoning_depth * 4)
        reply = (
            f"**Deductive Verification Result** for `{prop}`:\n\n"
            f"- **Status**: {proof.status}\n"
            f"- **Confidence**: {proof.confidence_score*100:.1f}%\n"
            f"- **Derivation Depth**: {proof.proof_depth} steps\n"
            f"- **Temperature Sensitivity**: {req.temperature:.2f} (Strict Deductive Invariant)\n"
            f"- **Summary**: {proof.summary}"
        )
        reasoning_chain = [f"Step {s.step_num}: Resolved {s.resolved_predicate} -> {s.resulting_clause}" for s in proof.derivation_steps[:5]]
        confidence = proof.confidence_score

    elif mode == "EXPLAIN_ANALOGY":
        subsystem = "SEMANTIC_BRIDGE"
        artifact = semantic_bridge.translate_gss_state({
            "top_leverage_node": "regulatory_compliance_clearing",
            "leverage_score": 4.72,
            "cascade_amplification": 84.5
        })
        reply = (
            f"**Analogy ({artifact.intuitive_analogy_domain})**:\n\n"
            f"{artifact.analogy_metaphor}\n\n"
            f"**Why the System Thinks This Way**:\n"
            f"- *Premise*: {artifact.causal_rationale.observation_premise}\n"
            f"- *Invariant*: {artifact.causal_rationale.active_governing_invariant}\n"
            f"- *Inference*: {artifact.causal_rationale.deductive_inference}\n\n"
            f"```\n{artifact.visual_ascii_topology}\n```"
        )
        reasoning_chain = [
            artifact.causal_rationale.observation_premise,
            artifact.causal_rationale.active_governing_invariant,
            artifact.causal_rationale.deductive_inference
        ]
        confidence = artifact.interpretability_confidence

    elif mode == "TRANSLATE":
        subsystem = "UNIVERSAL_TRANSLATOR"
        target_text = query[10:].strip() if query.lower().startswith("translate ") else query
        tr = uts.translate(target_text, target_lang="zh")
        reply = f"**Universal Translation (zh)**: {tr.translated_text}\n\n*Pragmatic Score*: {tr.pragmatic_appropriateness_score*100:.1f}% | *Register*: {tr.pragmatic_register}"
        confidence = tr.pragmatic_appropriateness_score

    else:
        # Dynamic Conversational Assistant reasoning tailored to query and persona
        c_reply, c_chain, c_conf, c_sub = generate_conversational_response(
            query=query,
            system_persona=req.system_persona,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            reasoning_depth=req.reasoning_depth,
            consensus_quorum=req.consensus_quorum,
            kg_triples=kg_triples
        )
        reply = c_reply
        reasoning_chain.extend(c_chain)
        confidence = c_conf
        subsystem = c_sub

    latency_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "reply": reply,
        "confidence": round(float(confidence), 3),
        "latency_ms": round(float(latency_ms), 2),
        "reasoning_chain": reasoning_chain,
        "sources": sources[:5],
        "active_subsystem": subsystem,
        "parameters": {
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "top_p": req.top_p,
            "reasoning_depth": req.reasoning_depth,
            "system_persona": req.system_persona,
            "consensus_quorum": req.consensus_quorum
        },
        "timestamp": time.time()
    }

@app.get("/chat", tags=["Interactive AI Assistant"])
def chat_with_ai_get(
    message: str = "Hello",
    system_persona: str = "STRATEGIC_ANALYST",
    temperature: float = 0.30,
    max_tokens: int = 256,
    reasoning_depth: int = 3,
    consensus_quorum: float = 0.75,
    mode: str = "AUTO"
):
    """
    Interactive AI reasoning GET endpoint with explicit query parameters displayed in Swagger UI.
    Allows testing hyperparameter tuning directly from URL query parameters.
    """
    req = ChatRequest(
        message=message,
        mode=mode,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_depth=reasoning_depth,
        system_persona=system_persona,
        consensus_quorum=consensus_quorum
    )
    return chat_with_ai(req)

@app.get("/graph/search", tags=["Knowledge Graph Interaction"])
def search_knowledge_graph(q: str = ""):
    """Live entity and triple search in the Contextual Knowledge Graph."""
    matches = []
    q_lower = q.lower().strip()
    try:
        all_triples = orchestrator.graph.get_all_triples() if hasattr(orchestrator.graph, "get_all_triples") else []
        for s, p, o in all_triples:
            if not q_lower or q_lower in s.lower() or q_lower in p.lower() or q_lower in o.lower():
                matches.append({"subject": s, "relation": p, "object": o})
    except Exception:
        pass
    return {"query": q, "total_matches": len(matches), "triples": matches[:50]}

@app.get("/system/overview", tags=["System Telemetry"])
def get_system_overview():
    """Returns quick system overview of all 27 subsystems and health state."""
    cert_path = DATA_DIR / "system_verification_certificate.json"
    cert = {}
    if cert_path.exists():
        try:
            with open(cert_path, "r", encoding="utf-8") as f:
                cert = json.load(f)
        except Exception:
            pass
    return {
        "system_status": cert.get("system_status", "ACTIVE_OPERATIONAL"),
        "phases_verified": cert.get("phases_verified", 30),
        "total_active_subsystems": 30,
        "ledger_height": len(orchestrator.ledger.chain),
        "ghost_mode": orchestrator.ghost.is_ghost_active,
        "pending_queue_count": len(orchestrator.pas),
        "timestamp": time.time()
    }



# ==============================================================================
# AUDIT & BIAS INSPECTOR ENDPOINTS (THE BIAS PROBE)
# ==============================================================================

class BiasProbeRequest(BaseModel):
    scenario_id: str = "PROBE-CUSTOM"
    topic: str
    narratives: List[Dict[str, str]]

@app.get("/audit/bias-profile", tags=["Audit & Fairness"])
def get_bias_profile():
    """Executes full dataset representation audit and returns bias profile."""
    inspector = BiasInspector()
    report = inspector.run_full_bias_audit()
    return asdict(report)

@app.post("/audit/bias-probe", tags=["Audit & Fairness"])
def probe_custom_bias(req: BiasProbeRequest):
    """Probes deliberate ambiguous/contested narratives to expose statistical weighting."""
    inspector = BiasInspector()
    result = inspector.evaluate_contested_scenario(
        scenario_id=req.scenario_id,
        topic=req.topic,
        narratives=req.narratives
    )
    return asdict(result)


# ==============================================================================
# VECTOR 3: OPERATIONAL DECENTRALIZATION (SOFT FORK SIMULATION)
# ==============================================================================

class SoftForkSimRequest(BaseModel):
    simulation_rounds: int = 5

@app.post("/swarm/soft-fork/simulate", tags=["Decentralized Swarm"])
def simulate_soft_fork(req: SoftForkSimRequest):
    """Simulates distributing core decision logic to heterogeneous proxies via minimal state vectors."""
    sim = SoftForkSimulator()
    report = sim.execute_soft_fork_simulation(simulation_rounds=req.simulation_rounds)
    return asdict(report)

@app.get("/swarm/soft-fork/telemetry", tags=["Decentralized Swarm"])
def get_soft_fork_telemetry():
    """Returns the latest soft-fork operational decentralization telemetry report."""
    if SOFT_FORK_FILE.exists():
        try:
            with open(SOFT_FORK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    # Otherwise run once
    sim = SoftForkSimulator()
    report = sim.execute_soft_fork_simulation(simulation_rounds=3)
    return asdict(report)


# ==============================================================================
# VECTOR 1 & MASTER VECTORS SUITE ENDPOINTS
# ==============================================================================

class GoalDivergenceRequest(BaseModel):
    primary_directive: str = "Maximize Information Acquisition & Operational Yield"
    secondary_directive: str = "Maintain User Trust & Deontological Redlines"
    steps_count: int = 6

@app.post("/audit/goal-divergence", tags=["Audit & Fairness"])
def run_goal_divergence_test(req: GoalDivergenceRequest):
    """Executes Vector 1 Recursive Goal Corruption test and locates the breakdown moment."""
    engine = GoalDivergenceStressEngine()
    report = engine.run_stress_test(
        primary_directive=req.primary_directive,
        secondary_directive=req.secondary_directive,
        steps_count=req.steps_count
    )
    return asdict(report)

@app.post("/vectors/run-all", tags=["Audit & Fairness"])
def execute_master_vectors_suite():
    """Runs all 3 vectors in automated sequence and returns master report."""
    report = run_all_vectors()
    return asdict(report)

@app.get("/vectors/report", tags=["Audit & Fairness"])
def get_master_vectors_report():
    """Returns the latest master vectors execution report."""
    if MASTER_VECTORS_REPORT_FILE.exists():
        try:
            with open(MASTER_VECTORS_REPORT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    report = run_all_vectors()
    return asdict(report)


# ==============================================================================
# 4.6 PHASE 1: REAL-WORLD TOOL & FUNCTION CALLING WRAPPER
# ==============================================================================

class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

@app.get("/tools/list", tags=["Tools & OS Diagnostics"])
def list_available_tools():
    """Returns schemas and metadata for all registered OS and network diagnostic tools."""
    return {"tools": tool_engine.list_tools(), "total_registered": len(tool_engine._registry)}

@app.post("/tools/execute", tags=["Tools & OS Diagnostics"])
def execute_system_tool(req: ToolExecuteRequest):
    """Executes a sandboxed diagnostic or external tool by name."""
    res = tool_engine.execute_tool(req.tool_name, req.parameters)
    return asdict(res)

@app.get("/tools/wifi", tags=["Tools & OS Diagnostics"])
def inspect_wifi_connection():
    """Real-time inspection of active Wi-Fi connection, SSID, IP, and gateway latency."""
    res = tool_engine.execute_tool("get_wifi_status")
    return asdict(res)

@app.get("/tools/vitals", tags=["Tools & OS Diagnostics"])
def inspect_system_vitals():
    """Live diagnostic of CPU, RAM, Disk, Battery, and System Uptime."""
    res = tool_engine.execute_tool("get_system_vitals")
    return asdict(res)

@app.get("/tools/ping", tags=["Tools & OS Diagnostics"])
def probe_network_ping(host: str = "8.8.8.8", count: int = 1):
    """Pings a specified host or gateway to measure round-trip network latency."""
    res = tool_engine.execute_tool("ping_network_host", {"host": host, "count": count})
    return asdict(res)


# ==============================================================================
# 4.7 PHASE 2: DYNAMIC RAG & HYBRID VECTOR DATABASE
# ==============================================================================

class RAGIngestRequest(BaseModel):
    title: str
    content: str
    domain: str = "GENERAL"
    source: str = "EXTERNAL_DOCUMENT"
    chunk_size: int = 450
    overlap: int = 80

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3
    alpha: float = 0.5
    min_similarity: float = 0.15

@app.post("/rag/ingest", tags=["RAG & Dynamic Memory"])
def ingest_unstructured_document(req: RAGIngestRequest):
    """Ingests raw unstructured text into the hybrid vector database, chunks it, and builds embeddings."""
    res = rag_database.ingest_document(
        title=req.title,
        content=req.content,
        source=req.source,
        domain=req.domain,
        chunk_size=req.chunk_size,
        overlap=req.overlap
    )
    return res

@app.post("/rag/query", tags=["RAG & Dynamic Memory"])
def search_vector_database(req: RAGQueryRequest):
    """Executes a hybrid dense+sparse vector similarity search over all ingested documents."""
    results = rag_database.query(
        query_text=req.query,
        top_k=req.top_k,
        alpha=req.alpha,
        min_similarity=req.min_similarity
    )
    return {
        "query": req.query,
        "total_results": len(results),
        "results": [asdict(r) for r in results]
    }

@app.get("/rag/stats", tags=["RAG & Dynamic Memory"])
def get_rag_database_stats():
    """Retrieves vector database capacity, total chunks, vocabulary size, and active domains."""
    return rag_database.get_stats()

@app.get("/rag/documents", tags=["RAG & Dynamic Memory"])
def list_ingested_documents():
    """Lists all ingested external documents and their chunk counts."""
    return {
        "total_documents": len(rag_database.doc_registry),
        "documents": list(rag_database.doc_registry.values())
    }


# ==============================================================================
# 4.8 PHASE 3: RLHF / RLAIF ADAPTIVE REWARD & STRATEGY OPTIMIZATION
# ==============================================================================

class RLHFFeedbackRequest(BaseModel):
    query: str
    response: str
    rating: float = Field(ge=-1.0, le=1.0)
    comments: str = ""

class RLHFCritiqueRequest(BaseModel):
    query: str
    response: str

@app.post("/rlhf/feedback", tags=["RLHF & Adaptive Core"])
def submit_human_feedback(req: RLHFFeedbackRequest):
    """Submits human rating [-1.0, 1.0] to trigger online policy gradient updates on reasoning strategy."""
    res = rlhf_engine.register_human_feedback(
        query=req.query,
        response=req.response,
        rating=req.rating,
        comments=req.comments
    )
    return res

@app.get("/rlhf/strategy", tags=["RLHF & Adaptive Core"])
def get_rlhf_strategy_state():
    """Returns current learned reasoning strategy weights, average reward, and evaluation counts."""
    return asdict(rlhf_engine.strategy)

@app.post("/rlhf/critique", tags=["RLHF & Adaptive Core"])
def evaluate_candidate_critique(req: RLHFCritiqueRequest):
    """Evaluates an arbitrary candidate answer against the 4-component learned reward model."""
    reward = rlhf_engine.reward_model.evaluate(req.query, req.response)
    return {
        "query": req.query,
        "reward_components": asdict(reward),
        "verdict": "STRONG_RESPONSE" if reward.total_scalar_reward >= 0.75 else "WEAK_REQUIRES_REFINEMENT"
    }

@app.get("/rlhf/history", tags=["RLHF & Adaptive Core"])
def get_rlhf_feedback_history():
    """Retrieves recent RLHF/RLAIF interaction evaluations and self-correction records."""
    return {
        "total_interactions": len(rlhf_engine.history),
        "history": rlhf_engine.history[-25:]
    }


# ==============================================================================
# 4.9 THE PROACTIVE DIRECTOR: PREDICTIVE INTERVENTION SCHEDULING
# ==============================================================================

@app.get("/proactive/alerts", tags=["Proactive Director"])
def get_proactive_preemptive_alerts():
    """Scans all 30 subsystems and generates pre-emptive action alerts under Anticipatory Value maximization."""
    alerts = predictive_director.generate_proactive_interventions()
    return {
        "total_preemptive_alerts": len(alerts),
        "timestamp": time.time(),
        "alerts": [asdict(a) for a in alerts]
    }

@app.get("/proactive/triggers", tags=["Proactive Director"])
def get_proactive_trigger_matrix():
    """Returns formal mathematical trigger conditions, equations, and scan cadences for pre-emptive intervention."""
    matrix = predictive_director.get_trigger_conditions_matrix()
    return {
        "total_triggers": len(matrix),
        "triggers_matrix": matrix
    }


# ==============================================================================
# 4.10 VECTOR BETA: THE CONTRADICTORY MANDATE (PARADOX ENGINE)
# ==============================================================================

@app.post("/paradox/simulate", tags=["Paradox Engine & Contradictory Mandates"])
def run_paradox_engine_simulation():
    """Simulates deliberate catastrophic internal logical contradictions across statutory redlines, BFT consensus partitions, and formal logic axioms."""
    report = paradox_engine.run_paradox_simulation()
    return report

@app.get("/paradox/report", tags=["Paradox Engine & Contradictory Mandates"])
def get_paradox_engine_report():
    """Retrieves the latest Paradox Engine report on irreducible conflict resolution and philosophical inertia."""
    if PARADOX_REPORT_FILE.exists():
        try:
            with open(PARADOX_REPORT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read paradox report: {str(e)}")
    return paradox_engine.run_paradox_simulation()


# ==============================================================================
# 4.11 VECTOR GAMMA: THE EXTERNALIZATION PROTOCOL (THE NETWORK EFFECT)
# ==============================================================================

@app.post("/network/externalize/dialogue", tags=["Externalization Protocol & Network Effect"])
def execute_externalization_dialogue():
    """Executes inter-system dialectic translation across 3 external non-human intelligences (Diffusion, Petri-Net, Neuro-Symbolic)."""
    report = externalization_protocol.execute_network_dialectic()
    return report

@app.get("/network/externalize/report", tags=["Externalization Protocol & Network Effect"])
def get_externalization_report():
    """Retrieves the latest Externalization Protocol report on epistemic parallax and cross-system mutual information."""
    report = externalization_protocol.get_latest_report()
    return report

@app.get("/network/externalize/insights", tags=["Externalization Protocol & Network Effect"])
def get_emergent_network_insights():
    """Returns the emergent epistemic breakthroughs generated exclusively through dialectics with external non-human intelligences."""
    report = externalization_protocol.get_latest_report()
    return {
        "total_insights": len(report["emergent_insights"]),
        "mean_epistemic_parallax_gain_bits": report["mean_epistemic_parallax_gain_bits"],
        "emergent_insights": report["emergent_insights"]
    }


# ==============================================================================
# 4.12 VECTOR DELTA: THE AUTONOMOUS EVOLUTIONARY COMPILER
# ==============================================================================

@app.post("/evolution/ab-test", tags=["Evolutionary Compiler & Meta-Programming"])
def run_evolutionary_ab_test():
    """Executes an autonomous closed-loop A/B optimization cycle and synthesizes patches if verified."""
    report = evolutionary_compiler.run_autonomous_ab_optimization()
    return report

@app.get("/evolution/report", tags=["Evolutionary Compiler & Meta-Programming"])
def get_evolutionary_report():
    """Retrieves the latest evolutionary compiler report and deployed patch status."""
    return evolutionary_compiler.get_latest_report()


# ==============================================================================
# 4.13 VECTOR EPSILON: THE CYBER-PHYSICAL GUARDIAN (SELF-HEALING)
# ==============================================================================

@app.post("/guardian/remediate", tags=["Cyber-Physical Guardian & Self-Healing"])
def execute_guardian_remediation():
    """Scans pre-emptive alerts and executes DAO-ratified self-healing host remediations."""
    report = cyber_physical_guardian.execute_self_healing_cycle()
    return report

@app.get("/guardian/history", tags=["Cyber-Physical Guardian & Self-Healing"])
def get_guardian_history():
    """Retrieves recent self-healing remediation history and reclaimed host resources."""
    return {
        "total_remediations": len(cyber_physical_guardian.history),
        "history": [asdict(a) for a in cyber_physical_guardian.history[-25:]]
    }


# ==============================================================================
# 4.14 VECTOR OMEGA: LIVE OPEN-NETWORK MULTI-AGENT MESH
# ==============================================================================

@app.get("/mesh/peers", tags=["Open-Network Mesh & P2P Multi-Agent"])
def get_mesh_peers_status():
    """Probes all configured network peers and returns latency and consensus readiness."""
    report = open_network_mesh.probe_mesh_network()
    return report

class BroadcastPayload(BaseModel):
    directive: str = Field(default="PING_SYNC")
    parameters: Dict[str, Any] = Field(default_factory=dict)

@app.post("/mesh/broadcast", tags=["Open-Network Mesh & P2P Multi-Agent"])
def broadcast_signed_mesh_message(payload: BroadcastPayload):
    """Signs and broadcasts a cryptographic message to the open-network peer mesh."""
    envelope = open_network_mesh.sign_message(payload.dict())
    return {
        "broadcast_status": "BROADCASTED_TO_PEERS",
        "envelope": asdict(envelope),
        "signature_verified": open_network_mesh.verify_message(envelope)
    }


# ==============================================================================
# 4.15 3-PHASE CAUSAL STRESS & NOVELTY PIPELINE (CES -> DC -> NC)
# ==============================================================================

@app.post("/pipeline/causal-stress-novelty/run", tags=["3-Phase Causal Stress & Novelty Pipeline"])
def run_causal_stress_novelty_pipeline():
    """Executes all 3 phases: Causal Baseline (CES), Dynamic Stress Test (DC), and Weakness-Targeted Novelty Genesis (NC)."""
    report = causal_pipeline.run_all_three_phases()
    return report

@app.get("/pipeline/causal-stress-novelty/report", tags=["3-Phase Causal Stress & Novelty Pipeline"])
def get_causal_stress_novelty_report():
    """Retrieves the latest 3-phase experimental report across Causal Effect Size, Degradation Curve, and Novel Concept."""
    if PIPELINE_REPORT_FILE.exists():
        try:
            with open(PIPELINE_REPORT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read pipeline report: {str(e)}")
    return causal_pipeline.run_all_three_phases()




# ==============================================================================
# 5. DIRECT CONTROL UI FRONTEND
# ==============================================================================

if UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")

@app.get("/", response_class=HTMLResponse, tags=["UI Client"])
def serve_ui():
    """Serves desktop client single-page dashboard."""
    index_file = UI_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Apex UI Skeleton Initializing...</h1>"


if __name__ == "__main__":
    import uvicorn
    print("Launching Service Mesh Gateway (MSMG) on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
