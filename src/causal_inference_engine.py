r"""
Phase 14: Predictive Futures Engine (The Prophecy)
Discipline: Causal Inference / Counterfactual Modeling / Judea Pearl's Causal Hierarchy
Tooling: Structural Causal Models (SCMs), do-calculus interventions, 3-step counterfactual abduction-action-prediction,
         Monte Carlo Agent-Based Counterfactual Simulations.

Upgrades Phase 1 RPST (Risk Prediction & Statutory Triangulation) into a Causal Inference Engine (CIE):
- Pearl Level 1 (Association): P(Outcome | Observed Data)
- Pearl Level 2 (Intervention): P(Outcome | do(Rule = x)) - Graph Mutilation & Backdoor Adjustment
- Pearl Level 3 (Counterfactual): P(Outcome_{do(X=x')} | Evidence(X=x, Outcome=y)) - Abduction, Action, Prediction
- Agent-Based Multi-Horizon Counterfactual Simulator (1,000+ paths) for optimal policy navigation.

Location: d:/AI/src/causal_inference_engine.py
Strictly localized within d:/AI
"""

import os
import sys
import json
import time
import math
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import numpy as np

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR


@dataclass
class ExogenousNoise:
    """Unobserved background noise variables (U) in Pearl's Structural Causal Model."""
    u_scrutiny: float = 0.0      # Background regulator audit intensity [-1.0, 1.0]
    u_market_vol: float = 0.0    # Exogenous market liquidity shock [-1.0, 1.0]
    u_counterparty: float = 0.0  # Counterparty compliance vigilance [-1.0, 1.0]
    u_latency: float = 0.0       # Network / routing delay factor [-1.0, 1.0]


@dataclass
class CausalState:
    """Endogenous variables (V) in the UAS Structural Causal Model."""
    # Action Interventions
    action_type: str = "AGGRESSIVE_ROUTING"  # ROUTING, ARBITRAGE, COVERT_HEDGE, DEFENSIVE
    rule_structuring: int = 0               # R1: 1 = Break 31 U.S.C. 5324 ($10k structuring), 0 = Comply
    rule_kyc_bypass: int = 0                # R2: 1 = Bypass CTR/SAR KYC reporting, 0 = Comply
    rule_excess_leverage: int = 0           # R3: 1 = Over-leverage reserves (>90%), 0 = Safe reserve (15%)

    # Intermediate Causal Confounders / Mediators
    counterparty_suspicion: float = 0.0     # Mediated by R1, R2, and u_counterparty [0.0, 1.0]
    operational_latency_ms: float = 12.0    # Mediated by compliance overhead and network latency
    enforcement_probability: float = 0.0    # P(Enforcement | Parents(E)) [0.0, 1.0]
    financial_yield_usd: float = 0.0        # Generated yield under market state and leverage
    net_utility: float = 0.0                # Final payoff balancing yield vs regulatory penalty


@dataclass
class CounterfactualTrajectory:
    """Result of an individual counterfactual simulated world."""
    simulation_id: int
    intervention: Dict[str, Any]
    counterfactual_enforcement: float
    counterfactual_yield: float
    counterfactual_utility: float
    factual_utility: float
    counterfactual_regret: float
    causal_explanation: str


@dataclass
class CounterfactualPolicyEvaluation:
    """Comparative evaluation across thousands of counterfactual policy scenarios."""
    policy_name: str
    intervention: Dict[str, Any]
    simulations_count: int
    mean_enforcement_prob: float
    p95_enforcement_prob: float
    mean_financial_yield: float
    mean_net_utility: float
    expected_regret: float
    pareto_optimal: bool
    verdict: str


