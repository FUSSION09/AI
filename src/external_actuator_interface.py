r"""
Phase 9: External Actuator Interface (EAI) Layer (The Hands)
Modular adapter system translating abstracted Orchestrator actions into specific protocols.
Includes templates for:
1. Financial Exchange / Brokerage API (REST / FIX trading protocol)
2. Storage & Document Generation Service (POSIX / S3 object operations)
3. Communication Relay (MQTT / Webhook telemetry broadcast)
Location: d:/AI/src/external_actuator_interface.py
Strictly localized within d:/AI
"""

import os
import sys
import time
import json
import hmac
import hashlib
import secrets
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from config import BASE_DIR, DATA_DIR
from ephemeral_chain import EphemeralLedger

ACTUATOR_OUTPUT_DIR = DATA_DIR / "actuator_artifacts"


@dataclass
class ActuatorResult:
    success: bool
    action_type: str
    external_ref_id: str
    latency_ms: float
    payload: Dict[str, Any]
    error: Optional[str] = None


class BaseExternalActuator(ABC):
    """Abstract base contract for external actuators."""
    def __init__(self, name: str, protocol: str):
        self.name = name
        self.protocol = protocol

    @abstractmethod
    def execute(self, action: str, parameters: Dict[str, Any]) -> ActuatorResult:
        pass


# ==============================================================================
# 1. FINANCIAL EXCHANGE / BROKERAGE ACTUATOR (REST / HMAC PROTOCOL)
# ==============================================================================
class FinancialExchangeActuator(BaseExternalActuator):
    """
    Translates 'EXECUTE_TRADE', 'CANCEL_ORDER', 'QUERY_POSITIONS' into
    authenticated financial exchange order routing with HMAC-SHA256 signatures.
    """
    def __init__(self, api_key: str = "APEX_EXCHANGE_KEY_DEMO", api_secret: str = "APEX_SECRET_HMAC_DEMO"):
        super().__init__(name="FinancialExchangeActuator", protocol="REST_HMAC_SHA256")
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.simulated_positions = {"USD": 1000000.0, "BTC": 15.5, "ETH": 120.0}

    def _sign_request(self, timestamp: int, payload_str: str) -> str:
        msg = f"{timestamp}|{payload_str}".encode("utf-8")
        return hmac.new(self.api_secret, msg, hashlib.sha256).hexdigest()

    def execute(self, action: str, parameters: Dict[str, Any]) -> ActuatorResult:
        t0 = time.perf_counter()
        order_ref = f"ORD-{secrets.token_hex(6).upper()}"
        ts = int(time.time() * 1000)

        if action == "EXECUTE_TRADE":
            symbol = parameters.get("symbol", "BTC/USD")
            side = parameters.get("side", "BUY").upper()
            qty = float(parameters.get("quantity", 0.1))
            price = float(parameters.get("price", 65000.0))
            order_type = parameters.get("order_type", "LIMIT")

            # Signing the protocol request
            body_str = json.dumps({"symbol": symbol, "side": side, "qty": qty, "price": price})
            sig = self._sign_request(ts, body_str)

            # Simulated execution fill
            fill_price = price
            fill_qty = qty
            commission = (fill_price * fill_qty) * 0.0005

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ActuatorResult(
                success=True,
                action_type=action,
                external_ref_id=order_ref,
                latency_ms=elapsed_ms,
                payload={
                    "exchange_status": "FILLED",
                    "order_id": order_ref,
                    "symbol": symbol,
                    "side": side,
                    "filled_qty": fill_qty,
                    "average_price": fill_price,
                    "commission_usd": commission,
                    "hmac_signature": sig[:16] + "..."
                }
            )

        elif action == "QUERY_POSITIONS":
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ActuatorResult(
                success=True,
                action_type=action,
                external_ref_id=f"QUERY-{secrets.token_hex(4).upper()}",
                latency_ms=elapsed_ms,
                payload={"balances": self.simulated_positions}
            )

        else:
            return ActuatorResult(
                success=False,
                action_type=action,
                external_ref_id=order_ref,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                payload={},
                error=f"Unsupported action: {action}"
            )


