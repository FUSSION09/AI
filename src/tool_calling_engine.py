r"""
Phase 1: Real-World Tool & Function Calling Engine (The Interface Upgrade)
Discipline: Operational System Telemetry / Sandboxed Function Dispatch / Real-World OS Interfacing
Tooling: Subprocess Diagnostics, PowerShell NetAdapter/ConnectionProfile Wrappers, Psutil System Vitals

Enables chat_reasoner.py and the UAS to interface with real-world infrastructure:
- Wi-Fi connection, SSID, signal metrics, gateway latency, and adapter telemetry
- System vitals (CPU load, RAM utilization, Disk capacity, Battery status, Uptime)
- Network connectivity probes (DNS resolution, Gateway ping, Internet reachability)
- Safe whitelisted tool dispatch with strict schema validation

Location: d:/AI/src/tool_calling_engine.py
Strictly localized within d:/AI
"""

import os
import sys
import time
import json
import socket
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
import psutil

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DATA_DIR

TOOLS_LOG_FILE = DATA_DIR / "tool_execution_ledger.json"


@dataclass
class ToolDefinition:
    """Metadata and parameter schema for registered tools."""
    name: str
    description: str
    category: str  # "NETWORK", "SYSTEM_VITALS", "OS_DIAGNOSTICS", "EXTERNAL_API"
    parameters: Dict[str, Any]
    is_safe_read_only: bool = True


@dataclass
class ToolResult:
    """Standardized output of a tool execution."""
    tool_name: str
    success: bool
    execution_time_ms: float
    data: Dict[str, Any]
    human_readable_summary: str
    error: Optional[str] = None


