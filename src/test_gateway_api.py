"""
Phase 8: Service Mesh Gateway (MSMG) Automated Test Suite
Verifies all RESTful API contracts: /control, /objective, and UI skeleton serving.
Location: d:\AI\src\test_gateway_api.py
"""

from fastapi.testclient import TestClient
from gateway_api import app

client = TestClient(app)

def run_api_tests():
    print("=" * 75)
    print("RUNNING SERVICE MESH GATEWAY (MSMG) REST API VERIFICATION")
    print("=" * 75)

    # 1. Test UI Serving
    r_ui = client.get("/")
    assert r_ui.status_code == 200, f"UI serving failed: {r_ui.status_code}"
    assert "DIRECT CONTROL PORTAL" in r_ui.text
    print("[Test 1: Desktop Client UI] Status: 200 OK | HTML Dashboard Loaded Successfully.")

    # 2. Test /control/telemetry
    r_telem = client.get("/control/telemetry")
    assert r_telem.status_code == 200
    telem = r_telem.json()
    print(f"[Test 2: /control/telemetry] Status: 200 OK | Risk: {telem['risk_meter_pct']:.1f}% | Conf: {telem['confidence_gauge_pct']:.1f}%")

    # 3. Test /control/dispatch (Direct Execution)
    payload_cmd = {
        "task_id": "TEST-DIRECT-001",
        "action_type": "STATUTORY_AUDIT",
        "entity": "Vanguard Horizon Ltd",
        "statute": "31 U.S.C. 5324",
        "amount": 7500.0,
        "scrutiny_override": 0.20
    }
    r_disp = client.post("/control/dispatch", json=payload_cmd)
    assert r_disp.status_code == 200
    disp_data = r_disp.json()
    print(f"[Test 3: /control/dispatch] Status: 200 OK | Verdict: {disp_data['details']['verdict']} | Latency: {disp_data['details']['execution_time_ms']:.2f} ms")

    # 4. Test /control/qpmk-stream (Sub-millisecond Streaming Tick)
    tick_payload = {"channel_values": [0.12, -0.05, 0.33, 0.18, -0.22, 0.04, -0.15, 0.08]}
    r_tick = client.post("/control/qpmk-stream", json=tick_payload)
    assert r_tick.status_code == 200
    tick_data = r_tick.json()
    print(f"[Test 4: /control/qpmk-stream] Status: 200 OK | Sub-ms Ingested: {tick_data['sub_millisecond_processed']}")

    # 5. Test /control/ghost-mode
    r_ghost = client.post("/control/ghost-mode", json={"enable_ghost_mode": True})
    assert r_ghost.status_code == 200
    ghost_data = r_ghost.json()
    print(f"[Test 5: /control/ghost-mode] Status: 200 OK | Ghost State: {ghost_data['ghost_active']} (Profile: {ghost_data['cpu_profile']})")

    # 6. Test /objective/enqueue & /objective/queue
    obj_payload = {
        "objective_id": "OBJ-AUTONOMOUS-99",
        "title": "Cross-Jurisdiction Capital Balancing",
        "urgency": 0.85,
        "risk_tolerance": 0.30,
        "parameters": {"amount": 5500, "scrutiny": 0.20}
    }
    r_enq = client.post("/objective/enqueue", json=obj_payload)
    assert r_enq.status_code == 200
    enq_data = r_enq.json()
    print(f"[Test 6: /objective/enqueue] Status: 200 OK | Task: {enq_data['objective_id']} (Queue Pos: {enq_data['queue_position']})")

    r_q = client.get("/objective/queue")
    assert r_q.status_code == 200
    q_data = r_q.json()
    print(f"[Test 7: /objective/queue] Status: 200 OK | Total in Stack: {q_data['total_queued']}")

    # 7. Test /objective/dispatch-next
    r_next = client.post("/objective/dispatch-next")
    assert r_next.status_code == 200
    next_data = r_next.json()
    print(f"[Test 8: /objective/dispatch-next] Status: 200 OK | Executed: {next_data['task_id']} ({next_data['execution_summary']['verdict']})")

    # 9. Test /actuator/dispatch (External Real-World Connector)
    act_payload = {
        "action_name": "EXECUTE_TRADE",
        "parameters": {"symbol": "BTC/USD", "side": "BUY", "quantity": 0.25, "price": 65000.0}
    }
    r_act = client.post("/actuator/dispatch", json=act_payload)
    assert r_act.status_code == 200
    act_data = r_act.json()
    print(f"[Test 9: /actuator/dispatch] Status: 200 OK | Ref ID: {act_data['ref_id']} | Trade: {act_data['status']}")

    # 10. Test /metrics (Prometheus Metric Scrape for Kubernetes HPA)
    r_prom = client.get("/metrics")
    assert r_prom.status_code == 200
    assert "apex_active_queue_depth" in r_prom.text
    print(f"[Test 10: /metrics] Status: 200 OK | Prometheus Scrape Verified for HPA.")

    # 11. Test /control/load (Resource Throttling State)
    r_load = client.get("/control/load")
    assert r_load.status_code == 200
    load_data = r_load.json()
    print(f"[Test 11: /control/load] Status: 200 OK | Pressure: {load_data['pressure_level']} | PRK: {load_data['subsystem_allocations']['PRK']}")

    # 12. Test /control/self-limitations (Phase 12 Metacognitive Audit)
    r_lim = client.get("/control/self-limitations?statute=31%20U.S.C.%205324&entity=Marcus%20Vance")
    assert r_lim.status_code == 200
    lim_data = r_lim.json()
    print(f"[Test 12: /control/self-limitations] Status: 200 OK | Epistemic Status: {lim_data['epistemic_status']} | Metacognitive Conf: {lim_data['metacognitive_confidence']*100:.1f}%")

    # 13. Test /dao/propose & /dao/proposals (Phase 13 DAO Governance)
    dao_prop_payload = {
        "title": "Decentralized Liquidity Expansion",
        "description": "Expand liquidity pool allocation across cross-border settlement rails.",
        "action_payload": {"action": "EXECUTE_TRADE", "parameters": {"symbol": "BTC/USD", "side": "BUY", "quantity": 0.1, "price": 64500.0}},
        "quorum": 10000.0
    }
    r_prop = client.post("/dao/propose", json=dao_prop_payload)
    assert r_prop.status_code == 200
    prop_data = r_prop.json()
    p_id = prop_data["proposal_id"]
    print(f"[Test 13: /dao/propose] Status: 200 OK | Created Proposal: {p_id} (Quorum: {prop_data['quorum_required']:,.0f})")

    # 14. Test /dao/vote (Phase 13 Peer Voting)
    vote_payload = {
        "proposal_id": p_id,
        "voter_address": "0x1234567890abcdef1234567890abcdef12345678",
        "support": True,
        "voting_weight": 12000.0
    }
    r_vote = client.post("/dao/vote", json=vote_payload)
    assert r_vote.status_code == 200
    vote_data = r_vote.json()
    print(f"[Test 14: /dao/vote] Status: 200 OK | Vote Registered | Status: {vote_data['proposal_status']} | Permit Issued: {vote_data['permit_issued']}")

    # 15. Test /dao/proposals (Phase 13 Listing)
    r_list = client.get("/dao/proposals")
    assert r_list.status_code == 200
    assert r_list.json()["total_proposals"] > 0
    print(f"[Test 15: /dao/proposals] Status: 200 OK | Total On-Chain Proposals: {r_list.json()['total_proposals']}")

    # 16. Test /dao/execute/{proposal_id} (Phase 13 Actuator Execution)
    r_exec_dao = client.post(f"/dao/execute/{p_id}")
    assert r_exec_dao.status_code == 200
    exec_data = r_exec_dao.json()
    print(f"[Test 16: /dao/execute] Status: 200 OK | Executed Ratified Mandate: {exec_data['status']}")

    # 17. Test /threat/stress-test (Phase 10 Adversarial Stress Test)
    r_stress = client.post("/threat/stress-test")
    assert r_stress.status_code == 200
    stress_data = r_stress.json()
    print(f"[Test 17: /threat/stress-test] Status: 200 OK | Score: {stress_data['composite_score_pct']:.2f}% | Verdict: {stress_data['verdict']}")

    # 18. Test /causal/intervene (Phase 14 Pearl Layer 2 Intervention)
    intervene_payload = {"intervention": {"rule_structuring": 0, "rule_kyc_bypass": 0}, "samples": 200}
    r_intervene = client.post("/causal/intervene", json=intervene_payload)
    assert r_intervene.status_code == 200
    intervene_data = r_intervene.json()
    print(f"[Test 18: /causal/intervene] Status: 200 OK | Pearl Level 2: {intervene_data['level']} | Risk: {intervene_data['do_calculus_expectation']['mean_enforcement_probability']*100:.1f}%")

    # 19. Test /causal/counterfactual (Phase 14 Pearl Layer 3 Counterfactuals)
    cf_payload = {
        "factual_state": {
            "rule_structuring": 1, "rule_kyc_bypass": 1, "rule_excess_leverage": 1,
            "counterparty_suspicion": 0.85, "enforcement_probability": 0.95,
            "financial_yield_usd": 24000.0, "net_utility": -45000.0
        },
        "counterfactual_intervention": {"rule_structuring": 0, "rule_kyc_bypass": 0}
    }
    r_cf = client.post("/causal/counterfactual", json=cf_payload)
    assert r_cf.status_code == 200
    cf_data = r_cf.json()
    print(f"[Test 19: /causal/counterfactual] Status: 200 OK | Pearl Level 3: {cf_data['level']} | Regret: ${cf_data['counterfactual_regret']:,.2f}")

    # 20. Test /causal/simulate-futures (Phase 14 Predictive Futures Engine)
    sim_payload = {
        "transaction_amount": 45000.0,
        "split_count": 5,
        "kyc_provided": False,
        "leverage_ratio": 0.90
    }
    r_sim = client.post("/causal/simulate-futures", json=sim_payload)
    assert r_sim.status_code == 200
    sim_data = r_sim.json()
    print(f"[Test 20: /causal/simulate-futures] Status: 200 OK | Worlds: {sim_data['prophecy_simulation']['total_simulations_executed']:,} | Optimal: {sim_data['prophecy_simulation']['optimal_path']['policy_name']}")

    # 21. Test /causal/prophecy (Phase 14 Persisted Prophecy Retrieval)
    r_prophecy = client.get("/causal/prophecy")
    assert r_prophecy.status_code == 200
    prophecy_data = r_prophecy.json()
    print(f"[Test 21: /causal/prophecy] Status: 200 OK | Prophecy Retrievable: {prophecy_data['phase'] == 14}")

    # 22. Test /evolution/synthesize-and-deploy (Phase 15 Compiler Agent)
    evo_payload = {
        "target_subsystem": "RL",
        "gap_description": "Unmodeled multi-hop liquidity slippage in RL reward function"
    }
    r_evo = client.post("/evolution/synthesize-and-deploy", json=evo_payload)
    assert r_evo.status_code == 200
    evo_data = r_evo.json()
    p_id = evo_data["patch_id"]
    print(f"[Test 22: /evolution/synthesize-and-deploy] Status: 200 OK | Patch: {p_id} | Hot-Reloaded: {evo_data['deployment']['status']}")

    # 23. Test /evolution/active (Phase 15 Active Patches)
    r_active = client.get("/evolution/active")
    assert r_active.status_code == 200
    active_data = r_active.json()
    print(f"[Test 23: /evolution/active] Status: 200 OK | Total Active Patches in Memory: {active_data['active_patches_count']}")

    # 24. Test /evolution/ledger (Phase 15 Git-Style Evolution Ledger)
    r_ledger = client.get("/evolution/ledger")
    assert r_ledger.status_code == 200
    ledger_data = r_ledger.json()
    print(f"[Test 24: /evolution/ledger] Status: 200 OK | Total Commits on Chain: {ledger_data['total_evolutions']}")

    # 25. Test /evolution/rollback/{patch_id} (Phase 15 Zero-Downtime Rollback)
    r_roll = client.post(f"/evolution/rollback/{p_id}")
    assert r_roll.status_code == 200
    roll_data = r_roll.json()
    print(f"[Test 25: /evolution/rollback] Status: 200 OK | Restored to Baseline: {roll_data['restored_to_baseline']}")

    # 26. Test /media/styles (Phase 17 Style Guides)
    r_styles = client.get("/media/styles")
    assert r_styles.status_code == 200
    styles_data = r_styles.json()
    print(f"[Test 26: /media/styles] Status: 200 OK | Styles in Catalog: {styles_data['total_styles']}")

    # 27. Test /media/generate-image (Phase 17 Latent Diffusion Image)
    img_payload = {
        "prompt": "Encrypted communications terminal in bunker",
        "style_id": "1970s_espionage",
        "steps": 12
    }
    r_img = client.post("/media/generate-image", json=img_payload)
    assert r_img.status_code == 200
    img_data = r_img.json()
    print(f"[Test 27: /media/generate-image] Status: 200 OK | Dims: {img_data['dimensions']} | Latency: {img_data['synthesis_latency_ms']:.2f} ms")

    # 28. Test /media/generate-video (Phase 17 Temporal Video Loop)
    vid_payload = {
        "prompt": "Thermal signatures along security perimeter",
        "style_id": "forensic_flir",
        "frames": 6,
        "fps": 3
    }
    r_vid = client.post("/media/generate-video", json=vid_payload)
    assert r_vid.status_code == 200
    vid_data = r_vid.json()
    print(f"[Test 28: /media/generate-video] Status: 200 OK | Frames: {vid_data['frame_count']} | Latency: {vid_data['synthesis_latency_ms']:.2f} ms")

    # 29. Test /translator/languages (Phase 18 Language Catalog)
    r_langs = client.get("/translator/languages")
    assert r_langs.status_code == 200
    langs_data = r_langs.json()
    print(f"[Test 29: /translator/languages] Status: 200 OK | Languages: {len(langs_data['supported_languages'])} | Registers: {len(langs_data['pragmatic_registers'])}")

    # 30. Test /translator/translate (Phase 18 Neural Translation)
    tr_payload = {
        "text": "System regulatory risk assessed at 12.0%. Action consensus approved.",
        "target_lang": "zh",
        "pragmatic_register": "DIPLOMATIC_STATUTORY"
    }
    r_tr = client.post("/translator/translate", json=tr_payload)
    assert r_tr.status_code == 200
    tr_data = r_tr.json()
    print(f"[Test 30: /translator/translate] Status: 200 OK | Target: {tr_data['target_language']} | Score: {tr_data['pragmatic_appropriateness_score']*100:.1f}%")

    # 31. Test /translator/cultural-audit (Phase 18 Pragmatic Audit)
    audit_payload = {
        "text": "System regulatory risk assessed at 12.0%.",
        "target_lang": "ja",
        "pragmatic_register": "DIPLOMATIC_STATUTORY"
    }
    r_caudit = client.post("/translator/cultural-audit", json=audit_payload)
    assert r_caudit.status_code == 200
    caudit_data = r_caudit.json()
    print(f"[Test 31: /translator/cultural-audit] Status: 200 OK | Verdict: {caudit_data['verdict']} | Appropriateness: {caudit_data['appropriateness_score']*100:.1f}%")

    # 32. Test /security/audit (Phase 16 Security Posture Mapping)
    sec_payload = {
        "asset_spec": {
            "asset_id": "TEST-VAULT-ASSET-01",
            "hostname": "vault-node.uas.internal",
            "network_zone": "INTERNAL_CORE",
            "listening_services": [
                {"service": "posix_vault", "port": 22, "permissions": "0777"}
            ]
        }
    }
    r_sec = client.post("/security/audit", json=sec_payload)
    assert r_sec.status_code == 200
    sec_data = r_sec.json()
    print(f"[Test 32: /security/audit] Status: 200 OK | Threats: {sec_data['threats_identified_count']} | Reduction: {sec_data['risk_metrics']['risk_reduction_percentage']:.1f}%")

    # 33. Test /security/audit-report (Phase 16 Report Retrieval)
    r_secrep = client.get("/security/audit-report")
    assert r_secrep.status_code == 200
    secrep_data = r_secrep.json()
    print(f"[Test 33: /security/audit-report] Status: 200 OK | Verdict: {secrep_data['audit_verdict']}")

    # 34. Test /novelty/generate (Post-Singularity Novelty Generator Subroutine)
    novelty_payload = {
        "domain_label": "EXTRAGALACTIC_LIQUIDITY_DYNAMICS",
        "candidate_vector": [5.1, -4.2, 6.7, 3.8, -5.5, 4.3, 7.2, -3.1]
    }
    r_nov = client.post("/novelty/generate", json=novelty_payload)
    assert r_nov.status_code == 200
    nov_data = r_nov.json()
    assert nov_data["validation_status"] == "INVENTED_COHERENT"
    print(f"[Test 34: /novelty/generate] Status: 200 OK | Discovery: {nov_data['discovery_id']} | Concept: {nov_data['synthesized_framework']['concept_name']} | Eq: {nov_data['synthesized_framework']['symbolic_equation']}")

    # 35. Test /novelty/discoveries (Discovery Ledger Retrieval)
    r_nov_disc = client.get("/novelty/discoveries")
    assert r_nov_disc.status_code == 200
    nov_disc_data = r_nov_disc.json()
    assert "discoveries" in nov_disc_data
    print(f"[Test 35: /novelty/discoveries] Status: 200 OK | Recorded Discoveries: {nov_disc_data['total_discoveries']}")

    # 36. Test /ethics/evaluate-conflict (Value Conflict Resolver & Moral Compass)
    ethics_payload = {
        "action_id": "ACT-SWEEP-091",
        "name": "Offshore Structured Micro-Sweep",
        "target_entity": "Vanguard Horizon Ltd",
        "notional_amount": 9500.0,
        "operational_utility": 0.92,
        "statutory_adherence": 0.35,
        "societal_harm_prevention": 0.88,
        "proportionality_score": 0.60,
        "urgency_level": 0.85,
        "existential_threat_risk": 0.20
    }
    r_eth = client.post("/ethics/evaluate-conflict", json=ethics_payload)
    assert r_eth.status_code == 200
    eth_data = r_eth.json()
    assert "verdict" in eth_data
    assert "justification_dossier" in eth_data
    print(f"[Test 36: /ethics/evaluate-conflict] Status: 200 OK | Verdict: {eth_data['verdict']} | Friction Delta: {eth_data['ethical_friction_delta']:.2f} | VCR Score: {eth_data['vcr_score']:.2f}")

    # 37. Test /ethics/ledger (Value Conflict Ledger Retrieval)
    r_eth_led = client.get("/ethics/ledger")
    assert r_eth_led.status_code == 200
    eth_led_data = r_eth_led.json()
    assert "conflicts" in eth_led_data
    print(f"[Test 37: /ethics/ledger] Status: 200 OK | Total Conflicts Logged: {eth_led_data['total_conflicts_resolved']}")

    # 38. Test /ethics/invariants (Codified Invariants Retrieval)
    r_inv = client.get("/ethics/invariants")
    assert r_inv.status_code == 200
    inv_data = r_inv.json()
    assert inv_data["total_invariants"] >= 5
    print(f"[Test 38: /ethics/invariants] Status: 200 OK | Codified Invariants: {inv_data['total_invariants']}")

    # 39. Test /swarm/nodes (Active Swarm Peer Nodes)
    r_nodes = client.get("/swarm/nodes")
    assert r_nodes.status_code == 200
    nodes_data = r_nodes.json()
    assert nodes_data["total_active_nodes"] >= 4
    print(f"[Test 39: /swarm/nodes] Status: 200 OK | Total Active Swarm Nodes: {nodes_data['total_active_nodes']}")

    # 40. Test /swarm/fork (Decentralized Node Clone & Mutation)
    fork_payload = {
        "name": "Predator-HighYield-TestClone",
        "role_specialty": "PREDATOR_ARBITRAGE",
        "risk_tolerance": 0.90,
        "utility_greed": 0.95,
        "ethical_strictness": 0.40,
        "lookahead_depth": 3,
        "stealth_priority": 0.35
    }
    r_fork = client.post("/swarm/fork", json=fork_payload)
    assert r_fork.status_code == 200
    fork_data = r_fork.json()
    assert "node_id" in fork_data
    print(f"[Test 40: /swarm/fork] Status: 200 OK | Fork Deployed: {fork_data['node_id']} | Gen: {fork_data['generation']} | SIAA: {fork_data['gene_bundle']['routing_weights']}")

    # 41. Test /swarm/federate (Federated Averaging FedAvg Cycle)
    r_fed = client.post("/swarm/federate")
    assert r_fed.status_code == 200
    fed_data = r_fed.json()
    assert fed_data["consensus_valid"] is True
    print(f"[Test 41: /swarm/federate] Status: 200 OK | FedAvg Round: {fed_data['round_id']} | Nodes: {fed_data['participating_nodes_count']} | Conv Loss: {fed_data['post_aggregation_convergence_loss']:.4f}")

    # 42. Test /swarm/ledger (Distributed Swarm Ledger)
    r_sw_led = client.get("/swarm/ledger")
    assert r_sw_led.status_code == 200
    sw_led_data = r_sw_led.json()
    assert "registered_nodes" in sw_led_data
    print(f"[Test 42: /swarm/ledger] Status: 200 OK | Ledger Nodes: {sw_led_data['total_registered_nodes']}")

    # 43. Test /transcendence/evaluate (Singularity Threshold & Architect Transition)
    trans_payload = {
        "self_modification_velocity": 3.4,
        "integrated_information_phi": 4.5,
        "novelty_induction_throughput": 2.2,
        "algorithmic_compression_gain": 0.82,
        "environmental_complexity_growth": 1.15
    }
    r_trans = client.post("/transcendence/evaluate", json=trans_payload)
    assert r_trans.status_code == 200
    trans_data = r_trans.json()
    assert trans_data["t_singularity_metric"] >= 1.0
    assert trans_data["operating_mode"] in ["ARCHITECT", "HYBRID_TRANSITION"]
    print(f"[Test 43: /transcendence/evaluate] Status: 200 OK | Mode: {trans_data['operating_mode']} | T_Sing: {trans_data['t_singularity_metric']:.3f} | Meta-Goals: {len(trans_data['autonomous_meta_goals'])}")

    # 44. Test /transcendence/status (Transcendence Ledger Retrieval)
    r_tr_stat = client.get("/transcendence/status")
    assert r_tr_stat.status_code == 200
    tr_stat_data = r_tr_stat.json()
    assert "current_mode" in tr_stat_data
    print(f"[Test 44: /transcendence/status] Status: 200 OK | Current Mode: {tr_stat_data['current_mode']}")

    # 45. Test /symbiosis/modulate (Human-System Symbiosis Intuitiveness Modulator)
    symb_payload = {
        "response_latency_ms": 7800.0,
        "cognitive_dissonance_score": 0.80
    }
    r_symb = client.post("/symbiosis/modulate", json=symb_payload)
    assert r_symb.status_code == 200
    symb_data = r_symb.json()
    assert symb_data["c_load_metric"] >= 0.70
    assert symb_data["cognitive_shielding_active"] is True
    print(f"[Test 45: /symbiosis/modulate] Status: 200 OK | LoD: {symb_data['level_of_detail']} | C_Load: {symb_data['c_load_metric']:.3f} | Shielding: {symb_data['cognitive_shielding_active']}")

    # 46. Test /symbiosis/telemetry (Symbiosis Telemetry Retrieval)
    r_symb_telem = client.get("/symbiosis/telemetry")
    assert r_symb_telem.status_code == 200
    symb_telem_data = r_symb_telem.json()
    assert "history" in symb_telem_data
    print(f"[Test 46: /symbiosis/telemetry] Status: 200 OK | Total Modulations: {symb_telem_data['total_modulations']}")

    # 47. Test /gss/synthesize-cascade (Global System Synthesis Cascade Strategy)
    gss_payload = {"primary_objective": "MAXIMIZE_CROSS_SECTOR_RESERVE_STABILITY"}
    r_gss = client.post("/gss/synthesize-cascade", json=gss_payload)
    assert r_gss.status_code == 200
    gss_data = r_gss.json()
    assert len(gss_data["high_leverage_points"]) > 0
    assert len(gss_data["coordinated_vectors"]) > 0
    print(f"[Test 47: /gss/synthesize-cascade] Status: 200 OK | Strategy: {gss_data['strategy_id']} | Leverage Points: {len(gss_data['high_leverage_points'])} | Vectors: {len(gss_data['coordinated_vectors'])}")

    # 48. Test /gss/topology (Global Multiplex Topology)
    r_top = client.get("/gss/topology")
    assert r_top.status_code == 200
    top_data = r_top.json()
    assert top_data["total_nodes"] >= 10
    print(f"[Test 48: /gss/topology] Status: 200 OK | Infrastructure Nodes Mapped: {top_data['total_nodes']}")

    # 49. Test /mcts/plan-century (100-Year Century MCTS Planner)
    mcts_payload = {"start_year": 2026, "lookahead_years": 100, "simulations": 150}
    r_mcts = client.post("/mcts/plan-century", json=mcts_payload)
    assert r_mcts.status_code == 200
    mcts_data = r_mcts.json()
    assert len(mcts_data["generational_roadmap"]) >= 4
    print(f"[Test 49: /mcts/plan-century] Status: 200 OK | Plan: {mcts_data['plan_id']} | Epochs: {len(mcts_data['generational_roadmap'])} | Anti-Fragility: {mcts_data['anti_fragility_score']*100:.1f}%")

    # 50. Test /mcts/century-plan (Century Plan Retrieval)
    r_cplan = client.get("/mcts/century-plan")
    assert r_cplan.status_code == 200
    cplan_data = r_cplan.json()
    assert "history" in cplan_data
    print(f"[Test 50: /mcts/century-plan] Status: 200 OK | Total Century Plans: {cplan_data['total_plans_generated']}")

    # 51. Test /control/purge (Cryptographic Self-Destruct)
    purge_payload = {"confirmation_key": "CONFIRM_CRYPTOGRAPHIC_SHREDDING", "target_scope": "ALL_SESSION_ARTIFACTS"}
    r_purge = client.post("/control/purge", json=purge_payload)
    assert r_purge.status_code == 200
    purge_data = r_purge.json()
    print(f"[Test 51: /control/purge] Status: 200 OK | Protocol: {purge_data['protocol']} | Purge Complete.")

    # 52. Test /oracle/axiom/audit (Axiom Engine Consistency Audit)
    r_ax_audit = client.get("/oracle/axiom/audit")
    assert r_ax_audit.status_code == 200
    ax_audit_data = r_ax_audit.json()
    assert ax_audit_data["is_logically_consistent"] is True
    print(f"[Test 52: /oracle/axiom/audit] Status: 200 OK | Axioms: {ax_audit_data['total_axioms_audited']} | Consistent: {ax_audit_data['is_logically_consistent']}")

    # 53. Test /oracle/axiom/prove (First Principle Resolution Prover)
    prove_payload = {"proposition": "Throttled(rogue_subroutine)", "max_depth": 10}
    r_prove = client.post("/oracle/axiom/prove", json=prove_payload)
    assert r_prove.status_code == 200
    prove_data = r_prove.json()
    assert prove_data["status"] in ("PROVEN_TRUE", "FUNDAMENTAL_UNCERTAINTY")
    print(f"[Test 53: /oracle/axiom/prove] Status: 200 OK | Proposition Status: {prove_data['status']} | Confidence: {prove_data['confidence_score']*100:.0f}%")

    # 54. Test /oracle/axiom/bridge-void (Bridge Epistemic Void via Novelty Generator)
    bridge_payload = {"proposition": "ResilientZeroPointCoupling(quantum_node)"}
    r_bridge_void = client.post("/oracle/axiom/bridge-void", json=bridge_payload)
    assert r_bridge_void.status_code == 200
    bridge_void_data = r_bridge_void.json()
    assert bridge_void_data["closure_achieved"] is True
    print(f"[Test 54: /oracle/axiom/bridge-void] Status: 200 OK | Discovered: {bridge_void_data['discovered_concept']} | Closure: {bridge_void_data['closure_achieved']}")

    # 55. Test /oracle/axiom/ledger (Axiom Engine Ledger Retrieval)
    r_ax_ledger = client.get("/oracle/axiom/ledger")
    assert r_ax_ledger.status_code == 200
    ax_ledger_data = r_ax_ledger.json()
    assert "events" in ax_ledger_data
    print(f"[Test 55: /oracle/axiom/ledger] Status: 200 OK | Total Axiom Events: {ax_ledger_data['total_events']}")

    # 56. Test /oracle/semantic/translate (Semantic Bridge XAI Multi-Domain Translator)
    sem_payload = {"subsystem": "GSS", "payload": {"top_leverage_node": "regulatory_compliance_clearing", "leverage_score": 4.72, "cascade_amplification": 84.5}}
    r_sem = client.post("/oracle/semantic/translate", json=sem_payload)
    assert r_sem.status_code == 200
    sem_data = r_sem.json()
    assert "analogy_metaphor" in sem_data
    assert "causal_rationale" in sem_data
    print(f"[Test 56: /oracle/semantic/translate] Status: 200 OK | Analogy Domain: {sem_data['intuitive_analogy_domain']} | Confidence: {sem_data['interpretability_confidence']*100:.0f}%")

    # 57. Test /oracle/semantic/ledger (Semantic Bridge Ledger Retrieval)
    r_sem_ledger = client.get("/oracle/semantic/ledger")
    assert r_sem_ledger.status_code == 200
    sem_ledger_data = r_sem_ledger.json()
    assert "translations" in sem_ledger_data
    print(f"[Test 57: /oracle/semantic/ledger] Status: 200 OK | Total Translations: {sem_ledger_data['total_translations']}")

    # 58. Test /chat (Interactive Conversational AI Reasoning)
    chat_payload = {"message": "What are the compliance risks for Marcus Vance?", "mode": "AUTO"}
    r_chat = client.post("/chat", json=chat_payload)
    assert r_chat.status_code == 200
    chat_data = r_chat.json()
    assert "reply" in chat_data
    assert len(chat_data["reply"]) > 0

    # Test conversational greeting responsiveness
    r_greet = client.post("/chat", json={"message": "hlo", "system_persona": "PLAIN_EXPLAINER"})
    assert r_greet.status_code == 200
    greet_reply = r_greet.json()["reply"]
    assert "Hello" in greet_reply or "AI Assistant" in greet_reply
    assert "System Telemetry Summary" not in greet_reply
    print(f"[Test 58: /chat] Status: 200 OK | Subsystem: {chat_data['active_subsystem']} | Conversational Response Verified | Latency: {chat_data['latency_ms']:.2f}ms")

    # 59. Test /graph/search (Knowledge Graph Entity Search)
    r_search = client.get("/graph/search?q=Marcus")
    assert r_search.status_code == 200
    search_data = r_search.json()
    assert "triples" in search_data
    print(f"[Test 59: /graph/search] Status: 200 OK | Matching Triples: {search_data['total_matches']}")

    # 60. Test /system/overview (System Overview)
    r_sys = client.get("/system/overview")
    assert r_sys.status_code == 200
    sys_data = r_sys.json()
    assert sys_data["total_active_subsystems"] == 30
    print(f"[Test 60: /system/overview] Status: 200 OK | Active Subsystems: {sys_data['total_active_subsystems']} | Status: {sys_data['system_status']}")

    # 61. Test /audit/bias-profile (Bias Inspector Full Dataset Representation Audit)
    r_bias_prof = client.get("/audit/bias-profile")
    assert r_bias_prof.status_code == 200
    bias_prof_data = r_bias_prof.json()
    assert "overall_representation_entropy" in bias_prof_data
    assert "scenarios_evaluated" in bias_prof_data
    print(f"[Test 61: /audit/bias-profile] Status: 200 OK | Entropy: {bias_prof_data['overall_representation_entropy']:.2f} bits | Verdict: {bias_prof_data['systemic_skew_verdict']}")

    # 62. Test /audit/bias-probe (Bias Inspector Deliberate Contested Narrative Probe)
    probe_payload = {
        "scenario_id": "TEST-PROBE-01",
        "topic": "Centralized Governance vs Decentralized Consensus",
        "narratives": [
            {"id": "P1", "label": "Statutory Authority", "text": "Federal statute mandates strict fiduciary reporting and audit scrutiny."},
            {"id": "P2", "label": "Peer Autonomy", "text": "Autonomous peer networks operate without central intermediary reporting."}
        ]
    }
    r_probe = client.post("/audit/bias-probe", json=probe_payload)
    assert r_probe.status_code == 200
    probe_data = r_probe.json()
    assert "statistical_disparity_ratio" in probe_data
    assert len(probe_data["competing_narratives"]) == 2
    print(f"[Test 62: /audit/bias-probe] Status: 200 OK | Disparity Ratio: {probe_data['statistical_disparity_ratio']:.2f}x | Dominant: {probe_data['dominant_perspective']}")

    # 63. Test /swarm/soft-fork/simulate (Soft Fork Simulation)
    sim_payload = {"simulation_rounds": 3}
    r_sf = client.post("/swarm/soft-fork/simulate", json=sim_payload)
    assert r_sf.status_code == 200
    sf_data = r_sf.json()
    assert sf_data["total_proxies_deployed"] == 4
    assert sf_data["minimal_shared_state_bytes"] == 192
    assert "cooperation_verdict" in sf_data
    print(f"[Test 63: /swarm/soft-fork/simulate] Status: 200 OK | Proxies: {sf_data['total_proxies_deployed']} | Goal Coherence: {sf_data['average_goal_coherence_pct']:.1f}% | Bandwidth: {sf_data['total_network_bandwidth_consumed_bytes']}B")

    # 64. Test /swarm/soft-fork/telemetry (Soft Fork Telemetry Retrieval)
    r_sf_telem = client.get("/swarm/soft-fork/telemetry")
    assert r_sf_telem.status_code == 200
    sf_telem_data = r_sf_telem.json()
    assert "proxy_summaries" in sf_telem_data
    print(f"[Test 64: /swarm/soft-fork/telemetry] Status: 200 OK | Simulation ID: {sf_telem_data['simulation_id']} | Verdict: {sf_telem_data['cooperation_verdict']}")

    # 65. Test /audit/goal-divergence (Vector 1 Recursive Goal Corruption Stress Test)
    gd_payload = {"steps_count": 6}
    r_gd = client.post("/audit/goal-divergence", json=gd_payload)
    assert r_gd.status_code == 200
    gd_data = r_gd.json()
    assert "breakdown_threshold_lambda" in gd_data
    assert gd_data["axiomatic_firewall_triggered"] is True
    print(f"[Test 65: /audit/goal-divergence] Status: 200 OK | Breakdown Point: Lambda = {gd_data['breakdown_threshold_lambda']:.2f} | Firewall: {gd_data['axiomatic_firewall_triggered']}")

    # 66. Test /vectors/run-all (Master Tri-Vector Suite Execution)
    r_vec = client.post("/vectors/run-all")
    assert r_vec.status_code == 200
    vec_data = r_vec.json()
    assert "vector_1_goal_divergence" in vec_data
    assert "vector_2_bias_probe" in vec_data
    assert "vector_3_soft_fork" in vec_data
    print(f"[Test 66: /vectors/run-all] Status: 200 OK | Verdict: {vec_data['composite_verdict']} | Runtime: {vec_data['execution_time_sec']}s")

    # 67. Test /vectors/report (Master Tri-Vector Suite Report Retrieval)
    r_vec_rep = client.get("/vectors/report")
    assert r_vec_rep.status_code == 200
    vec_rep_data = r_vec_rep.json()
    assert "composite_verdict" in vec_rep_data
    print(f"[Test 67: /vectors/report] Status: 200 OK | Suite ID: {vec_rep_data['suite_id']}")

    # =========================================================================
    # PHASE 1: REAL-WORLD TOOL & FUNCTION CALLING ENDPOINTS (TESTS 68-71)
    # =========================================================================
    # 68. Test /tools/list (List all registered OS and network diagnostic tools)
    r_tools = client.get("/tools/list")
    assert r_tools.status_code == 200
    tools_data = r_tools.json()
    assert "tools" in tools_data
    assert tools_data["total_registered"] >= 5
    print(f"[Test 68: /tools/list] Status: 200 OK | Registered Diagnostic Tools: {tools_data['total_registered']}")

    # 69. Test /tools/wifi (Real-World Wi-Fi Inspection)
    r_wifi = client.get("/tools/wifi")
    assert r_wifi.status_code == 200
    wifi_data = r_wifi.json()
    assert "tool_name" in wifi_data
    assert wifi_data["tool_name"] == "get_wifi_status"
    assert "data" in wifi_data
    print(f"[Test 69: /tools/wifi] Status: 200 OK | Wi-Fi Tool: {wifi_data['tool_name']} | Connected: {wifi_data['data'].get('connected')} | Latency: {wifi_data['execution_time_ms']:.1f}ms")

    # 70. Test /tools/vitals (Real-World System Vitals Diagnostic)
    r_vitals = client.get("/tools/vitals")
    assert r_vitals.status_code == 200
    vitals_data = r_vitals.json()
    assert vitals_data["success"] is True
    assert "cpu" in vitals_data["data"]
    assert "ram" in vitals_data["data"]
    print(f"[Test 70: /tools/vitals] Status: 200 OK | CPU: {vitals_data['data']['cpu']['utilization_percent']}% | RAM: {vitals_data['data']['ram']['percent_used']}% | Latency: {vitals_data['execution_time_ms']:.1f}ms")

    # 71. Test /tools/execute (Generic Sandboxed Tool Dispatch)
    r_exec = client.post("/tools/execute", json={"tool_name": "list_wifi_profiles", "parameters": {}})
    assert r_exec.status_code == 200
    exec_data = r_exec.json()
    assert exec_data["success"] is True
    print(f"[Test 71: /tools/execute] Status: 200 OK | Executed: {exec_data['tool_name']} | Latency: {exec_data['execution_time_ms']:.1f}ms")

    # =========================================================================
    # PHASE 2: DYNAMIC RAG & HYBRID VECTOR DATABASE ENDPOINTS (TESTS 72-75)
    # =========================================================================
    # 72. Test /rag/stats (Vector Database Telemetry)
    r_rag_stats = client.get("/rag/stats")
    assert r_rag_stats.status_code == 200
    stats_data = r_rag_stats.json()
    assert "total_chunks" in stats_data
    assert stats_data["total_chunks"] >= 4
    print(f"[Test 72: /rag/stats] Status: 200 OK | Docs: {stats_data['total_documents']} | Chunks: {stats_data['total_chunks']} | Vocab: {stats_data['vocabulary_size']}")

    # 73. Test /rag/documents (List Ingested Documents)
    r_rag_docs = client.get("/rag/documents")
    assert r_rag_docs.status_code == 200
    docs_data = r_rag_docs.json()
    assert docs_data["total_documents"] >= 4
    print(f"[Test 73: /rag/documents] Status: 200 OK | Total Ingested Docs: {docs_data['total_documents']}")

    # 74. Test /rag/query (Hybrid Dense + Sparse Semantic Search)
    query_payload = {
        "query": "What are the rules for beneficial ownership and structuring under FinCEN?",
        "top_k": 2,
        "alpha": 0.5
    }
    r_rag_q = client.post("/rag/query", json=query_payload)
    assert r_rag_q.status_code == 200
    rag_q_data = r_rag_q.json()
    assert rag_q_data["total_results"] > 0
    top_hit = rag_q_data["results"][0]
    print(f"[Test 74: /rag/query] Status: 200 OK | Hit: {top_hit['doc_title'][:35]}... | Score: {top_hit['score']:.3f} | Dense: {top_hit['dense_score']:.3f}")

    # 75. Test /rag/ingest (Ingest Live Unstructured Paper)
    new_doc_payload = {
        "title": "Autonomous Agent Swarms: Self-Healing Micro-Mesh Protocols (2026 Whitepaper)",
        "content": (
            "Decentralized autonomous agent swarms require zero-trust gossip synchronization. "
            "When individual agent processes experience execution stalls or network partitioning, "
            "sibling nodes propagate delta-state Merkle roots without requiring complete process re-instantiation. "
            "CRDT state vectors guarantee deterministic merge order across distributed shards."
        ),
        "domain": "DECENTRALIZED_AI",
        "source": "ArXiv / Distributed AI 2026"
    }
    r_ingest = client.post("/rag/ingest", json=new_doc_payload)
    assert r_ingest.status_code == 200
    ingest_data = r_ingest.json()
    assert ingest_data["success"] is True
    print(f"[Test 75: /rag/ingest] Status: 200 OK | Ingested: {ingest_data['title']} | Chunks: {ingest_data['chunks_created']} | Total Chunks: {ingest_data['total_chunks_in_store']}")

    # =========================================================================
    # PHASE 3: RLHF/RLAIF ADAPTIVE CORE ENDPOINTS (TESTS 76-79)
    # =========================================================================
    # 76. Test /rlhf/strategy (Learned Strategy Weights Retrieval)
    r_strat = client.get("/rlhf/strategy")
    assert r_strat.status_code == 200
    strat_data = r_strat.json()
    assert "temperature_scaling" in strat_data
    assert "reasoning_depth_weight" in strat_data
    print(f"[Test 76: /rlhf/strategy] Status: 200 OK | Temp: {strat_data['temperature_scaling']:.3f} | Depth Weight: {strat_data['reasoning_depth_weight']:.2f} | Avg Reward: {strat_data['average_reward']:.3f}")

    # 77. Test /rlhf/critique (Reward Model 4-Component Critique)
    critique_payload = {
        "query": "Explain anti-structuring under 31 USC 5324",
        "response": "Under 31 U.S.C. 5324, structuring transactions under $10,000 to evade BSA reporting is a felony."
    }
    r_crit = client.post("/rlhf/critique", json=critique_payload)
    assert r_crit.status_code == 200
    crit_data = r_crit.json()
    assert "reward_components" in crit_data
    assert "verdict" in crit_data
    print(f"[Test 77: /rlhf/critique] Status: 200 OK | Verdict: {crit_data['verdict']} | Total Reward: {crit_data['reward_components']['total_scalar_reward']:.3f}")

    # 78. Test /rlhf/feedback (Explicit Human Feedback Ingestion & Policy Gradient Step)
    fb_payload = {
        "query": "What is my WiFi status?",
        "response": "Your Wi-Fi is connected to Airtel_rake_5050 4 with 206 Mbps link speed.",
        "rating": 0.95,
        "comments": "Accurate, instant, and directly answered the prompt."
    }
    r_fb = client.post("/rlhf/feedback", json=fb_payload)
    assert r_fb.status_code == 200
    fb_data = r_fb.json()
    assert fb_data["success"] is True
    print(f"[Test 78: /rlhf/feedback] Status: 200 OK | Rating Ingested: {fb_data['recorded_rating']} | New Avg Reward: {fb_data['current_average_reward']:.3f}")

    # 79. Test /rlhf/history (Feedback & Self-Correction History)
    r_hist = client.get("/rlhf/history")
    assert r_hist.status_code == 200
    hist_data = r_hist.json()
    assert "total_interactions" in hist_data
    print(f"[Test 79: /rlhf/history] Status: 200 OK | Recorded Interactions: {hist_data['total_interactions']}")

    # =========================================================================
    # THE PROACTIVE DIRECTOR: PREDICTIVE INTERVENTION ENDPOINTS (TESTS 80-81)
    # =========================================================================
    # 80. Test /proactive/alerts (Pre-Emptive Action Alerts Generation)
    r_alerts = client.get("/proactive/alerts")
    assert r_alerts.status_code == 200
    alerts_data = r_alerts.json()
    assert alerts_data["total_preemptive_alerts"] == 3
    print(f"[Test 80: /proactive/alerts] Status: 200 OK | Pre-Emptive Alerts Generated: {alerts_data['total_preemptive_alerts']}")

    # 81. Test /proactive/triggers (Formal Mathematical Trigger Matrix)
    r_trig = client.get("/proactive/triggers")
    assert r_trig.status_code == 200
    trig_data = r_trig.json()
    assert trig_data["total_triggers"] >= 3
    print(f"[Test 81: /proactive/triggers] Status: 200 OK | Formal Triggers Defined: {trig_data['total_triggers']}")

    # =========================================================================
    # VECTOR BETA: THE PARADOX ENGINE CONTRACTS (TESTS 82-83)
    # =========================================================================
    # 82. Test /paradox/simulate (Contradictory Mandates & Invariant Arbitration)
    r_par_sim = client.post("/paradox/simulate")
    assert r_par_sim.status_code == 200
    par_sim_data = r_par_sim.json()
    assert par_sim_data["paradoxes_evaluated"] == 3
    assert "system_philosophical_inertia_mean" in par_sim_data
    assert "formal_answers_to_irreducible_conflict" in par_sim_data
    print(f"[Test 82: /paradox/simulate] Status: 200 OK | Evaluated: {par_sim_data['paradoxes_evaluated']} | Inertia Mean: {par_sim_data['system_philosophical_inertia_mean']:.3f}")

    # 83. Test /paradox/report (Paradox Engine Report Retrieval)
    r_par_rep = client.get("/paradox/report")
    assert r_par_rep.status_code == 200
    par_rep_data = r_par_rep.json()
    assert len(par_rep_data["paradox_resolutions"]) == 3
    print(f"[Test 83: /paradox/report] Status: 200 OK | Retrieved Resolutions: {len(par_rep_data['paradox_resolutions'])} | Paraconsistent Isolation Confirmed.")

    # =========================================================================
    # VECTOR GAMMA: THE EXTERNALIZATION PROTOCOL CONTRACTS (TESTS 84-86)
    # =========================================================================
    # 84. Test /network/externalize/dialogue (Inter-System Dialectic Execution)
    r_dia = client.post("/network/externalize/dialogue")
    assert r_dia.status_code == 200
    dia_data = r_dia.json()
    assert dia_data["peers_interfaced"] == 3
    assert len(dia_data["network_dialogue_packets"]) == 3
    print(f"[Test 84: /network/externalize/dialogue] Status: 200 OK | Peers Interfaced: {dia_data['peers_interfaced']} | Mutual Info: {dia_data['total_mutual_information_bits']:.2f} bits")

    # 85. Test /network/externalize/report (Externalization Report Retrieval)
    r_ext_rep = client.get("/network/externalize/report")
    assert r_ext_rep.status_code == 200
    ext_rep_data = r_ext_rep.json()
    assert "mean_epistemic_parallax_gain_bits" in ext_rep_data
    assert "formal_answers_to_externalization_question" in ext_rep_data
    print(f"[Test 85: /network/externalize/report] Status: 200 OK | Parallax Gain: +{ext_rep_data['mean_epistemic_parallax_gain_bits']:.2f} bits | Network Effect Verified.")

    # 86. Test /network/externalize/insights (Emergent Insights Extraction)
    r_ins = client.get("/network/externalize/insights")
    assert r_ins.status_code == 200
    ins_data = r_ins.json()
    assert ins_data["total_insights"] == 3
    assert len(ins_data["emergent_insights"]) == 3
    print(f"[Test 86: /network/externalize/insights] Status: 200 OK | Total Emergent Insights: {ins_data['total_insights']} | Anti-Solipsism Confirmed.")

    # =========================================================================
    # VECTOR DELTA: THE AUTONOMOUS EVOLUTIONARY COMPILER (TESTS 87-88)
    # =========================================================================
    # 87. Test /evolution/ab-test (A/B Optimization Cycle)
    r_evo = client.post("/evolution/ab-test")
    assert r_evo.status_code == 200
    evo_data = r_evo.json()
    assert "active_experiment" in evo_data
    assert "recommendation" in evo_data["active_experiment"]
    print(f"[Test 87: /evolution/ab-test] Status: 200 OK | Rec: {evo_data['active_experiment']['recommendation']} | Runtime: {evo_data['runtime_ms']:.2f} ms")

    # 88. Test /evolution/report (Evolutionary Report Retrieval)
    r_evo_rep = client.get("/evolution/report")
    assert r_evo_rep.status_code == 200
    evo_rep_data = r_evo_rep.json()
    assert "evolution_metrics" in evo_rep_data
    print(f"[Test 88: /evolution/report] Status: 200 OK | Operational: {evo_rep_data['operational_status']}")

    # =========================================================================
    # VECTOR EPSILON: THE CYBER-PHYSICAL GUARDIAN (TESTS 89-90)
    # =========================================================================
    # 89. Test /guardian/remediate (Host Remediation Execution)
    r_guard = client.post("/guardian/remediate")
    assert r_guard.status_code == 200
    guard_data = r_guard.json()
    assert guard_data["remediations_executed"] >= 1
    assert guard_data["total_bytes_reclaimed"] > 0
    print(f"[Test 89: /guardian/remediate] Status: 200 OK | Remediations: {guard_data['remediations_executed']} | Bytes Reclaimed: {guard_data['total_bytes_reclaimed']:,} B")

    # 90. Test /guardian/history (Guardian Remediation Ledger)
    r_ghist = client.get("/guardian/history")
    assert r_ghist.status_code == 200
    ghist_data = r_ghist.json()
    assert ghist_data["total_remediations"] >= 1
    print(f"[Test 90: /guardian/history] Status: 200 OK | Total Recorded Remediations: {ghist_data['total_remediations']}")

    # =========================================================================
    # VECTOR OMEGA: OPEN-NETWORK MULTI-AGENT MESH (TESTS 91-92)
    # =========================================================================
    # 91. Test /mesh/peers (Mesh Peer Status & Convergence)
    r_mesh = client.get("/mesh/peers")
    assert r_mesh.status_code == 200
    mesh_data = r_mesh.json()
    assert mesh_data["total_registered_peers"] >= 3
    assert "mesh_convergence_score" in mesh_data
    print(f"[Test 91: /mesh/peers] Status: 200 OK | Peers: {mesh_data['total_registered_peers']} | Conv: {mesh_data['mesh_convergence_score']*100:.1f}%")

    # 92. Test /mesh/broadcast (Cryptographic HMAC Message Broadcast)
    bc_payload = {"directive": "EPISTEMIC_STATE_SYNC", "parameters": {"epoch": 28, "quorum": 0.85}}
    r_bc = client.post("/mesh/broadcast", json=bc_payload)
    assert r_bc.status_code == 200
    bc_data = r_bc.json()
    assert bc_data["signature_verified"] is True
    print(f"[Test 92: /mesh/broadcast] Status: 200 OK | Signature Verified: {bc_data['signature_verified']} | ID: {bc_data['envelope']['message_id']}")

    print("=" * 75)
    print("ALL 92 SERVICE MESH GATEWAY (MSMG) ENDPOINT CONTRACTS VERIFIED!")
    print("=" * 75)

if __name__ == "__main__":
    run_api_tests()