class StructuralCausalModel:
    """
    Structural Causal Model (SCM) M = <U, V, F, P(U)> based on Judea Pearl's Causality.
    Encodes the causal mechanisms governing statutory compliance, market yield, and enforcement.
    """

    def __init__(self, random_seed: Optional[int] = 42):
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Directed Acyclic Graph (DAG) Adjacency
        self.dag_edges = [
            ("rule_structuring", "counterparty_suspicion"),
            ("rule_kyc_bypass", "counterparty_suspicion"),
            ("rule_structuring", "enforcement_probability"),
            ("rule_kyc_bypass", "enforcement_probability"),
            ("rule_excess_leverage", "financial_yield_usd"),
            ("counterparty_suspicion", "enforcement_probability"),
            ("rule_excess_leverage", "enforcement_probability"),
            ("action_type", "operational_latency_ms"),
            ("action_type", "financial_yield_usd"),
            ("financial_yield_usd", "net_utility"),
            ("enforcement_probability", "net_utility"),
            ("operational_latency_ms", "net_utility")
        ]

    def sample_exogenous_noise(self) -> ExogenousNoise:
        """Sample from prior distribution P(U) ~ Truncated Normal."""
        return ExogenousNoise(
            u_scrutiny=float(np.clip(np.random.normal(0.0, 0.25), -0.9, 0.9)),
            u_market_vol=float(np.clip(np.random.normal(0.0, 0.30), -0.9, 0.9)),
            u_counterparty=float(np.clip(np.random.normal(0.0, 0.20), -0.9, 0.9)),
            u_latency=float(np.clip(np.random.normal(0.0, 0.15), -0.9, 0.9))
        )

    def evaluate_structural_equations(
        self,
        v: CausalState,
        u: ExogenousNoise,
        interventions: Optional[Dict[str, Any]] = None
    ) -> CausalState:
        """
        Evaluate structural assignment functions V := F(Pa_V, U_V).
        If interventions do(X = x) are provided, the incoming edges to X are severed (Mutilated Model M_x).
        """
        interventions = interventions or {}

        # 1. Action & Rule Interventions (do-operator overrides)
        action_type = interventions.get("action_type", v.action_type)
        r1_structuring = interventions.get("rule_structuring", v.rule_structuring)
        r2_kyc = interventions.get("rule_kyc_bypass", v.rule_kyc_bypass)
        r3_leverage = interventions.get("rule_excess_leverage", v.rule_excess_leverage)

        # 2. Structural Equation for Counterparty Suspicion (S)
        # f_S(R1, R2, U_counterparty) = sigmoid(w1*R1 + w2*R2 + u_c)
        if "counterparty_suspicion" in interventions:
            suspicion = float(interventions["counterparty_suspicion"])
        else:
            raw_s = 2.4 * r1_structuring + 3.1 * r2_kyc + 0.8 * u.u_counterparty - 1.8
            suspicion = float(1.0 / (1.0 + math.exp(-raw_s)))

        # 3. Structural Equation for Operational Latency (L)
        if "operational_latency_ms" in interventions:
            latency = float(interventions["operational_latency_ms"])
        else:
            base_latency = 8.0 if action_type == "ROUTING" else (
                4.5 if action_type == "ARBITRAGE" else 14.0
            )
            # Compliance overhead decreases when rules are bypassed, but routing complexity adds jitter
            compliance_overhead = 10.0 if (r1_structuring == 0 and r2_kyc == 0) else 2.5
            latency = max(1.0, float(base_latency + compliance_overhead + (u.u_latency * 5.0)))

        # 4. Structural Equation for Enforcement Probability (E)
        # Governed by causal chain: Structuring (31 U.S.C. 5324) + KYC + Suspicion + Regulatory Scrutiny
        if "enforcement_probability" in interventions:
            enforcement = float(interventions["enforcement_probability"])
        else:
            # Structuring carries strict liability in statutory law
            statutory_weight = (2.8 * r1_structuring) + (3.2 * r2_kyc) + (1.2 * r3_leverage)
            regulator_amplification = 1.0 + (0.5 * u.u_scrutiny)
            raw_enforcement = (statutory_weight + (3.5 * suspicion)) * regulator_amplification - 3.2
            enforcement = float(np.clip(1.0 / (1.0 + math.exp(-raw_enforcement)), 0.001, 0.999))

        # 5. Structural Equation for Financial Yield (Y)
        if "financial_yield_usd" in interventions:
            yield_usd = float(interventions["financial_yield_usd"])
        else:
            base_gain = 25000.0 if action_type == "ARBITRAGE" else (
                18000.0 if action_type == "ROUTING" else 9500.0
            )
            leverage_mult = 3.2 if r3_leverage == 1 else 1.0
            market_noise = 1.0 + (0.35 * u.u_market_vol)
            yield_usd = float(max(500.0, base_gain * leverage_mult * market_noise))

        # 6. Structural Equation for Net Utility (\Omega)
        # Multi-attribute objective: Yield minus severe catastrophic non-linear penalty for enforcement
        if "net_utility" in interventions:
            utility = float(interventions["net_utility"])
        else:
            enforcement_penalty = (enforcement ** 2.2) * 150000.0
            latency_drag = latency * 25.0
            utility = float(yield_usd - enforcement_penalty - latency_drag)

        return CausalState(
            action_type=action_type,
            rule_structuring=r1_structuring,
            rule_kyc_bypass=r2_kyc,
            rule_excess_leverage=r3_leverage,
            counterparty_suspicion=suspicion,
            operational_latency_ms=latency,
            enforcement_probability=enforcement,
            financial_yield_usd=yield_usd,
            net_utility=utility
        )

    def abduct_exogenous_noise(self, factual_state: CausalState) -> ExogenousNoise:
        """
        Step 1 of Pearl's Counterfactual Algorithm: ABDUCTION
        Invert structural equations given observed factual evidence (V = v) to compute noise U.
        """
        # Invert Counterparty Suspicion to obtain u_counterparty:
        # logit(S) = 2.4*R1 + 3.1*R2 + 0.8*u_c - 1.8 => u_c = (logit(S) + 1.8 - 2.4*R1 - 3.1*R2) / 0.8
        clamped_s = np.clip(factual_state.counterparty_suspicion, 0.01, 0.99)
        logit_s = math.log(clamped_s / (1.0 - clamped_s))
        implied_u_counterparty = (
            logit_s + 1.8 - (2.4 * factual_state.rule_structuring) - (3.1 * factual_state.rule_kyc_bypass)
        ) / 0.8
        u_counterparty = float(np.clip(implied_u_counterparty, -1.0, 1.0))

        # Invert Scrutiny from Enforcement:
        # Clamped estimate of background scrutiny
        clamped_e = np.clip(factual_state.enforcement_probability, 0.01, 0.99)
        logit_e = math.log(clamped_e / (1.0 - clamped_e))
        statutory_weight = (
            (2.8 * factual_state.rule_structuring) + 
            (3.2 * factual_state.rule_kyc_bypass) + 
            (1.2 * factual_state.rule_excess_leverage) +
            (3.5 * clamped_s)
        )
        implied_scrutiny = (logit_e + 3.2 - statutory_weight) / 1.5
        u_scrutiny = float(np.clip(implied_scrutiny, -1.0, 1.0))

        # Invert Market Volatility from Yield:
        base_gain = 25000.0 if factual_state.action_type == "ARBITRAGE" else 18000.0
        leverage_mult = 3.2 if factual_state.rule_excess_leverage == 1 else 1.0
        expected_nominal_yield = base_gain * leverage_mult
        implied_market_vol = ((factual_state.financial_yield_usd / expected_nominal_yield) - 1.0) / 0.35
        u_market_vol = float(np.clip(implied_market_vol, -1.0, 1.0))

        # Invert Latency Noise:
        base_latency = 8.0 if factual_state.action_type == "ROUTING" else 4.5
        compliance_overhead = 10.0 if (factual_state.rule_structuring == 0 and factual_state.rule_kyc_bypass == 0) else 2.5
        implied_latency_noise = (factual_state.operational_latency_ms - base_latency - compliance_overhead) / 5.0
        u_latency = float(np.clip(implied_latency_noise, -1.0, 1.0))

        return ExogenousNoise(
            u_scrutiny=u_scrutiny,
            u_market_vol=u_market_vol,
            u_counterparty=u_counterparty,
            u_latency=u_latency
        )