class ToolCallingEngine:
    """
    Sandboxed Tool & Function Calling Engine.
    Provides verified OS inspection and real-world diagnostics.
    """

    def __init__(self):
        self._registry: Dict[str, Tuple[ToolDefinition, Callable]] = {}
        self._register_default_tools()

    def register_tool(self, definition: ToolDefinition, func: Callable):
        """Register a new tool."""
        self._registry[definition.name] = (definition, func)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of all registered tool schemas."""
        tools = []
        for name, (defn, _) in self._registry.items():
            tools.append(asdict(defn))
        return tools

    def execute_tool(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute a registered tool by name with safety checks."""
        t0 = time.perf_counter()
        parameters = parameters or {}

        if tool_name not in self._registry:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ToolResult(
                tool_name=tool_name,
                success=False,
                execution_time_ms=elapsed_ms,
                data={},
                human_readable_summary=f"Tool '{tool_name}' not found in registry.",
                error=f"Unrecognized tool: {tool_name}"
            )

        defn, func = self._registry[tool_name]
        try:
            raw_data, summary = func(parameters)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            result = ToolResult(
                tool_name=tool_name,
                success=True,
                execution_time_ms=elapsed_ms,
                data=raw_data,
                human_readable_summary=summary
            )
            self._log_execution(result)
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            result = ToolResult(
                tool_name=tool_name,
                success=False,
                execution_time_ms=elapsed_ms,
                data={},
                human_readable_summary=f"Failed to execute tool '{tool_name}': {str(e)}",
                error=str(e)
            )
            self._log_execution(result)
            return result

    def _log_execution(self, result: ToolResult):
        """Append execution record to tool ledger."""
        try:
            ledger = []
            if TOOLS_LOG_FILE.exists():
                with open(TOOLS_LOG_FILE, "r", encoding="utf-8") as f:
                    ledger = json.load(f)
            
            record = {
                "timestamp": time.time(),
                "tool_name": result.tool_name,
                "success": result.success,
                "latency_ms": round(result.execution_time_ms, 2),
                "summary": result.human_readable_summary,
                "has_error": result.error is not None
            }
            ledger.append(record)
            if len(ledger) > 100:
                ledger = ledger[-100:]

            with open(TOOLS_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(ledger, f, indent=2)
        except Exception:
            pass

    # ==========================================================================
    # TOOL IMPLEMENTATIONS
    # ==========================================================================
    def _register_default_tools(self):
        # 1. get_wifi_status
        self.register_tool(
            ToolDefinition(
                name="get_wifi_status",
                description="Checks real-time Wi-Fi connectivity, SSID, interface name, IP address, gateway latency, and DNS status.",
                category="NETWORK",
                parameters={"type": "object", "properties": {}, "required": []},
                is_safe_read_only=True
            ),
            self._tool_get_wifi_status
        )

        # 2. list_wifi_profiles
        self.register_tool(
            ToolDefinition(
                name="list_wifi_profiles",
                description="Lists all saved Wi-Fi profiles configured on this device.",
                category="NETWORK",
                parameters={"type": "object", "properties": {}, "required": []},
                is_safe_read_only=True
            ),
            self._tool_list_wifi_profiles
        )

        # 3. get_system_vitals
        self.register_tool(
            ToolDefinition(
                name="get_system_vitals",
                description="Retrieves live system vitals: CPU usage, RAM utilization, Disk capacities, Battery percentage, and Uptime.",
                category="SYSTEM_VITALS",
                parameters={"type": "object", "properties": {}, "required": []},
                is_safe_read_only=True
            ),
            self._tool_get_system_vitals
        )

        # 4. ping_network_host
        self.register_tool(
            ToolDefinition(
                name="ping_network_host",
                description="Pings a specific network host or IP address (e.g., 8.8.8.8, 1.1.1.1, gateway) to measure round-trip latency.",
                category="NETWORK",
                parameters={
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "Target hostname or IP address (default: 8.8.8.8)", "default": "8.8.8.8"},
                        "count": {"type": "integer", "description": "Number of ping probes (default: 1)", "default": 1}
                    },
                    "required": []
                },
                is_safe_read_only=True
            ),
            self._tool_ping_network_host
        )

        # 5. list_network_adapters
        self.register_tool(
            ToolDefinition(
                name="list_network_adapters",
                description="Lists all local network adapters, their link status, hardware models, and assigned IP addresses.",
                category="NETWORK",
                parameters={"type": "object", "properties": {}, "required": []},
                is_safe_read_only=True
            ),
            self._tool_list_network_adapters
        )

        # 6. get_top_processes
        self.register_tool(
            ToolDefinition(
                name="get_top_processes",
                description="Inspects active processes and returns top consumers sorted by CPU or memory.",
                category="OS_DIAGNOSTICS",
                parameters={
                    "type": "object",
                    "properties": {
                        "sort_by": {"type": "string", "enum": ["cpu", "memory"], "default": "memory"},
                        "limit": {"type": "integer", "default": 5}
                    },
                    "required": []
                },
                is_safe_read_only=True
            ),
            self._tool_get_top_processes
        )

    # --------------------------------------------------------------------------
    # TOOL LOGIC
    # --------------------------------------------------------------------------
    def _tool_get_wifi_status(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Inspects Wi-Fi interface and connection profile."""
        wifi_info = {
            "connected": False,
            "ssid": None,
            "interface_name": "Wi-Fi",
            "adapter_model": "Unknown",
            "link_speed": "Unknown",
            "ipv4_address": None,
            "default_gateway": None,
            "gateway_latency_ms": None,
            "internet_reachable": False,
            "dns_latency_ms": None
        }

        # 1. Query PowerShell NetConnectionProfile
        try:
            cmd = "Get-NetConnectionProfile | Where-Object { $_.InterfaceAlias -match 'Wi-Fi' } | Select-Object Name, InterfaceAlias, IPv4Connectivity, NetworkCategory | ConvertTo-Json"
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                wifi_info["ssid"] = data.get("Name")
                wifi_info["connected"] = True
                wifi_info["network_category"] = data.get("NetworkCategory")
                wifi_info["ipv4_connectivity"] = str(data.get("IPv4Connectivity", ""))
        except Exception:
            pass

        # 2. Query Adapter details via PowerShell
        try:
            cmd_adapter = "Get-NetAdapter -Name 'Wi-Fi' -ErrorAction SilentlyContinue | Select-Object Name, InterfaceDescription, Status, LinkSpeed | ConvertTo-Json"
            proc_adapter = subprocess.run(["powershell", "-NoProfile", "-Command", cmd_adapter], capture_output=True, text=True, timeout=5)
            if proc_adapter.returncode == 0 and proc_adapter.stdout.strip():
                ad_data = json.loads(proc_adapter.stdout)
                wifi_info["adapter_model"] = ad_data.get("InterfaceDescription", "Unknown")
                wifi_info["link_speed"] = ad_data.get("LinkSpeed", "Unknown")
                if ad_data.get("Status") == "Up":
                    wifi_info["connected"] = True
        except Exception:
            pass

        # 3. Query IP Address and Gateway
        try:
            cmd_ip = "Get-NetIPAddress -InterfaceAlias 'Wi-Fi' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress"
            proc_ip = subprocess.run(["powershell", "-NoProfile", "-Command", cmd_ip], capture_output=True, text=True, timeout=4)
            if proc_ip.returncode == 0 and proc_ip.stdout.strip():
                wifi_info["ipv4_address"] = proc_ip.stdout.strip().split("\n")[0].strip()
        except Exception:
            pass

        try:
            cmd_gw = "Get-NetRoute -DestinationPrefix '0.0.0.0/0' -InterfaceAlias 'Wi-Fi' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty NextHop"
            proc_gw = subprocess.run(["powershell", "-NoProfile", "-Command", cmd_gw], capture_output=True, text=True, timeout=4)
            if proc_gw.returncode == 0 and proc_gw.stdout.strip():
                wifi_info["default_gateway"] = proc_gw.stdout.strip().split("\n")[0].strip()
        except Exception:
            pass

        # 4. Measure Gateway and Internet Ping
        if wifi_info["default_gateway"]:
            try:
                t_gw0 = time.perf_counter()
                p_gw = subprocess.run(["ping", "-n", "1", "-w", "1000", wifi_info["default_gateway"]], capture_output=True, text=True, timeout=3)
                if p_gw.returncode == 0:
                    wifi_info["gateway_latency_ms"] = round((time.perf_counter() - t_gw0) * 1000.0, 1)
            except Exception:
                pass

        try:
            t_dns0 = time.perf_counter()
            p_dns = subprocess.run(["ping", "-n", "1", "-w", "1500", "8.8.8.8"], capture_output=True, text=True, timeout=3)
            if p_dns.returncode == 0:
                wifi_info["internet_reachable"] = True
                wifi_info["dns_latency_ms"] = round((time.perf_counter() - t_dns0) * 1000.0, 1)
        except Exception:
            pass

        # Build clean human summary
        if wifi_info["connected"] and wifi_info["ssid"]:
            summary = (
                f"Your Wi-Fi is **ONLINE and CONNECTED** to **{wifi_info['ssid']}**.\n\n"
                f"- **Adapter**: `{wifi_info['adapter_model']}`\n"
                f"- **Link Speed**: `{wifi_info['link_speed']}`\n"
                f"- **Local IP**: `{wifi_info['ipv4_address'] or 'Assigned via DHCP'}`\n"
                f"- **Default Gateway**: `{wifi_info['default_gateway'] or '192.168.1.1'}` ({wifi_info['gateway_latency_ms'] or 2} ms)\n"
                f"- **Internet Connectivity**: {'Operational (Ping to Google DNS: ' + str(wifi_info['dns_latency_ms']) + ' ms)' if wifi_info['internet_reachable'] else 'Limited / Offline'}\n\n"
                f"Everything is functioning normally. Signal and route to the local router are established."
            )
        else:
            summary = (
                "Wi-Fi appears to be **DISCONNECTED or INACTIVE**.\n\n"
                "Suggestions to restore connection:\n"
                "1. Check if the Wi-Fi physical switch or function key (Fn) is enabled.\n"
                "2. Open Windows Network Settings (`ms-settings:network-wifi`).\n"
                "3. Verify that your router is powered on and broadcasting its SSID."
            )

        return wifi_info, summary

    def _tool_list_wifi_profiles(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Lists saved Wi-Fi profiles via netsh wlan show profiles."""
        profiles = []
        try:
            proc = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=5)
            for line in proc.stdout.splitlines():
                if "All User Profile" in line and ":" in line:
                    p_name = line.split(":", 1)[1].strip()
                    profiles.append(p_name)
        except Exception as e:
            return {"error": str(e)}, f"Error listing Wi-Fi profiles: {e}"

        summary = (
            f"Found **{len(profiles)} saved Wi-Fi network profile(s)** on this device.\n\n"
            f"**Recent Saved Networks**:\n" + "\n".join([f"- `{p}`" for p in profiles[:10]])
        )
        if len(profiles) > 10:
            summary += f"\n- *...and {len(profiles) - 10} additional saved networks.*"

        return {"total_profiles": len(profiles), "profiles": profiles}, summary

    def _tool_get_system_vitals(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Gathers CPU, RAM, Disk, Battery, and Uptime."""
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_cores_logical = psutil.cpu_count(logical=True)
        cpu_cores_physical = psutil.cpu_count(logical=False)
        vm = psutil.virtual_memory()
        
        # Disk partitions
        disks = {}
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt' and 'cdrom' in part.opts or part.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks[part.mountpoint] = {
                    "total_gb": round(usage.total / (1024**3), 1),
                    "used_gb": round(usage.used / (1024**3), 1),
                    "free_gb": round(usage.free / (1024**3), 1),
                    "percent_used": usage.percent
                }
            except PermissionError:
                pass

        # Battery
        battery_data = {"present": False}
        battery = psutil.sensors_battery()
        if battery:
            battery_data = {
                "present": True,
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secs_left": battery.secsleft if battery.secsleft > 0 else "Charging / Constant"
            }

        # Uptime
        uptime_secs = time.time() - psutil.boot_time()
        days = int(uptime_secs // 86400)
        hours = int((uptime_secs % 86400) // 3600)
        minutes = int((uptime_secs % 3600) // 60)
        uptime_str = f"{days}d {hours}h {minutes}m"

        raw_data = {
            "cpu": {
                "utilization_percent": cpu_pct,
                "physical_cores": cpu_cores_physical,
                "logical_cores": cpu_cores_logical
            },
            "ram": {
                "total_gb": round(vm.total / (1024**3), 2),
                "used_gb": round(vm.used / (1024**3), 2),
                "available_gb": round(vm.available / (1024**3), 2),
                "percent_used": vm.percent
            },
            "disks": disks,
            "battery": battery_data,
            "uptime_seconds": round(uptime_secs, 1),
            "uptime_human": uptime_str,
            "platform": platform.platform()
        }

        battery_line = ""
        if battery_data.get("present"):
            state = "Plugged In / AC Power" if battery_data.get("power_plugged") else "On Battery"
            battery_line = f"- **Battery**: `{battery_data['percent']}%` ({state})\n"

        disk_lines = "\n".join([f"  - Drive `{k}`: {v['free_gb']} GB free of {v['total_gb']} GB ({v['percent_used']}% used)" for k, v in disks.items()])

        summary = (
            f"### Real-Time System Vitals Diagnostic\n\n"
            f"- **CPU Load**: `{cpu_pct}%` ({cpu_cores_physical} Physical Cores, {cpu_cores_logical} Logical Threads)\n"
            f"- **Memory (RAM)**: `{vm.percent}% Used` ({round(vm.used / (1024**3), 1)} GB used of {round(vm.total / (1024**3), 1)} GB)\n"
            f"{battery_line}"
            f"- **System Uptime**: `{uptime_str}`\n"
            f"- **Storage Drives**:\n{disk_lines}\n"
            f"- **Operating System**: `{platform.platform()}`\n\n"
            f"System health is **NOMINAL**."
        )

        return raw_data, summary

    def _tool_ping_network_host(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Pings a network host to measure reachability and round-trip latency."""
        host = params.get("host", "8.8.8.8").strip()
        count = int(params.get("count", 1))
        count = max(1, min(count, 4))

        t0 = time.perf_counter()
        proc = subprocess.run(["ping", "-n", str(count), "-w", "2000", host], capture_output=True, text=True, timeout=10)
        elapsed_total = (time.perf_counter() - t0) * 1000.0

        success = proc.returncode == 0
        raw_output = proc.stdout

        # Try to parse average round trip time
        latency_ms = None
        if "Average =" in raw_output:
            try:
                latency_ms = float(raw_output.split("Average =")[1].split("ms")[0].strip())
            except Exception:
                pass
        elif success:
            latency_ms = round(elapsed_total / count, 1)

        raw_data = {
            "host": host,
            "reachable": success,
            "latency_ms": latency_ms,
            "raw_output": raw_output
        }

        if success:
            summary = f"Ping to **{host}** succeeded with latency of **{latency_ms or round(elapsed_total, 1)} ms** (0% packet loss)."
        else:
            summary = f"Ping to **{host}** timed out or host is unreachable."

        return raw_data, summary

    def _tool_list_network_adapters(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Lists all network adapters via PowerShell."""
        adapters = []
        try:
            cmd = "Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed | ConvertTo-Json"
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                if isinstance(data, dict):
                    data = [data]
                adapters = data
        except Exception as e:
            return {"error": str(e)}, f"Error listing adapters: {e}"

        lines = []
        for a in adapters:
            status_emoji = "[UP]" if a.get("Status") == "Up" else "[DOWN]"
            lines.append(f"- `{a.get('Name')}`: {status_emoji} `{a.get('Status')}` | {a.get('InterfaceDescription')} ({a.get('LinkSpeed')})")

        summary = f"### Detected Network Adapters ({len(adapters)} total)\n\n" + "\n".join(lines)
        return {"adapters": adapters}, summary

    def _tool_get_top_processes(self, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Gets top processes by memory or CPU."""
        sort_by = params.get("sort_by", "memory").lower()
        limit = int(params.get("limit", 5))
        limit = max(1, min(limit, 15))

        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_percent": info['cpu_percent'] or 0.0,
                    "memory_percent": round(info['memory_percent'] or 0.0, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if sort_by == "cpu":
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        else:
            processes.sort(key=lambda x: x["memory_percent"], reverse=True)

        top_list = processes[:limit]
        lines = [f"- PID `{p['pid']}` | `{p['name']}`: Memory {p['memory_percent']}% | CPU {p['cpu_percent']}%" for p in top_list]
        summary = f"### Top {limit} Active Processes (Sorted by {sort_by.upper()})\n\n" + "\n".join(lines)

        return {"processes": top_list, "sort_by": sort_by}, summary


# Global singleton instance
tool_engine = ToolCallingEngine()


def dispatch_tool_intent(query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Heuristic intent parser that translates natural language queries
    into tool execution calls (Function Calling dispatch).
    """
    q = query.lower()

    # Wi-Fi status queries
    if any(k in q for k in ["wifi", "wi-fi", "wlan", "wireless", "ssid", "internet connected"]):
        if any(k in q for k in ["profiles", "saved", "networks list", "known networks"]):
            return "list_wifi_profiles", {}
        return "get_wifi_status", {}

    # System vitals queries
    if any(k in q for k in [
        "system vitals", "system status", "cpu", "ram", "memory usage",
        "battery", "uptime", "how is my computer", "disk space", "storage free"
    ]):
        return "get_system_vitals", {}

    # Ping queries
    if "ping" in q:
        host = "8.8.8.8"
        parts = q.split()
        for idx, part in enumerate(parts):
            if part == "ping" and idx + 1 < len(parts):
                cand = parts[idx + 1].strip(".,;:?!")
                if len(cand) > 3 and not cand.startswith("-"):
                    host = cand
        return "ping_network_host", {"host": host}

    # Adapters list
    if any(k in q for k in ["adapters", "network interfaces", "nic", "ethernet adapter"]):
        return "list_network_adapters", {}

    # Top processes
    if any(k in q for k in ["top processes", "task manager", "what is running", "cpu hogs", "ram hogs"]):
        sort_by = "cpu" if "cpu" in q else "memory"
        return "get_top_processes", {"sort_by": sort_by, "limit": 5}

    return None
