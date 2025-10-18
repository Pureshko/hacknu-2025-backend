from abc import ABC, abstractmethod
from typing import Dict, List, Any
import asyncio
import aiohttp
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.rate_limiter = asyncio.Semaphore(10)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        region: str
    ) -> List[Dict[str, Any]]:
        """Search for accommodations"""
        pass
    
    @abstractmethod
    async def enrich_data(
        self, 
        accommodation_id: str
    ) -> Dict[str, Any]:
        """Enrich accommodation data with additional details"""
        pass
    
    async def rate_limited_request(
        self, 
        url: str, 
        params: Dict = None
    ) -> Dict:
        """Make rate-limited API request"""
        async with self.rate_limiter:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()