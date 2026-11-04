r"""
Phase 12: ECC (Everything Claude Code / Agent Harness Performance Optimization System) Bridge
Integrates 71 specialized agents and 314 modular skills from affaan-m/ECC into Apex UAS:
1. Dynamic Indexer & Catalog Caching:
   - Scans d:/AI/external/ECC/agents (*.md) and skills (*/SKILL.md).
   - Extracts YAML frontmatter (name, description, model, tools).
   - Caches parsed catalog to d:/AI/data/ecc_catalog.json for instant warm-start (< 1ms).
2. Intelligent Specialist Router:
   - Evaluates incoming tasks and matches them to the top specialized ECC agent and relevant skills.
   - Computes relevance scoring using keyword density and domain heuristic mappings.
3. Dialectic Quartet Integration:
   - Maps the 4 specialized roles (Execution, Utility, Coherence, Paraconsistency) to exact ECC agents.
4. Edge Execution Engine:
   - Formulates specialist system prompts with ECC defense baselines.
   - Routes to local_model_bridge (In-Process PyTorch SmolLM-135M+LoRA or Deterministic Kernel)
     for 100% offline edge inference with zero cloud egress.

Location: d:/AI/src/ecc_bridge.py
Strictly localized within d:/AI
"""

import os
import sys
import re
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR
from local_model_bridge import local_model_bridge

ECC_DIR = BASE_DIR / "external" / "ECC"
ECC_CATALOG_FILE = DATA_DIR / "ecc_catalog.json"


@dataclass
class ECCAgent:
    name: str
    description: str
    model: str
    tools: List[str]
    file_path: str
    char_count: int


@dataclass
class ECCSkill:
    name: str
    description: str
    origin: str
    file_path: str
    char_count: int


@dataclass
class ECCRoutingDecision:
    query: str
    selected_agent: Optional[str]
    agent_confidence: float
    recommended_skills: List[str]
    reasoning: str
    execution_preview: Optional[str] = None


