from datetime import date
import os
import hmac
import pandas as pd
import streamlit as st
from valuation_engine import estimate_value, financing_scenario, gross_rental_yield

st.set_page_config(page_title="BOT 03 | FC INMOBILIARIOS", page_icon="🏠", layout="wide")

# Acceso de staging: la clave se configura como secreto del servicio, nunca en Git.
_access_password = os.getenv("BOT03_ACCESS_PASSWORD", "")
if not _access_password:
    st.error("El entorno no está configurado: falta BOT03_ACCESS_PASSWORD.")
    st.stop()
if not st.session_state.get("bot03_authenticated", False):
    st.title("BOT 03 — Acceso privado")
    _entered = st.text_input("Contraseña de acceso", type="password")
    if st.button("Ingresar", type="primary"):
        if hmac.compare_digest(_entered, _access_password):
            st.session_state["bot03_authenticated"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()
st.title("BOT 03 — Tasador Inmobiliario IA")
st.caption("FC INMOBILIARIOS · MVP 0.1 · Motor propio de comparación de mercado")
st.warning("Estimación de apoyo comercial. No es tasación bancaria, pericial ni aprobación de crédito. La calidad del resultado depende de los comparables y sus fuentes.")

TYPES = ["Casa", "Departamento", "Terreno urbano", "Terreno rural", "Parcela", "Oficina", "Local comercial", "Bodega", "Industrial", "Uso mixto"]
BASES = ["Construida", "Útil", "Terreno", "Total", "Arrendable"]
EVIDENCE = ["Venta efectiva", "Oferta publicada"]

with st.sidebar:
    st.header("Identificación del inmueble")
    address = st.text_input("Dirección")
    commune = st.text_input("Comuna")
    region = st.text_input("Región", value="Región Metropolitana")
    property_type = st.selectbox("Tipología", TYPES)
    basis = st.selectbox("Base de superficie a comparar", BASES)
    area = st.number_input("Superficie objetivo (m²)", min_value=0.0, value=100.0, step=1.0)
    land_area = st.number_input("Superficie de terreno (m²)", min_value=0.0, value=0.0, step=1.0)
    latitude = st.text_input("Latitud (opcional)")
    longitude = st.text_input("Longitud (opcional)")
    st.caption("No mezclar superficies construidas, útiles y de terreno en una misma comparación.")

st.subheader("1. Características y observaciones")
c1, c2, c3 = st.columns(3)
with c1:
    bedrooms = st.number_input("Dormitorios", min_value=0, value=3)
    bathrooms = st.number_input("Baños", min_value=0, value=2)
with c2:
    parking = st.number_input("Estacionamientos", min_value=0, value=1)
    age = st.number_input("Antigüedad (años)", min_value=0, value=10)
with c3:
    condition = st.selectbox("Conservación", ["No informada", "Excelente", "Buena", "Regular", "Deficiente"])
    valuation_date = st.date_input("Fecha de análisis", value=date.today())
notes = st.text_area("Observaciones (remodelaciones, orientación, ampliaciones, vista, etc.)")

st.subheader("2. Comparables")
st.write("Ingresa observaciones con fuente y fecha. Las filas de demostración son ficticias y deben sustituirse antes de cualquier uso real.")
demo = pd.DataFrame([
    {"reference":"DEMO A - FICTICIO","property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":115,"price_uf":7800,"evidence_type":"Venta efectiva","date":"2026-03-10","distance_km":0.5,"source":"Dato ficticio de demostración"},
    {"reference":"DEMO B - FICTICIO","property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":120,"price_uf":8200,"evidence_type":"Venta efectiva","date":"2026-04-20","distance_km":0.8,"source":"Dato ficticio de demostración"},
    {"reference":"DEMO C - FICTICIO","property_type":"Casa","commune":"Providencia","basis":"Construida","area_m2":118,"price_uf":8500,"evidence_type":"Oferta publicada","date":"2026-05-01","distance_km":0.4,"source":"Dato ficticio de demostración"},
])
uploaded = st.file_uploader("Cargar comparables CSV", type=["csv"])
if uploaded:
    comps = pd.read_csv(uploaded)
else:
    comps = demo
    st.info("Estás viendo comparables ficticios. No representan propiedades ni transacciones reales.")
edited = st.data_editor(comps, num_rows="dynamic", use_container_width=True, key="comps")
st.download_button("Descargar plantilla CSV", demo.to_csv(index=False).encode("utf-8-sig"), "plantilla_comparables_bot03.csv", "text/csv")

st.subheader("3. Ejecutar valorización")
if st.button("Calcular valor comercial", type="primary", use_container_width=True):
    if not address.strip() or not commune.strip():
        st.error("Completa dirección y comuna.")
    elif area <= 0:
        st.error("La superficie objetivo debe ser mayor que cero.")
    else:
        target = {"property_type":property_type,"commune":commune,"basis":basis,"area_m2":area}
        try:
            if latitude.strip() and longitude.strip():
                target["latitude"] = float(latitude)
                target["longitude"] = float(longitude)
            result = estimate_value(target, edited)
            st.session_state["result"] = result
            st.session_state["property"] = {"address":address,"commune":commune,"region":region,"type":property_type,
                                            "basis":basis,"area":area,"land_area":land_area,"bedrooms":bedrooms,
                                            "bathrooms":bathrooms,"parking":parking,"age":age,"condition":condition,
                                            "date":str(valuation_date),"notes":notes}
        except Exception as exc:
            st.error(f"No fue posible calcular: {exc}")

if "result" in st.session_state:
    result = st.session_state["result"]
    prop = st.session_state["property"]
    if result.status == "ok":
        a,b,c = st.columns(3)
        a.metric("Valor central estimado", f"{result.value_uf:,.0f} UF")
        b.metric("Rango empírico", f"{result.low_uf:,.0f} – {result.high_uf:,.0f} UF")
        c.metric("Calidad de evidencia", result.confidence)
        st.write(f"**Precio unitario:** {result.unit_uf_m2:,.2f} UF/m² · **Comparables:** {result.comparable_count} · **Ventas:** {result.sale_count} · **Ofertas:** {result.listing_count}")
        st.write("**Método:** " + result.method)
        for warning in result.warnings:
            st.warning(warning)
        st.subheader("Comparables utilizados")
        used = pd.DataFrame(result.used_comparables)
        st.dataframe(used, use_container_width=True)
        st.subheader("4. Escenario de garantía (hipotético)")
        x,y,z = st.columns(3)
        haircut = x.slider("Descuento prudencial supuesto (%)", 0, 60, 15)
        ltv = y.slider("LTV supuesto (%)", 0, 90, 60)
        debt = z.number_input("Deuda vigente declarada (UF)", min_value=0.0, value=0.0)
        st.json(financing_scenario(result.value_uf, haircut, ltv, debt))
        st.caption("No representa política bancaria, tasación admisible, preaprobación ni oferta de crédito.")
        st.subheader("5. Escenario de arriendo")
        rent = st.number_input("Arriendo mensual estimado (UF)", min_value=0.0, value=0.0)
        if rent > 0:
            st.metric("Rentabilidad bruta anual", f"{gross_rental_yield(rent, result.value_uf)}%")
            st.caption("No descuenta vacancia, gastos comunes, contribuciones, mantención, administración ni impuestos.")
        report = f"""# FC INMOBILIARIOS — Informe preliminar BOT 03
**Fecha de análisis:** {prop['date']}

## Inmueble
- Dirección: {prop['address']}, {prop['commune']}, {prop['region']}
- Tipología: {prop['type']}
- Superficie de análisis: {prop['area']} m² ({prop['basis']})
- Superficie terreno declarada: {prop['land_area']} m²
- Dormitorios/baños: {prop['bedrooms']}/{prop['bathrooms']}
- Estacionamientos: {prop['parking']}
- Antigüedad: {prop['age']} años
- Conservación: {prop['condition']}

## Resultado
- Valor central: {result.value_uf:,.2f} UF
- Rango empírico: {result.low_uf:,.2f} – {result.high_uf:,.2f} UF
- Valor unitario: {result.unit_uf_m2:,.3f} UF/m²
- Calidad de evidencia: {result.confidence}
- Método: {result.method}

## Advertencias
{chr(10).join('- '+w for w in result.warnings)}

## Observaciones
{prop['notes']}

## Limitación
Estimación automatizada de apoyo comercial basada en los datos ingresados. No constituye tasación bancaria, pericial ni aprobación de financiamiento. La calidad depende de la exactitud, representatividad y autorización de uso de los comparables.
"""
        st.download_button("Descargar informe preliminar", report, "informe_bot03.md", "text/markdown")
        st.download_button("Descargar comparables utilizados", used.to_csv(index=False).encode("utf-8-sig"), "comparables_utilizados.csv", "text/csv")
    else:
        st.error("Información insuficiente para estimar el valor.")
        for warning in result.warnings:
            st.write("- " + warning)

st.divider()
st.caption("BOT 03 · FC INMOBILIARIOS · MVP 0.1 · No conectado todavía a proveedores externos.")
