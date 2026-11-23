"""Motor comparativo inicial BOT 03. Coeficientes heurísticos: requieren calibración."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
import math
import numpy as np
import pandas as pd

EFFECTIVE_SALE_TYPES = {"venta efectiva", "compraventa efectiva", "closed_sale", "cbr", "transaction"}
LISTING_TYPES = {"oferta publicada", "aviso publicado", "listing", "offer"}

@dataclass
class ValuationResult:
    status: str
    value_uf: float | None
    low_uf: float | None
    high_uf: float | None
    unit_uf_m2: float | None
    confidence: str
    comparable_count: int
    sale_count: int
    listing_count: int
    method: str
    warnings: list[str]
    used_comparables: list[dict]

def _norm(value):
    return str(value or "").strip().casefold()

def _weighted_quantile(values, weights, q):
    order = np.argsort(values)
    v = np.asarray(values, dtype=float)[order]
    w = np.asarray(weights, dtype=float)[order]
    if len(v) == 0 or w.sum() <= 0:
        return float("nan")
    cdf = np.cumsum(w) / w.sum()
    return float(v[min(np.searchsorted(cdf, q, side="left"), len(v)-1)])

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2)-float(lat1))
    dl = math.radians(float(lon2)-float(lon1))
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

def estimate_value(target: dict, comparables: pd.DataFrame, max_age_days: int = 365) -> ValuationResult:
    required = {"property_type", "commune", "price_uf", "area_m2", "basis", "evidence_type", "date"}
    missing = required - set(comparables.columns)
    if missing:
        raise ValueError("Faltan columnas: " + ", ".join(sorted(missing)))
    area = float(target.get("area_m2") or 0)
    if area <= 0:
        raise ValueError("La superficie objetivo debe ser mayor que cero.")
    today = pd.Timestamp.today().normalize()
    df = comparables.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["price_uf", "area_m2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date", "price_uf", "area_m2"])
    df = df[(df.price_uf > 0) & (df.area_m2 > 0)]
    df = df[df.property_type.map(_norm) == _norm(target["property_type"])]
    df = df[df.commune.map(_norm) == _norm(target["commune"])]
    df = df[df.basis.map(_norm) == _norm(target["basis"])]
    df = df[df.date >= today - pd.Timedelta(days=max_age_days)].copy()
    if df.empty:
        return ValuationResult("insufficient_data", None, None, None, None, "Insuficiente", 0, 0, 0,
                               "Sin comparables compatibles", ["No hay observaciones compatibles por tipología, comuna, base de superficie y antigüedad."], [])
    df["unit_uf_m2"] = df.price_uf / df.area_m2
    if "distance_km" not in df.columns:
        df["distance_km"] = np.nan
    else:
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
    coords = all(target.get(k) not in (None, "") for k in ["latitude", "longitude"])
    if coords and {"latitude", "longitude"}.issubset(df.columns):
        def dist(row):
            if pd.isna(row.latitude) or pd.isna(row.longitude):
                return np.nan
            return haversine_km(target["latitude"], target["longitude"], row.latitude, row.longitude)
        df["distance_km"] = df.apply(dist, axis=1)
    # Initial transparent heuristic weights; calibrate on verified Chilean sales before production.
    def weight(row):
        distance_weight = math.exp(-float(row.distance_km)/2.0) if pd.notna(row.distance_km) else 0.65
        ratio = min(area, float(row.area_m2)) / max(area, float(row.area_m2))
        size_weight = max(0.15, ratio ** 1.5)
        age_days = max(0, (today - row.date.normalize()).days)
        recency_weight = math.exp(-age_days/240.0)
        evidence = _norm(row.evidence_type)
        evidence_weight = 1.0 if evidence in EFFECTIVE_SALE_TYPES else (0.70 if evidence in LISTING_TYPES else 0.35)
        return max(0.001, distance_weight * size_weight * recency_weight * evidence_weight)
    df["weight"] = df.apply(weight, axis=1)
    # IQR filter: keep original records in source systems; flag exclusions in report.
    q1, q3 = df.unit_uf_m2.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr > 0:
        lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
        excluded = int(((df.unit_uf_m2 < lo) | (df.unit_uf_m2 > hi)).sum())
        df = df[(df.unit_uf_m2 >= lo) & (df.unit_uf_m2 <= hi)].copy()
    else:
        excluded = 0
    warnings = []
    if excluded:
        warnings.append(f"{excluded} observación(es) fuera de 1,5 IQR excluidas del cálculo.")
    sales = df[df.evidence_type.map(_norm).isin(EFFECTIVE_SALE_TYPES)]
    listings = df[df.evidence_type.map(_norm).isin(LISTING_TYPES)]
    if len(sales) >= 3:
        chosen = pd.concat([sales, listings]).sort_values("weight", ascending=False).head(15)
        method = "Ventas efectivas prioritarias, con ofertas complementarias"
    elif len(sales) > 0:
        chosen = pd.concat([sales, listings]).sort_values("weight", ascending=False).head(15)
        method = "Ventas efectivas y ofertas complementarias"
        warnings.append("Hay menos de tres ventas efectivas; las ofertas complementan la muestra.")
    else:
        chosen = listings.sort_values("weight", ascending=False).head(15)
        method = "Solo ofertas publicadas"
        warnings.append("No hay ventas efectivas. El resultado se basa en precios de oferta y puede diferir del precio de cierre.")
    if len(chosen) < 3:
        warnings.append("Menos de tres comparables: no utilizar como base única para decisiones comerciales o financieras.")
    if chosen.empty:
        return ValuationResult("insufficient_data", None, None, None, None, "Insuficiente", 0, 0, 0,
                               method, warnings + ["No quedaron observaciones utilizables."], [])
    values = chosen.unit_uf_m2.to_numpy()
    weights = chosen.weight.to_numpy()
    unit = _weighted_quantile(values, weights, 0.50)
    low_unit = _weighted_quantile(values, weights, 0.20)
    high_unit = _weighted_quantile(values, weights, 0.80)
    value = unit * area
    low, high = low_unit * area, high_unit * area
    if not np.isfinite(low) or not np.isfinite(high) or high <= low:
        low, high = value * 0.90, value * 1.10
        warnings.append("Rango ilustrativo por dispersión insuficiente; no es intervalo estadístico de confianza.")
    sale_count = int(chosen.evidence_type.map(_norm).isin(EFFECTIVE_SALE_TYPES).sum())
    listing_count = int(chosen.evidence_type.map(_norm).isin(LISTING_TYPES).sum())
    spread = (high-low)/value if value else 1
    if len(chosen) >= 8 and sale_count >= 5 and spread <= .20:
        confidence = "Alta"
    elif len(chosen) >= 5 and sale_count >= 2 and spread <= .35:
        confidence = "Media"
    else:
        confidence = "Baja"
    if not coords:
        warnings.append("No se proporcionaron coordenadas: la cercanía se ponderó de forma neutral.")
    if confidence == "Baja":
        warnings.append("La evidencia disponible no permite una estimación de alta confianza.")
    used = chosen.copy()
    used["date"] = used["date"].dt.strftime("%Y-%m-%d")
    records = used.replace({np.nan: None}).to_dict(orient="records")
    return ValuationResult("ok", round(value, 2), round(low, 2), round(high, 2), round(unit, 3),
                           confidence, len(chosen), sale_count, listing_count, method, warnings, records)

def financing_scenario(value_uf: float, haircut_pct: float, ltv_pct: float, existing_debt_uf: float = 0):
    if not 0 <= haircut_pct <= 60 or not 0 <= ltv_pct <= 90 or existing_debt_uf < 0:
        raise ValueError("Parámetros fuera de rango.")
    admissible = value_uf * (1 - haircut_pct/100)
    gross = admissible * ltv_pct/100
    return {
        "valor_admisible_simulado_uf": round(admissible, 2),
        "credito_bruto_hipotetico_uf": round(gross, 2),
        "potencial_neto_hipotetico_uf": round(max(0, gross-existing_debt_uf), 2)
    }

def gross_rental_yield(monthly_rent_uf: float, value_uf: float):
    if value_uf <= 0 or monthly_rent_uf < 0:
        raise ValueError("Arriendo o valor inválido.")
    return round(monthly_rent_uf * 12 / value_uf * 100, 2)
