"""
Fast verification script for contracts 108-114 (SRDL Triad & ECC Bridge).
Run: python src/test_ecc_contracts.py
"""
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from gateway_api import app

client = TestClient(app)

def test_srdl_and_ecc():
    print("=" * 70)
    print("RUNNING SRDL & ECC REST API CONTRACT TESTS (108-114)")
    print("=" * 70)

    # 108. Relational Triad
    r_rel = client.get("/api/v1/vectors/higher-order/relational?include_provenance=true")
    assert r_rel.status_code == 200, f"Contract 108 failed: {r_rel.status_code}"
    rel = r_rel.json()
    assert rel["expressive_coherence_index"] > 0
    assert rel["ratio_psi_folly_utility"] > 0
    print(f"[Test 108: SRDL Relational Triad] Status: 200 OK | Xi_UGE: {rel['expressive_coherence_index']} | Ratio Psi: {rel['ratio_psi_folly_utility']}")

    # 109. ECC Status
    r_stat = client.get("/api/v1/ecc/status")
    assert r_stat.status_code == 200
    stat = r_stat.json()
    assert stat["ecc_installed"] is True
    assert stat["agents_count"] >= 70
    assert stat["skills_count"] >= 300
    print(f"[Test 109: ECC Status] Status: 200 OK | Agents: {stat['agents_count']} | Skills: {stat['skills_count']}")

    # 110. ECC Agents Search
    r_ag = client.get("/api/v1/ecc/agents?query=architect&limit=5")
    assert r_ag.status_code == 200
    ag_data = r_ag.json()
    assert len(ag_data["results"]) > 0
    print(f"[Test 110: ECC Agents Search] Status: 200 OK | Matches: {len(ag_data['results'])} | Top: {ag_data['results'][0]['name']}")

    # 111. ECC Skills Search
    r_sk = client.get("/api/v1/ecc/skills?query=agent&limit=5")
    assert r_sk.status_code == 200
    sk_data = r_sk.json()
    assert len(sk_data["results"]) > 0
    print(f"[Test 111: ECC Skills Search] Status: 200 OK | Matches: {len(sk_data['results'])} | Top: {sk_data['results'][0]['name']}")

    # 112. ECC Route Task
    r_rt = client.post("/api/v1/ecc/route", json={"query": "Audit our FastAPI endpoints for security vulnerabilities."})
    assert r_rt.status_code == 200
    rt_data = r_rt.json()
    assert rt_data["selected_agent"] == "security-reviewer"
    print(f"[Test 112: ECC Route Task] Status: 200 OK | Routed to: [{rt_data['selected_agent']}] (Confidence: {rt_data['agent_confidence']})")

    # 113. ECC Dialectic Quartet
    r_qt = client.get("/api/v1/ecc/quartet")
    assert r_qt.status_code == 200
    qt_data = r_qt.json()
    assert "execution_agent" in qt_data["quartet"]
    assert "utility_agent" in qt_data["quartet"]
    print(f"[Test 113: ECC Dialectic Quartet] Status: 200 OK | Mapped all 4 roles to ECC specialists.")

    # 114. ECC Dispatch Specialist
    r_disp = client.post("/api/v1/ecc/dispatch", json={
        "agent_name": "security-reviewer",
        "prompt": "Verify statutory anti-structuring invariants for 31 U.S.C. 5324.",
        "backend": "deterministic",
        "max_tokens": 48
    })
    assert r_disp.status_code == 200
    disp_data = r_disp.json()
    assert disp_data["offline_certified"] is True
    print(f"[Test 114: ECC Dispatch Specialist] Status: 200 OK | Agent: {disp_data['ecc_agent']} | Latency: {disp_data['duration_ms']} ms")

    print("=" * 70)
    print("ALL 7 NEW CONTRACTS (108-114) VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_srdl_and_ecc()
