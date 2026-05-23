"""
ChainGuard - AI-Powered Blockchain Security Platform
Main engine coordinating 6 specialized agents.
"""

__version__ = "1.0.0"
__author__ = "ChainGuard Team"

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chainguard")


class Severity(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Alert types for different threats."""
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"
    SUSPICIOUS = "suspicious"
    GOVERNANCE = "governance"
    ORACLE = "oracle"
    MEV = "mev"


@dataclass
class Vulnerability:
    """Represents a detected vulnerability."""
    id: str
    name: str
    severity: Severity
    contract: str
    chain: str
    description: str
    impact: str
    recommendation: str
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    confidence: float = 0.0
    cwe_id: Optional[str] = None
    swc_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity.value,
            "contract": self.contract,
            "chain": self.chain,
            "description": self.description,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "tx_hash": self.tx_hash,
            "block_number": self.block_number,
            "confidence": self.confidence,
            "cwe_id": self.cwe_id,
            "swc_id": self.swc_id
        }


@dataclass
class Alert:
    """Represents a security alert."""
    id: str
    type: AlertType
    severity: Severity
    title: str
    description: str
    chain: str
    contract: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class AgentMetrics:
    """Agent performance metrics."""
    contracts_scanned: int = 0
    vulnerabilities_found: int = 0
    alerts_generated: int = 0
    exploits_prevented: int = 0
    uptime_seconds: float = 0
    avg_scan_time_ms: float = 0


class ChainGuardEngine:
    """Core engine coordinating all security agents."""
    
    def __init__(self):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.vulnerabilities: List[Vulnerability] = []
        self.alerts: List[Alert] = []
        self.metrics = AgentMetrics()
        self.running = False
        self._start_time = None
        self.monitored_contracts: Dict[str, Dict] = {}
    
    def register_agent(self, name: str, agent: 'BaseAgent'):
        """Register a new agent with the engine."""
        self.agents[name] = agent
        logger.info(f"Agent registered: {name}")
    
    def add_contract(self, address: str, chain: str, name: str = ""):
        """Add a contract to monitor."""
        self.monitored_contracts[address] = {
            "chain": chain,
            "name": name,
            "added": datetime.utcnow().isoformat(),
            "alerts": 0
        }
        logger.info(f"Monitoring contract: {address} on {chain}")
    
    async def start(self, agents: Optional[List[str]] = None):
        """Start specified or all agents."""
        self.running = True
        self._start_time = datetime.utcnow()
        
        targets = agents or list(self.agents.keys())
        tasks = []
        
        for name in targets:
            if name in self.agents:
                tasks.append(self._run_agent(name))
        
        logger.info(f"Starting {len(tasks)} agents...")
        await asyncio.gather(*tasks)
    
    async def _run_agent(self, name: str):
        """Run a single agent."""
        agent = self.agents[name]
        try:
            logger.info(f"Agent {name} started")
            await agent.run()
        except Exception as e:
            logger.error(f"Agent {name} error: {e}")
    
    async def stop(self):
        """Stop all agents."""
        self.running = False
        logger.info("All agents stopped")
    
    def add_vulnerability(self, vuln: Vulnerability):
        """Add a detected vulnerability."""
        self.vulnerabilities.append(vuln)
        self.metrics.vulnerabilities_found += 1
        logger.warning(f"Vulnerability: {vuln.name} [{vuln.severity.value}] on {vuln.contract}")
    
    def add_alert(self, alert: Alert):
        """Add a security alert."""
        self.alerts.append(alert)
        self.metrics.alerts_generated += 1
        logger.warning(f"Alert: {alert.title} [{alert.severity.value}]")
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "running": self.running,
            "uptime": (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0,
            "monitored_contracts": len(self.monitored_contracts),
            "total_vulnerabilities": len(self.vulnerabilities),
            "total_alerts": len(self.alerts),
            "vulnerabilities_by_severity": {
                sev.value: len([v for v in self.vulnerabilities if v.severity == sev])
                for sev in Severity
            },
            "agents": {
                name: {"status": "active", "metrics": agent.metrics.__dict__}
                for name, agent in self.agents.items()
            }
        }


class BaseAgent:
    """Base class for all ChainGuard agents."""
    
    def __init__(self, name: str, engine: ChainGuardEngine):
        self.name = name
        self.engine = engine
        self.metrics = AgentMetrics()
        self._start_time = None
    
    async def run(self):
        """Main agent loop."""
        self._start_time = datetime.utcnow()
        while self.engine.running:
            await self.process()
            await asyncio.sleep(1)
    
    async def process(self):
        """Process events. Override in subclass."""
        raise NotImplementedError
    
    def report_vulnerability(self, vuln: Vulnerability):
        """Report a vulnerability to the engine."""
        self.engine.add_vulnerability(vuln)
        self.metrics.vulnerabilities_found += 1
    
    def report_alert(self, alert: Alert):
        """Report an alert to the engine."""
        self.engine.add_alert(alert)
        self.metrics.alerts_generated += 1


__all__ = [
    "ChainGuardEngine", "BaseAgent", "Vulnerability", "Alert",
    "Severity", "AlertType", "AgentMetrics"
]
