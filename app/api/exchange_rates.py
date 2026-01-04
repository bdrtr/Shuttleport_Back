# Exchange Rate API - Real-time currency conversion rates
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import httpx
from typing import Dict, Optional

router = APIRouter(prefix="/api", tags=["exchange-rates"])

# Cache for exchange rates
_exchange_rate_cache: Optional[Dict] = None
_cache_timestamp: Optional[datetime] = None
_CACHE_DURATION = timedelta(hours=1)  # Cache for 1 hour

# Fallback rates (used if API fails)
FALLBACK_RATES = {
    "TRY": 1.0,
    "EUR": 0.029,
    "USD": 0.031,
    "GBP": 0.025
}


async def fetch_exchange_rates() -> Dict[str, float]:
    """
    Fetch current exchange rates from exchangerate-api.com
    Base currency: TRY (Turkish Lira)
    """
    try:
        # Using exchangerate-api.com free API (no key required for basic usage)
        url = "https://open.er-api.com/v6/latest/TRY"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                rates = data.get("rates", {})
                return {
                    "TRY": 1.0,  # Base currency
                    "EUR": rates.get("EUR", FALLBACK_RATES["EUR"]),
                    "USD": rates.get("USD", FALLBACK_RATES["USD"]),
                    "GBP": rates.get("GBP", FALLBACK_RATES["GBP"])
                }
            else:
                raise Exception("API returned unsuccessful result")
                
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        # Return fallback rates
        return FALLBACK_RATES


def is_cache_valid() -> bool:
    """Check if cached exchange rates are still valid"""
    if _cache_timestamp is None or _exchange_rate_cache is None:
        return False
    return datetime.now() - _cache_timestamp < _CACHE_DURATION


@router.get("/exchange-rates")
async def get_exchange_rates():
    """
    Get current exchange rates for TRY base currency.
    Results are cached for 1 hour to reduce API calls.
    
    Returns:
        {
            "rates": {
                "TRY": 1.0,
                "EUR": 0.029,
                "USD": 0.031,
                "GBP": 0.025
            },
            "last_updated": "2024-01-04T02:54:00Z",
            "cached": true/false
        }
    """
    global _exchange_rate_cache, _cache_timestamp
    
    # Return cached rates if still valid
    if is_cache_valid():
        return {
            "rates": _exchange_rate_cache,
            "last_updated": _cache_timestamp.isoformat(),
            "cached": True
        }
    
    # Fetch fresh rates
    rates = await fetch_exchange_rates()
    
    # Update cache
    _exchange_rate_cache = rates
    _cache_timestamp = datetime.now()
    
    return {
        "rates": rates,
        "last_updated": _cache_timestamp.isoformat(),
        "cached": False
    }