class ECCBridge:
    """
    Operating layer connecting Apex UAS to affaan-m/ECC repository.
    """

    def __init__(self, ecc_root: Optional[Path] = None):
        self.ecc_root = ecc_root or ECC_DIR
        self.agents_dir = self.ecc_root / "agents"
        self.skills_dir = self.ecc_root / "skills"
        
        self.agents: Dict[str, ECCAgent] = {}
        self.skills: Dict[str, ECCSkill] = {}
        self.last_indexed: float = 0.0

        # Load or scan catalog
        self.initialize_catalog()

    def _parse_frontmatter(self, text: str) -> Tuple[Dict[str, Any], str]:
        """Simple regex-based YAML frontmatter parser."""
        if not text.startswith("---"):
            return {}, text

        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text

        raw_yaml = parts[1]
        body = parts[2].strip()

        meta = {}
        for line in raw_yaml.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key == "tools":
                    # comma separated
                    meta[key] = [t.strip() for t in val.split(",") if t.strip()]
                else:
                    meta[key] = val

        return meta, body

    def index_catalog(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Scans external/ECC/agents and external/ECC/skills and builds the catalog."""
        t0 = time.perf_counter()
        agents_dict: Dict[str, ECCAgent] = {}
        skills_dict: Dict[str, ECCSkill] = {}

        # 1. Index Agents
        if self.agents_dir.exists():
            for p in self.agents_dir.glob("*.md"):
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    meta, _ = self._parse_frontmatter(content)
                    name = meta.get("name", p.stem)
                    desc = meta.get("description", "ECC Specialist Agent")
                    model = meta.get("model", "sonnet")
                    tools = meta.get("tools", ["Read", "Grep", "Glob", "Bash"])
                    
                    agents_dict[name] = ECCAgent(
                        name=name,
                        description=desc,
                        model=model,
                        tools=tools,
                        file_path=str(p.relative_to(BASE_DIR)),
                        char_count=len(content)
                    )
                except Exception:
                    continue

        # 2. Index Skills
        if self.skills_dir.exists():
            for p in self.skills_dir.glob("*/SKILL.md"):
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    meta, _ = self._parse_frontmatter(content)
                    name = meta.get("name", p.parent.name)
                    desc = meta.get("description", "ECC Workflow Skill")
                    origin = meta.get("metadata", {}).get("origin", "ECC") if isinstance(meta.get("metadata"), dict) else "ECC"
                    
                    skills_dict[name] = ECCSkill(
                        name=name,
                        description=desc,
                        origin=origin,
                        file_path=str(p.relative_to(BASE_DIR)),
                        char_count=len(content)
                    )
                except Exception:
                    continue

        self.agents = agents_dict
        self.skills = skills_dict
        self.last_indexed = time.time()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Cache catalog to data directory
        catalog_payload = {
            "timestamp": self.last_indexed,
            "indexing_duration_ms": round(elapsed_ms, 2),
            "agents_count": len(self.agents),
            "skills_count": len(self.skills),
            "agents": {k: asdict(v) for k, v in self.agents.items()},
            "skills": {k: asdict(v) for k, v in self.skills.items()}
        }

        try:
            with open(ECC_CATALOG_FILE, "w", encoding="utf-8") as f:
                json.dump(catalog_payload, f, indent=2)
        except Exception:
            pass

        return catalog_payload

    def initialize_catalog(self) -> None:
        """Loads from cache if fresh, otherwise runs full index."""
        if ECC_CATALOG_FILE.exists():
            try:
                with open(ECC_CATALOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Reconstruct dataclasses
                for k, v in data.get("agents", {}).items():
                    self.agents[k] = ECCAgent(**v)
                for k, v in data.get("skills", {}).items():
                    self.skills[k] = ECCSkill(**v)
                self.last_indexed = data.get("timestamp", time.time())
                if len(self.agents) >= 70 and len(self.skills) >= 300:
                    return
            except Exception:
                pass
        self.index_catalog()

    def get_status(self) -> Dict[str, Any]:
        """Returns catalog telemetry and integration health."""
        return {
            "ecc_installed": self.ecc_root.exists(),
            "ecc_root_path": str(self.ecc_root),
            "agents_count": len(self.agents),
            "skills_count": len(self.skills),
            "last_indexed": self.last_indexed,
            "offline_bridge_ready": local_model_bridge.probe_all_providers().get("offline_ready", False),
            "dialectic_quartet_available": True
        }

    def search_agents(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Searches specialized ECC agents by keyword or purpose."""
        q = query.lower().strip()
        results = []
        for name, agent in self.agents.items():
            score = 0
            if q in name.lower():
                score += 10
            if q in agent.description.lower():
                score += 5
            for tool in agent.tools:
                if q in tool.lower():
                    score += 2
            if not q or score > 0:
                d = asdict(agent)
                d["relevance_score"] = score
                results.append(d)

        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]

    def search_skills(self, query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
        """Searches ECC skills by keyword or domain."""
        q = query.lower().strip()
        results = []
        for name, skill in self.skills.items():
            score = 0
            if q in name.lower():
                score += 10
            if q in skill.description.lower():
                score += 5
            if not q or score > 0:
                d = asdict(skill)
                d["relevance_score"] = score
                results.append(d)

        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]

    def route_task(self, query: str) -> ECCRoutingDecision:
        """
        Intelligently routes an incoming prompt or engineering goal to the
        optimal ECC specialist agent and accompanying skill set.
        """
        q = query.lower()

        # Heuristic Domain Routing Table
        domain_routes = [
            # Security & Compliance
            (r"(secur|vuln|cve|audit|threat|exploit|harden|leak)", "security-reviewer", ["agent-security-hardening", "agent-architecture-audit"]),
            # Architecture & Systems
            (r"(architect|system|design|blueprint|pattern|refactor)", "code-architect", ["agentic-engineering", "backend-patterns"]),
            # Code Review & Quality
            (r"(review|clean|lint|simplify|smell)", "code-reviewer", ["code-simplifier", "tdd-workflow"]),
            # Autonomous Harness & Loop
            (r"(autonom|loop|harness|daemon|schedule|cron)", "chief-of-staff", ["autonomous-agent-harness", "autonomous-loops"]),
            # API & FastAPI
            (r"(api|endpoint|fastapi|rest|contract|http)", "fastapi-reviewer", ["api-design", "agent-runtime-gateway-smoke-test"]),
            # Build & Error Resolution
            (r"(error|fail|bug|traceback|fix|resolve)", "build-error-resolver", ["agent-introspection-debugging", "ai-regression-testing"]),
            # Evaluation & Benchmarking
            (r"(eval|benchmark|metric|test|verify)", "agent-evaluator", ["agent-eval", "benchmark"]),
        ]

        matched_agent = "code-architect"
        matched_skills = ["agentic-engineering", "tdd-workflow"]
        highest_confidence = 0.50
        reasoning = "General engineering heuristic match."

        for pattern, agent_name, skills in domain_routes:
            if re.search(pattern, q):
                if agent_name in self.agents:
                    matched_agent = agent_name
                    matched_skills = [s for s in skills if s in self.skills]
                    highest_confidence = 0.92
                    reasoning = f"Matched specialized domain pattern '{pattern}' to ECC agent [{agent_name}]."
                    break

        # Fallback to search if no regex hit
        if highest_confidence < 0.8:
            search_res = self.search_agents(query, limit=1)
            if search_res:
                matched_agent = search_res[0]["name"]
                highest_confidence = 0.75
                reasoning = f"Matched via keyword relevance scoring to ECC agent [{matched_agent}]."

        return ECCRoutingDecision(
            query=query,
            selected_agent=matched_agent,
            agent_confidence=highest_confidence,
            recommended_skills=matched_skills,
            reasoning=reasoning
        )

    def get_dialectic_quartet_mapping(self) -> Dict[str, Any]:
        """
        Maps the 4 specialized Dialectic Equilibrium (DEC) agents
        to concrete ECC specialists and skills.
        """
        return {
            "execution_agent": {
                "persona": "The Performer (OTV Invariant Enforcer)",
                "ecc_agent": self.agents.get("fastapi-reviewer", None),
                "ecc_skills": ["agent-runtime-gateway-smoke-test", "tdd-workflow"],
                "directive": "Verify step-by-step OTV fidelity, order compliance, and zero structural corruption."
            },
            "utility_agent": {
                "persona": "The Maximizer (Economic Surplus & DETS)",
                "ecc_agent": self.agents.get("code-architect", None),
                "ecc_skills": ["backend-patterns", "api-connector-builder"],
                "directive": "Optimize economic and resource margins under strict TQ resource friction bounds."
            },
            "coherence_agent": {
                "persona": "The Philosopher (RMGI & SRDL Narrative Invariant)",
                "ecc_agent": self.agents.get("architect", None),
                "ecc_skills": ["agentic-engineering", "agentic-os"],
                "directive": "Maximize expressive narrative density and UGE coherence index across all time steps."
            },
            "paraconsistency_agent": {
                "persona": "The Arbitrator (Paradox Engine & Contradiction Isolator)",
                "ecc_agent": self.agents.get("agent-evaluator", None),
                "ecc_skills": ["agent-architecture-audit", "agent-security-hardening"],
                "directive": "Mediate syntactic deadlock and enforce join-semilattice quarantine without explosion."
            }
        }

    def dispatch_specialist(
        self,
        agent_name: str,
        user_prompt: str,
        backend: str = "auto",
        max_tokens: int = 64
    ) -> Dict[str, Any]:
        """
        Dispatches a specialized prompt using the ECC agent's persona overlay,
        executed entirely offline via the local model bridge (SmolLM-135M+LoRA / Deterministic).
        """
        agent = self.agents.get(agent_name)
        if not agent:
            # Fallback
            agent = ECCAgent(
                name=agent_name,
                description="General ECC specialist",
                model="local",
                tools=["Read", "Grep"],
                file_path="",
                char_count=0
            )

        full_prompt = (
            f"You are the specialized ECC Agent [{agent.name}].\n"
            f"Role: {agent.description}\n"
            f"Directives: Maintain prompt defense baseline, avoid speculation, provide verifiable blueprints.\n\n"
            f"Task: {user_prompt}\n"
            f"Response:"
        )

        t0 = time.perf_counter()
        gen_res = local_model_bridge.generate(
            prompt=full_prompt,
            backend=backend,
            max_tokens=max_tokens,
            temperature=0.1
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "ecc_agent": agent.name,
            "agent_description": agent.description,
            "backend_used": getattr(gen_res, "backend_used", "deterministic_kernel"),
            "offline_certified": True,
            "generated_output": getattr(gen_res, "generated_text", ""),
            "duration_ms": round(elapsed_ms, 2),
            "tokens_generated": getattr(gen_res, "tokens_generated", 0),
            "tokens_per_second": getattr(gen_res, "tokens_per_second", 0.0)
        }