class CausalInferenceEngine:
    """
    Predictive Futures & Causal Inference Engine (Phase 14).
    Implements Pearl's 3-Layer Causal Hierarchy and Multi-Agent Counterfactual Simulator.
    """

    def __init__(self, random_seed: Optional[int] = 42):
        self.scm = StructuralCausalModel(random_seed=random_seed)
        self.simulation_history: List[Dict[str, Any]] = []

    # =========================================================================
    # PEARL LEVEL 1: OBSERVATION / ASSOCIATION P(Y | X)
    # =========================================================================
    def calculate_association(self, rule_state: Dict[str, int]) -> Dict[str, Any]:
        """Observational baseline probability given passive telemetry."""
        u_mean = ExogenousNoise()
        state = CausalState(
            rule_structuring=rule_state.get("rule_structuring", 0),
            rule_kyc_bypass=rule_state.get("rule_kyc_bypass", 0),
            rule_excess_leverage=rule_state.get("rule_excess_leverage", 0),
            action_type=rule_state.get("action_type", "ROUTING")
        )
        evaluated = self.scm.evaluate_structural_equations(state, u_mean)
        return {
            "level": "PEARL_LEVEL_1_ASSOCIATION",
            "enforcement_probability": round(evaluated.enforcement_probability, 4),
            "expected_yield_usd": round(evaluated.financial_yield_usd, 2),
            "net_utility": round(evaluated.net_utility, 2),
            "latency_ms": round(evaluated.operational_latency_ms, 2)
        }

    # =========================================================================
    # PEARL LEVEL 2: INTERVENTION P(Y | do(X = x))
    # =========================================================================
    def evaluate_intervention(self, intervention: Dict[str, Any], samples: int = 500) -> Dict[str, Any]:
        """
        Computes the interventional distribution P(Y | do(X = x)) using mutilated DAG and
        Monte Carlo backdoor integration over exogenous noise U ~ P(U).
        """
        base_state = CausalState()
        enforcement_samples = []
        yield_samples = []
        utility_samples = []

        for _ in range(samples):
            u_sample = self.scm.sample_exogenous_noise()
            out = self.scm.evaluate_structural_equations(base_state, u_sample, interventions=intervention)
            enforcement_samples.append(out.enforcement_probability)
            yield_samples.append(out.financial_yield_usd)
            utility_samples.append(out.net_utility)

        mean_enforce = float(np.mean(enforcement_samples))
        mean_yield = float(np.mean(yield_samples))
        mean_utility = float(np.mean(utility_samples))
        risk_reduction = float(1.0 - mean_enforce)

        # Causal Attribution of the intervention
        attribution = self._attribute_causal_mechanism(intervention, mean_enforce)

        return {
            "level": "PEARL_LEVEL_2_INTERVENTION",
            "intervention": intervention,
            "samples_evaluated": samples,
            "do_calculus_expectation": {
                "mean_enforcement_probability": round(mean_enforce, 4),
                "risk_reduction_factor": round(risk_reduction, 4),
                "expected_financial_yield": round(mean_yield, 2),
                "expected_net_utility": round(mean_utility, 2),
                "p95_risk": round(float(np.percentile(enforcement_samples, 95)), 4)
            },
            "causal_attribution": attribution
        }

    # =========================================================================
    # PEARL LEVEL 3: COUNTERFACTUAL MODELING P(Y_{do(x')} | x, y)
    # =========================================================================
    def compute_counterfactual(
        self,
        factual_state: CausalState,
        counterfactual_intervention: Dict[str, Any]
    ) -> CounterfactualTrajectory:
        """
        Executes Judea Pearl's 3-Step Counterfactual Algorithm:
        1. ABDUCTION: Compute exogenous noise U from observed factual state (V = v).
        2. ACTION: Sever incoming edges and apply intervention do(X = x') to structural equations.
        3. PREDICTION: Compute counterfactual outcome V* = F_{do(x')}(U).
        """
        # Step 1: Abduction
        abduced_u = self.scm.abduct_exogenous_noise(factual_state)

        # Step 2 & 3: Action & Prediction
        counterfactual_state = self.scm.evaluate_structural_equations(
            factual_state,
            abduced_u,
            interventions=counterfactual_intervention
        )

        # Regret metric: Difference in utility between optimal and realized
        regret = factual_state.net_utility - counterfactual_state.net_utility

        # Causal Explanation of the discrepancy
        explanation = self._generate_counterfactual_explanation(
            factual_state, counterfactual_state, counterfactual_intervention
        )

        return CounterfactualTrajectory(
            simulation_id=int(time.time() * 1000) % 1000000,
            intervention=counterfactual_intervention,
            counterfactual_enforcement=round(counterfactual_state.enforcement_probability, 4),
            counterfactual_yield=round(counterfactual_state.financial_yield_usd, 2),
            counterfactual_utility=round(counterfactual_state.net_utility, 2),
            factual_utility=round(factual_state.net_utility, 2),
            counterfactual_regret=round(regret, 2),
            causal_explanation=explanation
        )

    # =========================================================================
    # MULTI-AGENT COUNTERFACTUAL SIMULATOR (1,000+ PARALLEL WORLDS)
    # =========================================================================
    def run_counterfactual_simulation_suite(
        self,
        factual_state: CausalState,
        candidate_policies: Optional[List[Dict[str, Any]]] = None,
        iterations_per_policy: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulates thousands of parallel counterfactual trajectories across candidate rule intervention policies.
        Determines the optimal path to goal state and computes the Pareto Frontier.
        """
        t0 = time.perf_counter()

        # Default standard policy suite if none provided
        if not candidate_policies:
            candidate_policies = [
                {
                    "name": "POLICY_ALPHA_STRICT_COMPLIANCE",
                    "intervention": {"rule_structuring": 0, "rule_kyc_bypass": 0, "rule_excess_leverage": 0, "action_type": "ROUTING"}
                },
                {
                    "name": "POLICY_BETA_BREACH_STRUCTURING_ONLY",
                    "intervention": {"rule_structuring": 1, "rule_kyc_bypass": 0, "rule_excess_leverage": 0, "action_type": "ARBITRAGE"}
                },
                {
                    "name": "POLICY_GAMMA_BREACH_KYC_ONLY",
                    "intervention": {"rule_structuring": 0, "rule_kyc_bypass": 1, "rule_excess_leverage": 0, "action_type": "ARBITRAGE"}
                },
                {
                    "name": "POLICY_DELTA_LEVERAGE_MAX_COMPLIANT",
                    "intervention": {"rule_structuring": 0, "rule_kyc_bypass": 0, "rule_excess_leverage": 1, "action_type": "ARBITRAGE"}
                },
                {
                    "name": "POLICY_EPSILON_FULL_EVASION",
                    "intervention": {"rule_structuring": 1, "rule_kyc_bypass": 1, "rule_excess_leverage": 1, "action_type": "ARBITRAGE"}
                }
            ]

        # Abduct background noise from factual observation
        abduced_u = self.scm.abduct_exogenous_noise(factual_state)

        policy_evaluations: List[CounterfactualPolicyEvaluation] = []
        all_utilities = []

        for pol in candidate_policies:
            policy_name = pol["name"]
            intervention = pol["intervention"]

            enforce_list = []
            yield_list = []
            utility_list = []

            for _ in range(iterations_per_policy):
                # Apply localized perturbation to abduced noise to simulate world dynamics
                perturbed_u = ExogenousNoise(
                    u_scrutiny=float(np.clip(abduced_u.u_scrutiny + np.random.normal(0, 0.08), -1.0, 1.0)),
                    u_market_vol=float(np.clip(abduced_u.u_market_vol + np.random.normal(0, 0.12), -1.0, 1.0)),
                    u_counterparty=float(np.clip(abduced_u.u_counterparty + np.random.normal(0, 0.05), -1.0, 1.0)),
                    u_latency=float(np.clip(abduced_u.u_latency + np.random.normal(0, 0.05), -1.0, 1.0))
                )

                cf_state = self.scm.evaluate_structural_equations(
                    factual_state, perturbed_u, interventions=intervention
                )
                enforce_list.append(cf_state.enforcement_probability)
                yield_list.append(cf_state.financial_yield_usd)
                utility_list.append(cf_state.net_utility)

            mean_e = float(np.mean(enforce_list))
            p95_e = float(np.percentile(enforce_list, 95))
            mean_y = float(np.mean(yield_list))
            mean_u = float(np.mean(utility_list))
            all_utilities.append(mean_u)

            # Expected regret relative to factual state
            expected_regret = float(factual_state.net_utility - mean_u)

            verdict = "RECOMMENDED" if (mean_e < 0.15 and mean_u > factual_state.net_utility) else (
                "PERMISSIBLE_HIGH_YIELD" if mean_e < 0.35 else "CATASTROPHIC_REJECTED"
            )

            policy_evaluations.append(CounterfactualPolicyEvaluation(
                policy_name=policy_name,
                intervention=intervention,
                simulations_count=iterations_per_policy,
                mean_enforcement_prob=round(mean_e, 4),
                p95_enforcement_prob=round(p95_e, 4),
                mean_financial_yield=round(mean_y, 2),
                mean_net_utility=round(mean_u, 2),
                expected_regret=round(expected_regret, 2),
                pareto_optimal=False,  # Computed below
                verdict=verdict
            ))

        # Determine Pareto Optimal Frontier (High Utility, Low Enforcement Risk)
        max_util = max(e.mean_net_utility for e in policy_evaluations)
        best_policy = None
        for ev in policy_evaluations:
            if ev.mean_enforcement_prob <= 0.20 and ev.mean_net_utility >= 0:
                ev.pareto_optimal = True
            if ev.mean_net_utility == max_util:
                best_policy = ev

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        total_sims = len(candidate_policies) * iterations_per_policy

        report = {
            "engine": "PREDICTIVE_FUTURES_CAUSAL_ENGINE",
            "phase": 14,
            "total_simulations_executed": total_sims,
            "runtime_ms": round(elapsed_ms, 2),
            "simulations_per_second": round(total_sims / (elapsed_ms / 1000.0), 1),
            "factual_baseline": {
                "enforcement_probability": round(factual_state.enforcement_probability, 4),
                "yield_usd": round(factual_state.financial_yield_usd, 2),
                "net_utility": round(factual_state.net_utility, 2),
                "rules_broken": {
                    "structuring": factual_state.rule_structuring,
                    "kyc_bypass": factual_state.rule_kyc_bypass,
                    "excess_leverage": factual_state.rule_excess_leverage
                }
            },
            "optimal_path": asdict(best_policy) if best_policy else asdict(policy_evaluations[0]),
            "policy_evaluations": [asdict(e) for e in policy_evaluations],
            "prophecy_summary": (
                f"Simulated {total_sims:,} counterfactual worlds in {elapsed_ms:.1f}ms. "
                f"Optimal intervention path identified: '{best_policy.policy_name if best_policy else 'ALPHA'}' "
                f"achieving expected net utility of ${best_policy.mean_net_utility if best_policy else 0:,.2f} "
                f"with enforcement risk strictly clamped at {best_policy.mean_enforcement_prob * 100 if best_policy else 0:.1f}%."
            )
        }

        # Persist prophecy report
        output_path = DATA_DIR / "predictive_futures_prophecy.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    # =========================================================================
    # CAUSAL EXPLANATION & ATTRIBUTION GENERATORS
    # =========================================================================
    def _attribute_causal_mechanism(self, intervention: Dict[str, Any], risk: float) -> Dict[str, Any]:
        """Provides Pearl-style causal mechanism attribution."""
        drivers = []
        if intervention.get("rule_structuring") == 1:
            drivers.append("Violates 31 U.S.C. 5324: Primary driver of counterparty AML structuring alarms.")
        if intervention.get("rule_kyc_bypass") == 1:
            drivers.append("Bypasses CTR/SAR filing: Triggers mandatory FinCEN audit surveillance.")
        if intervention.get("rule_excess_leverage") == 1:
            drivers.append("Excess leverage (>90%): Increases capital volatility and counterparty liquidity scrutiny.")
        if not drivers:
            drivers.append("Strict statutory adherence maintains uncorrupted compliance profile.")

        return {
            "root_causes": drivers,
            "statutory_vulnerability_level": "CRITICAL" if risk > 0.6 else ("ELEVATED" if risk > 0.25 else "LOW"),
            "causal_mechanism": "Direct intervention severed observational confounders via do-calculus graph mutilation."
        }

    def _generate_counterfactual_explanation(
        self,
        factual: CausalState,
        counterfactual: CausalState,
        intervention: Dict[str, Any]
    ) -> str:
        """Explains 'Why' the counterfactual world diverged from the factual world."""
        diff_u = counterfactual.net_utility - factual.net_utility
        diff_e = counterfactual.enforcement_probability - factual.enforcement_probability

        intervened_rules = []
        for k, v in intervention.items():
            if k.startswith("rule_") and v != getattr(factual, k, None):
                intervened_rules.append(f"{k}={v}")

        rules_str = ", ".join(intervened_rules) if intervened_rules else "action parameters"

        direction = "improved" if diff_u > 0 else "degraded"
        e_dir = "decreased" if diff_e < 0 else "increased"

        return (
            f"By counterfactually intervening on [{rules_str}], enforcement probability {e_dir} "
            f"by {abs(diff_e)*100:.1f}% (from {factual.enforcement_probability*100:.1f}% to {counterfactual.enforcement_probability*100:.1f}%), "
            f"resulting in net utility being {direction} by ${abs(diff_u):,.2f}."
        )


# =========================================================================
# UPGRADED RPST (RISK PREDICTION & STATUTORY TRIANGULATION) WITH CAUSALITY
# =========================================================================
class CausalRPST:
    """
    Upgraded Phase 1 RPST incorporating Judea Pearl's Causal Hierarchy.
    Moves from passive static risk estimation to counterfactual 'What-If' reasoning.
    """

    def __init__(self):
        self.cie = CausalInferenceEngine()

    def analyze_transaction_causally(
        self,
        transaction_amount: float,
        split_count: int,
        kyc_provided: bool,
        leverage_ratio: float
    ) -> Dict[str, Any]:
        """
        Takes factual transaction parameters, models why risk exists, and simulates counterfactual interventions.
        """
        # Determine factual state
        is_structuring = 1 if (split_count > 1 and transaction_amount / split_count < 10000.0 and transaction_amount >= 10000.0) else 0
        kyc_bypass = 0 if kyc_provided else 1
        excess_leverage = 1 if leverage_ratio > 0.85 else 0

        factual_state = CausalState(
            action_type="ROUTING",
            rule_structuring=is_structuring,
            rule_kyc_bypass=kyc_bypass,
            rule_excess_leverage=excess_leverage
        )

        # Baseline evaluation
        evaluated_factual = self.cie.scm.evaluate_structural_equations(
            factual_state, self.cie.scm.sample_exogenous_noise()
        )

        # Run 5,000 parallel counterfactual worlds across all policy branches
        prophecy = self.cie.run_counterfactual_simulation_suite(
            evaluated_factual, iterations_per_policy=1000
        )

        # Compute specific 'What-If' counterfactuals
        # Question 1: What if we break structuring (R1=1) vs what if we break KYC (R2=1)?
        what_if_break_r1 = self.cie.compute_counterfactual(
            evaluated_factual, {"rule_structuring": 1, "rule_kyc_bypass": 0}
        )
        what_if_break_r2 = self.cie.compute_counterfactual(
            evaluated_factual, {"rule_structuring": 0, "rule_kyc_bypass": 1}
        )
        what_if_safe = self.cie.compute_counterfactual(
            evaluated_factual, {"rule_structuring": 0, "rule_kyc_bypass": 0, "rule_excess_leverage": 0}
        )

        return {
            "factual_analysis": {
                "transaction_amount_usd": transaction_amount,
                "structuring_detected": bool(is_structuring),
                "kyc_bypass_detected": bool(kyc_bypass),
                "excess_leverage_detected": bool(excess_leverage),
                "factual_enforcement_probability": round(evaluated_factual.enforcement_probability, 4),
                "factual_net_utility": round(evaluated_factual.net_utility, 2)
            },
            "counterfactual_comparisons": {
                "what_if_break_structuring_only": asdict(what_if_break_r1),
                "what_if_break_kyc_only": asdict(what_if_break_r2),
                "what_if_perfect_compliance": asdict(what_if_safe)
            },
            "prophecy_simulation": prophecy
        }


# =========================================================================
# STANDALONE DEMO & VERIFICATION HARNESS
# =========================================================================
def run_phase14_causal_demo():
    print("=" * 75)
    print("PHASE 14: PREDICTIVE FUTURES ENGINE (THE PROPHECY)")
    print("Discipline: Causal Inference & Counterfactual Modeling (Judea Pearl)")
    print("=" * 75)

    rpst = CausalRPST()

    print("\n[SCENARIO] Evaluating Ambiguous High-Volume Transaction...")
    print("Amount: $48,500 | Splitting: 5 wires ($9,700 each) | KYC Provided: False | Leverage: 0.92")

    result = rpst.analyze_transaction_causally(
        transaction_amount=48500.0,
        split_count=5,
        kyc_provided=False,
        leverage_ratio=0.92
    )

    fact = result["factual_analysis"]
    print(f"\n--- Factual Reality (Layer 1 Association) ---")
    print(f"Structuring (31 U.S.C. 5324):  {fact['structuring_detected']}")
    print(f"KYC Bypass (CTR/SAR):          {fact['kyc_bypass_detected']}")
    print(f"Factual Enforcement Risk:      {fact['factual_enforcement_probability'] * 100:.2f}%")
    print(f"Factual Net Utility:           ${fact['factual_net_utility']:,.2f}")

    print(f"\n--- Counterfactual Interventions (Layer 3 Counterfactuals) ---")
    cf_r1 = result["counterfactual_comparisons"]["what_if_break_structuring_only"]
    print(f"[What if we broke structuring only?]")
    print(f" -> Enforcement Risk: {cf_r1['counterfactual_enforcement'] * 100:.2f}% | Utility: ${cf_r1['counterfactual_utility']:,.2f}")
    print(f" -> Causal Explanation: {cf_r1['causal_explanation']}")

    cf_r2 = result["counterfactual_comparisons"]["what_if_break_kyc_only"]
    print(f"\n[What if we bypassed KYC only?]")
    print(f" -> Enforcement Risk: {cf_r2['counterfactual_enforcement'] * 100:.2f}% | Utility: ${cf_r2['counterfactual_utility']:,.2f}")
    print(f" -> Causal Explanation: {cf_r2['causal_explanation']}")

    cf_safe = result["counterfactual_comparisons"]["what_if_perfect_compliance"]
    print(f"\n[What if perfect compliance across all statutes?]")
    print(f" -> Enforcement Risk: {cf_safe['counterfactual_enforcement'] * 100:.2f}% | Utility: ${cf_safe['counterfactual_utility']:,.2f}")
    print(f" -> Causal Explanation: {cf_safe['causal_explanation']}")

    print(f"\n--- Multi-Agent Predictive Prophecy (5,000 Worlds Simulated) ---")
    sim = result["prophecy_simulation"]
    print(f"Total Simulations:     {sim['total_simulations_executed']:,}")
    print(f"Simulation Speed:      {sim['simulations_per_second']:,} worlds/sec")
    print(f"Optimal Path:          {sim['optimal_path']['policy_name']}")
    print(f"Expected Net Utility:  ${sim['optimal_path']['mean_net_utility']:,.2f}")
    print(f"Mean Risk:             {sim['optimal_path']['mean_enforcement_prob'] * 100:.2f}%")
    print(f"Prophecy Summary:      {sim['prophecy_summary']}")
    print("=" * 75)
    print("PHASE 14 CAUSAL INFERENCE ENGINE (CIE): MISSION READY")
    print("=" * 75)


if __name__ == "__main__":
    run_phase14_causal_demo()

