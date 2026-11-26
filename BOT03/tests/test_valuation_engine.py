import pandas as pd
from valuation_engine import estimate_value, financing_scenario, gross_rental_yield
from evidence_classifier import classify_evidence, is_sale_valuation_evidence

def sample():
    return pd.DataFrame([
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100,"price_uf":5000,"evidence_type":"Venta efectiva","date":str(pd.Timestamp.today().date()),"distance_km":0.5},
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":105,"price_uf":5250,"evidence_type":"Venta efectiva","date":str(pd.Timestamp.today().date()),"distance_km":0.7},
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":98,"price_uf":5100,"evidence_type":"Oferta publicada","date":str(pd.Timestamp.today().date()),"distance_km":0.3},
    ])

def test_returns_value_with_compatible_comparables():
    target={"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100}
    result=estimate_value(target,sample())
    assert result.status=="ok"
    assert result.value_uf > 0
    assert result.comparable_count >= 2

def test_no_mix_of_surface_basis():
    target={"property_type":"Casa","commune":"Providencia","basis":"Terreno","area_m2":300}
    result=estimate_value(target,sample())
    assert result.status=="insufficient_data"

def test_financing_is_only_arithmetic_scenario():
    result=financing_scenario(5000,10,60,500)
    assert result["credito_bruto_hipotetico_uf"] == 2700
    assert result["potencial_neto_hipotetico_uf"] == 2200

def test_rental_yield():
    assert gross_rental_yield(25,5000) == 6.0


def test_missing_distance_column_is_supported():
    target={"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100}
    comps=sample().drop(columns=["distance_km"])
    result=estimate_value(target,comps)
    assert result.status=="ok"
    assert result.value_uf > 0

def test_context_evidence_categories():
    assert classify_evidence("Venta efectiva") == "transaction"
    assert classify_evidence("Oferta publicada") == "listing_current"
    assert classify_evidence("Arriendo") == "rental"
    assert classify_evidence("Remate") == "auction"
    assert classify_evidence("Proyecto nuevo") == "new_project"
    assert is_sale_valuation_evidence("Venta efectiva")
    assert is_sale_valuation_evidence("Oferta publicada")
    assert not is_sale_valuation_evidence("Arriendo")
    assert not is_sale_valuation_evidence("Remate")

def test_context_only_rows_excluded_from_direct_estimate():
    comps=sample()
    extra=pd.DataFrame([
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100,"price_uf":9000,"evidence_type":"Arriendo","date":str(pd.Timestamp.today().date()),"distance_km":0.1},
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100,"price_uf":9000,"evidence_type":"Remate","date":str(pd.Timestamp.today().date()),"distance_km":0.1},
        {"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100,"price_uf":9000,"evidence_type":"Proyecto nuevo","date":str(pd.Timestamp.today().date()),"distance_km":0.1},
    ])
    target={"property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":100}
    result=estimate_value(target,pd.concat([comps,extra],ignore_index=True))
    assert result.status=="ok"
    assert result.comparable_count==3
    assert any("excluidas del cálculo directo" in w for w in result.warnings)