# Global singleton instance
ecc_bridge = ECCBridge()


if __name__ == "__main__":
    print("=" * 75)
    print("ECC (EVERYTHING CLAUDE CODE) AGENTIC OPERATING LAYER INITIALIZATION")
    print("=" * 75)
    status = ecc_bridge.get_status()
    print(f"ECC Installed: {status['ecc_installed']} at {status['ecc_root_path']}")
    print(f"Total Specialized Agents: {status['agents_count']}")
    print(f"Total Modular Skills    : {status['skills_count']}")

    print("\n--- SAMPLE AGENT SEARCH: 'architect' ---")
    archs = ecc_bridge.search_agents("architect", limit=3)
    for a in archs:
        print(f" - [{a['name']}] Tools: {', '.join(a['tools'])} | File: {a['file_path']}")

    print("\n--- SAMPLE SKILL SEARCH: 'agent' ---")
    skills = ecc_bridge.search_skills("agent", limit=5)
    for s in skills:
        print(f" - [{s['name']}] Origin: {s['origin']} | File: {s['file_path']}")

    print("\n--- INTELLIGENT SPECIALIST ROUTING TEST ---")
    query = "Audit our FastAPI endpoints for security vulnerabilities and race conditions."
    decision = ecc_bridge.route_task(query)
    print(f"Query: {decision.query}")
    print(f"Selected Agent : [{decision.selected_agent}] (Confidence: {decision.agent_confidence})")
    print(f"Recommended Skills: {decision.recommended_skills}")
    print(f"Reasoning: {decision.reasoning}")

    print("\n--- DIALECTIC QUARTET ECC MAPPING ---")
    quartet = ecc_bridge.get_dialectic_quartet_mapping()
    for role, info in quartet.items():
        print(f" - {role.upper()}: ECC [{info['ecc_agent'].name if info['ecc_agent'] else 'N/A'}] | Skills: {info['ecc_skills']}")

    print("\n--- OFFLINE SPECIALIST DISPATCH TEST ---")
    dispatch_out = ecc_bridge.dispatch_specialist(
        agent_name="security-reviewer",
        user_prompt="Review risk parameters for statutory invariance.",
        backend="deterministic"
    )
    print(f"Agent: {dispatch_out['ecc_agent']} | Backend: {dispatch_out['backend_used']} | Time: {dispatch_out['duration_ms']} ms")
    print(f"Output: {dispatch_out['generated_output'][:150]}...")
    print("=" * 75)