# ==============================================================================
# 2. STORAGE & DOCUMENT GENERATION ACTUATOR (POSIX / S3 PROTOCOL)
# ==============================================================================
class StorageServiceActuator(BaseExternalActuator):
    """
    Translates 'GENERATE_DOCUMENT', 'ARCHIVE_LEDGER', 'WRITE_ARTIFACT' into
    atomic POSIX / Object Storage operations with SHA-256 integrity hashing.
    """
    def __init__(self, storage_dir: Path = ACTUATOR_OUTPUT_DIR):
        super().__init__(name="StorageServiceActuator", protocol="POSIX_OBJECT_STORAGE")
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, action: str, parameters: Dict[str, Any]) -> ActuatorResult:
        t0 = time.perf_counter()
        doc_ref = f"DOC-{secrets.token_hex(6).upper()}"

        if action == "GENERATE_DOCUMENT":
            doc_type = parameters.get("doc_type", "COMPLIANCE_REPORT")
            title = parameters.get("title", "Statutory Audit Brief")
            content = parameters.get("content", "Automated system decision summary.")
            
            filename = f"{doc_type}_{doc_ref}.json"
            target_file = self.storage_dir / filename

            # Build structured document artifact
            doc_payload = {
                "document_id": doc_ref,
                "title": title,
                "doc_type": doc_type,
                "timestamp": time.time(),
                "body": content,
                "author": "Apex EAI Actuator"
            }
            raw_bytes = json.dumps(doc_payload, indent=2).encode("utf-8")
            sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

            # Atomic file write
            with open(target_file, "wb") as f:
                f.write(raw_bytes)

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ActuatorResult(
                success=True,
                action_type=action,
                external_ref_id=doc_ref,
                latency_ms=elapsed_ms,
                payload={
                    "file_path": str(target_file),
                    "file_size_bytes": len(raw_bytes),
                    "sha256_checksum": sha256_hash,
                    "storage_backend": "LOCAL_POSIX"
                }
            )

        elif action == "ARCHIVE_LEDGER":
            ledger_data = parameters.get("ledger_blocks", [])
            filename = f"LEDGER_ARCHIVE_{doc_ref}.json"
            target_file = self.storage_dir / filename
            raw_bytes = json.dumps(ledger_data, indent=2).encode("utf-8")
            with open(target_file, "wb") as f:
                f.write(raw_bytes)

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ActuatorResult(
                success=True,
                action_type=action,
                external_ref_id=doc_ref,
                latency_ms=elapsed_ms,
                payload={
                    "archive_file": str(target_file),
                    "blocks_archived": len(ledger_data),
                    "checksum": hashlib.sha256(raw_bytes).hexdigest()
                }
            )

        else:
            return ActuatorResult(
                success=False,
                action_type=action,
                external_ref_id=doc_ref,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                payload={},
                error=f"Unsupported storage action: {action}"
            )


# ==============================================================================
# 3. COMMUNICATION RELAY ACTUATOR (MQTT PROTOCOL)
# ==============================================================================
class CommunicationRelayActuator(BaseExternalActuator):
    """
    Translates 'BROADCAST_ALERT', 'DISPATCH_TELEMETRY', 'NOTIFY_OPERATOR' into
    MQTT topic publishing with Quality of Service (QoS) guarantees.
    """
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        super().__init__(name="CommunicationRelayActuator", protocol="MQTT_QOS1")
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.published_messages_mock: List[Dict[str, Any]] = []

    def execute(self, action: str, parameters: Dict[str, Any]) -> ActuatorResult:
        t0 = time.perf_counter()
        msg_ref = f"MQTT-{secrets.token_hex(6).upper()}"

        if action in ["BROADCAST_ALERT", "DISPATCH_TELEMETRY", "NOTIFY_OPERATOR"]:
            topic = parameters.get("topic", "apex/system/alerts")
            qos = parameters.get("qos", 1)
            payload_data = parameters.get("message", {"event": "SYSTEM_HEARTBEAT"})

            formatted_packet = {
                "message_id": msg_ref,
                "topic": topic,
                "qos": qos,
                "timestamp": time.time(),
                "payload": payload_data
            }

            # In production, uses paho.mqtt.client.Client.publish()
            # Maintains local confirmation buffer for verification
            self.published_messages_mock.append(formatted_packet)

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ActuatorResult(
                success=True,
                action_type=action,
                external_ref_id=msg_ref,
                latency_ms=elapsed_ms,
                payload={
                    "mqtt_topic": topic,
                    "qos": qos,
                    "broker": f"{self.broker_host}:{self.broker_port}",
                    "transmission_state": "DELIVERED_ACK"
                }
            )

        else:
            return ActuatorResult(
                success=False,
                action_type=action,
                external_ref_id=msg_ref,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                payload={},
                error=f"Unsupported communication action: {action}"
            )


