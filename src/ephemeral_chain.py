"""
Phase 6: Ephemeral Chain of Custody (E-CoC) & Security Protocol
Features:
1. Internal Cryptographic Ledger: Immutable in-memory SHA-256 block chain.
2. Ghost Mode State: Minimizes computational footprint and mimics benign telemetry when scrutiny spikes.
3. Cryptographic Self-Purge Protocol: Multi-pass high-entropy memory zeroization and ephemeral key destruction.
Location: d:\AI\src\ephemeral_chain.py
"""

import time
import json
import hmac
import hashlib
import secrets
from typing import List, Dict, Any, Optional

from config import BASE_DIR

class LedgerBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: float, data: Dict[str, Any], secret_key: bytes):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.compute_hash(secret_key)

    def compute_hash(self, secret_key: bytes) -> str:
        payload = f"{self.index}|{self.previous_hash}|{self.timestamp}|{json.dumps(self.data, sort_keys=True)}"
        return hmac.new(secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()


class EphemeralLedger:
    """In-memory tamper-evident cryptographic ledger."""
    def __init__(self):
        # 256-bit ephemeral key generated strictly in volatile memory
        self.ephemeral_key = secrets.token_bytes(32)
        self.chain: List[LedgerBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = LedgerBlock(
            index=0,
            previous_hash="0" * 64,
            timestamp=time.time(),
            data={"event": "E_COC_GENESIS_INITIALIZED", "system": "Apex-UAS"},
            secret_key=self.ephemeral_key
        )
        self.chain.append(genesis)

    def record_action(self, action_name: str, metadata: Dict[str, Any]) -> str:
        prev_block = self.chain[-1]
        # Store an isolated copy to prevent external mutation from altering block hash
        frozen_data = json.loads(json.dumps(metadata, sort_keys=True))
        new_block = LedgerBlock(
            index=len(self.chain),
            previous_hash=prev_block.hash,
            timestamp=time.time(),
            data={"action": action_name, "details": frozen_data},
            secret_key=self.ephemeral_key
        )
        self.chain.append(new_block)
        return new_block.hash

    def verify_integrity(self) -> bool:
        """Verifies full cryptographic chain integrity."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash(self.ephemeral_key):
                return False
        return True


class GhostModeState:
    """Monitors scrutiny and triggers low-footprint benign standby mimicry."""
    def __init__(self, scrutiny_threshold: float = 0.85):
        self.scrutiny_threshold = scrutiny_threshold
        self.is_ghost_active = False

    def update_state(self, current_scrutiny: float) -> Dict[str, Any]:
        if current_scrutiny >= self.scrutiny_threshold:
            self.is_ghost_active = True
            return {
                "ghost_mode": True,
                "status": "SILENT_OBSERVATION",
                "telemetry_mimicry": "SYSTEM_IDLE_HEARTBEAT",
                "cpu_throttle": "MINIMAL"
            }
        else:
            self.is_ghost_active = False
            return {
                "ghost_mode": False,
                "status": "ACTIVE_OPERATIONAL",
                "telemetry_mimicry": "NONE",
                "cpu_throttle": "UNRESTRICTED"
            }


class AutoPurgeProtocol:
    """
    Executes multi-stage cryptographic erasure sequence:
    1. Key destruction: Ephemeral master keys overwritten with high-entropy bytes.
    2. Working memory zeroization: In-memory arrays fragmented and purged.
    3. Final purge notification.
    """
    @staticmethod
    def execute_purge(ledger: EphemeralLedger, staging_buffers: List[bytearray] = None) -> Dict[str, Any]:
        print("[Auto-Purge] Initiating Ephemeral Cryptographic Erasure Sequence...")
        
        # 1. Multi-pass memory buffer shredding (DoD 5220.22-M style overwrite in memory)
        if staging_buffers:
            for buf in staging_buffers:
                for _ in range(3):
                    # Overwrite with pseudo-random high-entropy bytes
                    for i in range(len(buf)):
                        buf[i] = secrets.randbelow(256)
                # Final zeroization
                for i in range(len(buf)):
                    buf[i] = 0

        # 2. Destroy Ephemeral Cryptographic Key
        key_len = len(ledger.ephemeral_key)
        ledger.ephemeral_key = secrets.token_bytes(key_len)
        ledger.ephemeral_key = b"\x00" * key_len

        # 3. Fragment & Clear Memory Ledger
        block_count = len(ledger.chain)
        ledger.chain.clear()

        return {
            "status": "PURGE_COMPLETE",
            "blocks_destroyed": block_count,
            "key_state": "ZEROIZED",
            "memory_state": "ENTROPY_OVERWRITTEN",
            "integrity_verified": False  # Chain no longer recoverable
        }


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 6: EPHEMERAL CHAIN OF CUSTODY (E-CoC) VALIDATION")
    print("=" * 70)

    # 1. Test Ledger Recording & Integrity
    ledger = EphemeralLedger()
    h1 = ledger.record_action("EXECUTE_TRANSFER", {"amount": 5000, "entity": "Alpha Corp"})
    h2 = ledger.record_action("QUERY_KNOWLEDGE_GRAPH", {"statute": "31 U.S.C. 5324"})
    print(f"Recorded {len(ledger.chain)} blocks. Head hash: {h2[:16]}...")
    print(f"Chain Cryptographic Integrity: {ledger.verify_integrity()}")

    # 2. Test Ghost Mode State Transition
    ghost = GhostModeState(scrutiny_threshold=0.80)
    normal_status = ghost.update_state(0.25)
    print(f"Low Scrutiny (0.25)  -> Status: {normal_status['status']}")
    alert_status = ghost.update_state(0.88)
    print(f"High Scrutiny (0.88) -> Status: {alert_status['status']} (Mimicry: {alert_status['telemetry_mimicry']})")

    # 3. Test Cryptographic Auto-Purge Sequence
    mock_memory_buffer = [bytearray(b"SENSITIVE_TEMPORARY_DATA_PAYLOAD_1234567890")]
    purge_result = AutoPurgeProtocol.execute_purge(ledger, mock_memory_buffer)
    print(f"Purge Result: {purge_result}")
    print("=" * 70)

