"""
ChainGuard - Main Application
Entry point for the blockchain security platform.
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime

from core import ChainGuardEngine, Severity
from agents import (
    SentinelAgent, AuditorAgent, OracleAgent,
    ShieldAgent, WatchtowerAgent, CommanderAgent
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("chainguard")


class ChainGuard:
    """Main ChainGuard application."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.engine = ChainGuardEngine()
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize all agents."""
        # Sentinel - Contract Monitoring
        sentinel = SentinelAgent(self.engine, self.config.get("sentinel", {}))
        self.engine.register_agent("sentinel", sentinel)
        
        # Auditor - Code Review
        auditor = AuditorAgent(self.engine, self.config.get("auditor", {}))
        self.engine.register_agent("auditor", auditor)
        
        # Oracle - Price Feeds
        oracle = OracleAgent(self.engine, self.config.get("oracle", {}))
        self.engine.register_agent("oracle", oracle)
        
        # Shield - Attack Protection
        shield = ShieldAgent(self.engine, self.config.get("shield", {}))
        self.engine.register_agent("shield", shield)
        
        # Watchtower - Whale Tracking
        watchtower = WatchtowerAgent(self.engine, self.config.get("watchtower", {}))
        self.engine.register_agent("watchtower", watchtower)
        
        # Commander - Incident Response
        commander = CommanderAgent(self.engine, self.config.get("commander", {}))
        self.engine.register_agent("commander", commander)
        
        logger.info("All agents initialized")
    
    async def start(self, agents: list = None):
        """Start the platform."""
        logger.info("=" * 60)
        logger.info("ChainGuard - AI-Powered Blockchain Security")
        logger.info("=" * 60)
        logger.info(f"Starting at {datetime.utcnow().isoformat()}")
        logger.info(f"Agents: {', '.join(self.engine.agents.keys())}")
        logger.info("=" * 60)
        
        await self.engine.start(agents)
    
    async def stop(self):
        """Stop the platform."""
        logger.info("Stopping ChainGuard...")
        await self.engine.stop()
        logger.info("ChainGuard stopped")
    
    def monitor(self, address: str, chain: str = "ethereum", name: str = ""):
        """Add contract to monitor."""
        self.engine.add_contract(address, chain, name)
    
    def status(self) -> dict:
        """Get platform status."""
        return self.engine.get_status()
    
    def vulnerabilities(self, severity: str = None):
        """Get detected vulnerabilities."""
        if severity:
            return [v for v in self.engine.vulnerabilities if v.severity.value == severity]
        return self.engine.vulnerabilities
    
    def alerts(self, severity: str = None):
        """Get security alerts."""
        if severity:
            return [a for a in self.engine.alerts if a.severity.value == severity]
        return self.engine.alerts


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ChainGuard - AI-Powered Blockchain Security")
    parser.add_argument("action", choices=["start", "monitor", "audit", "status", "alerts"],
                       help="Action to perform")
    parser.add_argument("--chain", default="ethereum", help="Blockchain to monitor")
    parser.add_argument("--contract", help="Contract address")
    parser.add_argument("--agents", nargs="+", help="Specific agents to run")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    # Load config
    config = {}
    if args.config:
        import yaml
        with open(args.config) as f:
            config = yaml.safe_load(f)
    
    # Create platform
    platform = ChainGuard(config)
    
    if args.action == "start":
        try:
            await platform.start(args.agents)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await platform.stop()
    
    elif args.action == "monitor":
        if args.contract:
            platform.monitor(args.contract, args.chain)
            print(f"Monitoring {args.contract} on {args.chain}")
        else:
            print("Error: --contract required")
    
    elif args.action == "audit":
        if args.contract:
            print(f"Auditing {args.contract} on {args.chain}...")
            # Run audit
        else:
            print("Error: --contract required")
    
    elif args.action == "status":
        import json
        print(json.dumps(platform.status(), indent=2))
    
    elif args.action == "alerts":
        import json
        alerts = platform.alerts()
        print(json.dumps([a.__dict__ for a in alerts], indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
