"""
ChainGuard - API Integrations
Connect to blockchain security services.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime


class EtherscanAPI:
    """Etherscan API for contract verification and data."""
    
    BASE_URLS = {
        "ethereum": "https://api.etherscan.io/api",
        "bsc": "https://api.bscscan.com/api",
        "polygon": "https://api.polygonscan.com/api",
        "arbitrum": "https://api.arbiscan.io/api",
        "base": "https://api.basescan.org/api"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_contract_abi(self, address: str, chain: str = "ethereum") -> Dict:
        """Get contract ABI."""
        base = self.BASE_URLS.get(chain, self.BASE_URLS["ethereum"])
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base}?module=contract&action=getabi&address={address}&apikey={self.api_key}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"abi": data.get("result"), "status": data.get("status")}
                return {"error": f"HTTP {resp.status}"}
    
    async def get_contract_source(self, address: str, chain: str = "ethereum") -> Dict:
        """Get contract source code."""
        base = self.BASE_URLS.get(chain, self.BASE_URLS["ethereum"])
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base}?module=contract&action=getsourcecode&address={address}&apikey={self.api_key}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get("result", [{}])[0]
                    return {
                        "source": result.get("SourceCode"),
                        "name": result.get("ContractName"),
                        "compiler": result.get("CompilerVersion"),
                        "verified": result.get("ABI") != "Contract source code not verified"
                    }
                return {"error": f"HTTP {resp.status}"}
    
    async def get_transactions(self, address: str, chain: str = "ethereum", limit: int = 100) -> List[Dict]:
        """Get recent transactions."""
        base = self.BASE_URLS.get(chain, self.BASE_URLS["ethereum"])
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={self.api_key}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", [])[:limit]
                return []


class DeFiLlamaAPI:
    """DeFiLlama API for TVL and protocol data."""
    
    BASE_URL = "https://api.llama.fi"
    
    async def get_protocol(self, name: str) -> Dict:
        """Get protocol TVL and data."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/protocol/{name}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "name": data.get("name"),
                        "tvl": data.get("tvl", 0),
                        "chain": data.get("chain"),
                        "category": data.get("category"),
                        "chains": data.get("chains", [])
                    }
                return {"error": f"HTTP {resp.status}"}
    
    async def get_tvl(self, chain: str = None) -> Dict:
        """Get TVL for chain or all."""
        url = f"{self.BASE_URL}/v2/chains" if chain else f"{self.BASE_URL}/protocols"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    
    async def get_stablecoins(self) -> List[Dict]:
        """Get stablecoin data."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/stablecoins") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("peggedAssets", [])
                return []


class TenderlyAPI:
    """Tenderly API for transaction simulation."""
    
    BASE_URL = "https://api.tenderly.co/api/v1"
    
    def __init__(self, api_key: str, project: str):
        self.api_key = api_key
        self.project = project
        self.headers = {"X-Access-Key": api_key}
    
    async def simulate_tx(self, tx: Dict) -> Dict:
        """Simulate a transaction."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/account/{self.project}/simulate",
                headers=self.headers,
                json=tx
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    
    async def get_contract(self, address: str, chain: str = "1") -> Dict:
        """Get contract data."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/account/{self.project}/contract/{chain}/{address}",
                headers=self.headers
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}


class SlitherAPI:
    """Slither static analysis integration."""
    
    async def analyze(self, contract_path: str) -> Dict:
        """Run Slither analysis on contract."""
        # This would call slither CLI
        return {
            "detectors": [],
            "optimizations": [],
            "summary": {
                "high": 0,
                "medium": 0,
                "low": 0,
                "informational": 0
            }
        }


class SecurityIntelManager:
    """Unified security intelligence manager."""
    
    def __init__(self, config: Dict[str, str] = None):
        config = config or {}
        self.etherscan = EtherscanAPI(config.get("etherscan_key", ""))
        self.defillama = DeFiLlamaAPI()
        self.tenderly = TenderlyAPI(
            config.get("tenderly_key", ""),
            config.get("tenderly_project", "")
        )
        self.slither = SlitherAPI()
    
    async def full_analysis(self, address: str, chain: str = "ethereum") -> Dict:
        """Run full security analysis on contract."""
        results = await asyncio.gather(
            self.etherscan.get_contract_source(address, chain),
            self.etherscan.get_contract_abi(address, chain),
            return_exceptions=True
        )
        
        return {
            "address": address,
            "chain": chain,
            "source": results[0] if not isinstance(results[0], Exception) else {},
            "abi": results[1] if not isinstance(results[1], Exception) else {},
            "analyzed_at": datetime.utcnow().isoformat()
        }


__all__ = [
    "EtherscanAPI", "DeFiLlamaAPI", "TenderlyAPI",
    "SlitherAPI", "SecurityIntelManager"
]
