"""Evidence classification for BOT03; contextual observations must not enter sale-value calculations."""
from __future__ import annotations

CATEGORIES = {
    "transaction": {"venta efectiva", "compraventa efectiva", "closed_sale", "cbr", "transaction", "transacción verificable"},
    "listing_current": {"oferta publicada", "aviso publicado", "listing", "offer", "oferta vigente"},
    "listing_historical": {"oferta histórica", "aviso histórico", "historical listing"},
    "rental": {"arriendo", "arrendamiento", "rental", "lease"},
    "auction": {"remate", "auction", "subasta"},
    "new_project": {"proyecto nuevo", "new project", "venta proyecto"},
}

def normalize(value) -> str:
    return str(value or "").strip().casefold()

def classify_evidence(value) -> str:
    key = normalize(value)
    for category, aliases in CATEGORIES.items():
        if key in aliases:
            return category
    return "unknown"

def is_sale_valuation_evidence(value) -> bool:
    """Only verified transaction and current sale listing are eligible for direct estimate."""
    return classify_evidence(value) in {"transaction", "listing_current"}

def is_context_only(value) -> bool:
    return classify_evidence(value) in {"listing_historical", "rental", "auction", "new_project", "unknown"}
