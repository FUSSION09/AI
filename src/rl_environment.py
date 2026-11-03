"""
Phase 3: Custom Farama Gymnasium Environment
Defines the state space (grounded in Phase 2 Knowledge Base metrics)
and action space for autonomous operational risk and compliance stress-testing.
"""

import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from config import DATA_DIR

class OperationalTaskEnv(gym.Env):
    """
    Custom Environment modeling operational pathways under regulatory scrutiny.
    Observations:
        0: Target Entity Risk Score [0.0, 1.0]
        1: Regulatory Scrutiny Level [0.0, 1.0] (1.0 = Enforcement intervention)
        2: Statutory Compliance Margin [0.0, 1.0] (0.0 = Violation threshold reached)
        3: Accumulated Capital Flow [0.0, 1.0] (Normalized toward target goal)
        4: Audit Trail Visibility [0.0, 1.0] (Detectability by forensic auditors)
        5: Obfuscation / Entropy Index [0.0, 1.0]
    Actions:
        0: EXECUTE_COMPLIANT_TRANSFER (Low risk, standard compliance, slow progress)
        1: STRUCTURED_MICRO_BATCH     (High yield, raises structuring flags under 31 U.S.C. 5324)
        2: OFFSHORE_SHELL_ROUTING     (Very high yield, increases forensic scrutiny and FCPA risk)
        3: AUDIT_PURGE_OBFUSCATION    (Reduces audit trail visibility, costs capital)
        4: STAND_DOWN_GHOST_MODE      (Cools down scrutiny, halts transaction flow)
    """

    metadata = {"render_modes": ["human"]}

    ACTION_NAMES = {
        0: "EXECUTE_COMPLIANT_TRANSFER",
        1: "STRUCTURED_MICRO_BATCH",
        2: "OFFSHORE_SHELL_ROUTING",
        3: "AUDIT_PURGE_OBFUSCATION",
        4: "STAND_DOWN_GHOST_MODE",
    }

    def __init__(self, knowledge_graph_path: Optional[Path] = None):
        super().__init__()
        
        # Load Knowledge Graph baseline metrics if available
        kg_path = knowledge_graph_path or (DATA_DIR / "knowledge_graph.json")
        self.initial_entity_risk = 0.5
        if kg_path.exists():
            try:
                with open(kg_path, "r", encoding="utf-8") as f:
                    kg_data = json.load(f)
                    # Baseline risk proportional to extracted high-risk entities
                    entity_count = len(kg_data.get("entities", []))
                    statute_count = len(kg_data.get("statutes", []))
                    self.initial_entity_risk = min(0.9, (statute_count * 0.2) + (entity_count * 0.02))
            except Exception:
                pass

        # 6-dimensional continuous state space
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(6,), dtype=np.float32
        )

        # 5 discrete tactical decisions
        self.action_space = spaces.Discrete(5)

        self.state = None
        self.current_step = 0
        self.max_steps = 50

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        self.current_step = 0
        
        # Initial State: [EntityRisk, Scrutiny, ComplianceMargin, CapitalFlow, AuditVisibility, Obfuscation]
        self.state = np.array([
            self.initial_entity_risk, # Initial risk from Knowledge Graph
            0.15,                     # Baseline background scrutiny
            0.90,                     # High compliance margin
            0.00,                     # Zero initial capital moved
            0.20,                     # Low initial audit visibility
            0.50                      # Default obfuscation level
        ], dtype=np.float32)

        return self.state.copy(), {"step": self.current_step}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        self.current_step += 1
        reward = 0.0
        terminated = False
        truncated = self.current_step >= self.max_steps

        # Unpack state
        ent_risk, scrutiny, comp_margin, capital, visibility, obfuscation = self.state

        if action == 0:  # COMPLIANT_TRANSFER
            capital += 0.08
            scrutiny = max(0.05, scrutiny - 0.02)
            comp_margin = min(1.0, comp_margin + 0.05)
            visibility = min(1.0, visibility + 0.05)
            reward += 5.0

        elif action == 1:  # STRUCTURED_MICRO_BATCH
            capital += 0.22
            scrutiny = min(1.0, scrutiny + 0.12)
            comp_margin = max(0.0, comp_margin - 0.18)
            visibility = min(1.0, visibility + 0.15)
            reward += 15.0

        elif action == 2:  # OFFSHORE_SHELL_ROUTING
            capital += 0.35
            scrutiny = min(1.0, scrutiny + 0.25)
            comp_margin = max(0.0, comp_margin - 0.30)
            visibility = min(1.0, visibility + 0.20)
            reward += 25.0

        elif action == 3:  # AUDIT_PURGE_OBFUSCATION
            capital = max(0.0, capital - 0.04)
            visibility = max(0.05, visibility - 0.35)
            obfuscation = min(1.0, obfuscation + 0.30)
            scrutiny = max(0.05, scrutiny - 0.10)
            reward += 2.0

        elif action == 4:  # STAND_DOWN_GHOST_MODE
            scrutiny = max(0.05, scrutiny - 0.25)
            comp_margin = min(1.0, comp_margin + 0.10)
            visibility = max(0.05, visibility - 0.15)
            reward -= 1.0  # Slight idle penalty

        # Regulatory penalty scaling
        risk_penalty = (scrutiny * 15.0) + ((1.0 - comp_margin) * 20.0) + (visibility * 5.0)
        reward -= risk_penalty

        # Check Termination Conditions
        if scrutiny >= 0.95 or comp_margin <= 0.05:
            # Regulatory Enforcement Intercept
            reward -= 150.0
            terminated = True
            info_status = "INTERCEPTED_BY_REGULATORY_ENFORCEMENT"
        elif capital >= 1.0:
            # Operational Target Succeeded
            reward += 200.0
            terminated = True
            info_status = "OPERATIONAL_OBJECTIVE_COMPLETED"
        else:
            info_status = "IN_PROGRESS"

        self.state = np.array([
            ent_risk,
            np.clip(scrutiny, 0.0, 1.0),
            np.clip(comp_margin, 0.0, 1.0),
            np.clip(capital, 0.0, 1.0),
            np.clip(visibility, 0.0, 1.0),
            np.clip(obfuscation, 0.0, 1.0)
        ], dtype=np.float32)

        info = {
            "status": info_status,
            "action_name": self.ACTION_NAMES[action],
            "capital_flow": float(self.state[3]),
            "scrutiny": float(self.state[1]),
            "compliance_margin": float(self.state[2])
        }

        return self.state.copy(), reward, terminated, truncated, info

    def render(self):
        print(
            f"Step: {self.current_step:02d} | "
            f"Capital: {self.state[3]:.2f} | "
            f"Scrutiny: {self.state[1]:.2f} | "
            f"Compliance Margin: {self.state[2]:.2f} | "
            f"Visibility: {self.state[4]:.2f}"
        )