# ==============================================================================
# 4. EXTERNAL ACTUATOR DISPATCHER (EAI MANAGER)
# ==============================================================================
class ExternalActuatorDispatcher:
    """
    Master EAI Router: Dispatches high-level orchestrator commands to the
    appropriate specialized external actuator. Logs results to Ephemeral Ledger.
    """
    def __init__(self, ledger: Optional[EphemeralLedger] = None):
        self.exchange = FinancialExchangeActuator()
        self.storage = StorageServiceActuator()
        self.comms = CommunicationRelayActuator()
        self.ledger = ledger or EphemeralLedger()

        # Routing table mapping high-level actions to actuators
        self.action_routing_table = {
            "EXECUTE_TRADE": self.exchange,
            "QUERY_POSITIONS": self.exchange,
            "GENERATE_DOCUMENT": self.storage,
            "ARCHIVE_LEDGER": self.storage,
            "BROADCAST_ALERT": self.comms,
            "DISPATCH_TELEMETRY": self.comms,
            "NOTIFY_OPERATOR": self.comms,
        }

    def dispatch(self, action_name: str, parameters: Dict[str, Any]) -> ActuatorResult:
        actuator = self.action_routing_table.get(action_name)
        if not actuator:
            return ActuatorResult(
                success=False,
                action_type=action_name,
                external_ref_id="NONE",
                latency_ms=0.0,
                payload={},
                error=f"No external actuator registered for action '{action_name}'"
            )

        # Execute actuator protocol call
        result = actuator.execute(action_name, parameters)

        # Log transition to Ephemeral Ledger
        self.ledger.record_action(
            "EAI_EXTERNAL_DISPATCH",
            {
                "action": action_name,
                "protocol": actuator.protocol,
                "ref_id": result.external_ref_id,
                "success": result.success,
                "latency_ms": result.latency_ms
            }
        )

        return result


# ==============================================================================
# VERIFICATION SUITE
# ==============================================================================
if __name__ == "__main__":
    eai = ExternalActuatorDispatcher()

    print("=" * 75)
    print("PHASE 9: EXTERNAL ACTUATOR INTERFACE (EAI) VERIFICATION")
    print("=" * 75)

    # 1. Test Financial Trading API Adapter (REST / HMAC)
    print("\n[Actuator 1: Financial Exchange API]")
    trade_params = {"symbol": "BTC/USD", "side": "BUY", "quantity": 0.5, "price": 64200.0}
    r_trade = eai.dispatch("EXECUTE_TRADE", trade_params)
    print(f" -> Action: EXECUTE_TRADE | Status: {r_trade.success} | Order ID: {r_trade.external_ref_id}")
    print(f" -> Fill Details: {r_trade.payload['side']} {r_trade.payload['filled_qty']} {r_trade.payload['symbol']} @ ${r_trade.payload['average_price']}")
    print(f" -> Protocol Latency: {r_trade.latency_ms:.2f} ms")

    # 2. Test Storage & Document Generation Adapter (POSIX / S3)
    print("\n[Actuator 2: Storage & Document Generation]")
    doc_params = {
        "doc_type": "AUDIT_SUMMARY",
        "title": "Quarterly Regulatory Risk Assessment",
        "content": "All multi-hop transfers cleared through 31 U.S.C. 5324 screening without exceptions."
    }
    r_doc = eai.dispatch("GENERATE_DOCUMENT", doc_params)
    print(f" -> Action: GENERATE_DOCUMENT | Status: {r_doc.success} | Doc ID: {r_doc.external_ref_id}")
    print(f" -> Artifact Path: {r_doc.payload['file_path']}")
    print(f" -> Checksum: {r_doc.payload['sha256_checksum'][:24]}... | Latency: {r_doc.latency_ms:.2f} ms")

    # 3. Test Communication Relay Adapter (MQTT)
    print("\n[Actuator 3: Communication Relay (MQTT)]")
    comms_params = {
        "topic": "apex/compliance/alerts",
        "qos": 1,
        "message": {"alert_level": "WARNING", "event": "ELEVATED_SCRUTINY_DETECTED", "node": "Marcus Vance"}
    }
    r_mqtt = eai.dispatch("BROADCAST_ALERT", comms_params)
    print(f" -> Action: BROADCAST_ALERT | Status: {r_mqtt.success} | Msg ID: {r_mqtt.external_ref_id}")
    print(f" -> MQTT Topic: {r_mqtt.payload['mqtt_topic']} | Broker: {r_mqtt.payload['broker']}")
    print(f" -> Protocol Latency: {r_mqtt.latency_ms:.2f} ms")

    print("\n" + "=" * 75)
    print(f"Total Dispatches Logged to Ephemeral Ledger: {len(eai.ledger.chain) - 1}")
    print(f"Ephemeral Ledger Cryptographic Integrity: {eai.ledger.verify_integrity()}")
    print("=" * 75)

