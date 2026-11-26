# BOT 03 — Tasador Inmobiliario IA | MVP 0.1

Aplicación inicial de FC INMOBILIARIOS para estimación comercial residencial y comercial mediante comparables ingresados y revisados por el usuario.

## Incluye
- Tipologías: casa, departamento, terreno urbano/rural, parcela, oficina, local, bodega, industrial y uso mixto.
- Separación explícita de superficie construida, útil, terreno y otras bases comparables.
- Comparables clasificados como compraventa efectiva o aviso publicado.
- Ponderación por distancia, similitud de superficie, antigüedad del antecedente y tipo de evidencia.
- Mediana ponderada, rango empírico y advertencias de calidad.
- Escenarios hipotéticos de garantía hipotecaria y rendimiento bruto de arriendo.
- Exportación de comparables en CSV e informe preliminar en Markdown.

## Ejecutar localmente
Requiere Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run BOT03/app.py
```

## Despliegue
El hosting compartido de HostGator se mantiene para dominios/DNS; no ejecuta esta aplicación. El MVP se prepara para Render mediante `render.yaml`, conectado a la rama `feat/bot03-mvp` de GitHub. Render construye el contenedor desde `BOT03/Dockerfile`. El despliegue requiere que el usuario conecte su cuenta Render al repositorio y configure `BOT03_ACCESS_PASSWORD` como secreto durante la creación del servicio. No publicar credenciales en GitHub. El plan gratuito es solo staging/pruebas: puede suspenderse por inactividad y no debe usarse para cargas de trabajo críticas.

## Datos
Esta versión NO consulta automáticamente SII, CBR, TOCTOC, Catastral.cl ni DescubroData. Los comparables se ingresan manualmente o mediante CSV y deben contar con fuente y autorización de uso. La integración API se hará cuando se validen contratos, licencias, cuotas y esquemas reales.

## Metodología y limitaciones
El valor central es una mediana ponderada de UF/m² de comparables compatibles. El rango es empírico, no intervalo estadístico de confianza. Los coeficientes de ponderación son heurísticos iniciales y requieren calibración con transacciones verificadas. No es tasación bancaria, pericial ni oferta de crédito.

En casas, parcelas, terrenos y activos mixtos no se deben mezclar superficies de terreno y construcción. Seleccionar una base homogénea y utilizar comparables compatibles. Para valoración de suelo + edificación, capitalización de rentas y residual urbanístico se requieren módulos específicos posteriores.

## Variables de entorno
- `BOT03_ACCESS_PASSWORD`: contraseña de acceso al entorno de pruebas. Obligatoria; si falta, la aplicación no abre.
- Cuando se integren proveedores, usar secretos del entorno de despliegue y nunca versionarlos.

## Estado
MVP de demostración funcional. Configuración de despliegue Render preparada; requiere conectar la cuenta y completar la creación del servicio. Antes de uso comercial: probar con datos reales autorizados, revisión de un tasador, backtesting por tipología/comuna, persistencia, autenticación robusta y controles de seguridad.


## Estándar metodológico actualizado

Consulta `BOT03/METODOLOGIA_VALORIZACION_V1.md` para el protocolo de investigación, clasificación de evidencia (transacción, oferta vigente/histórica, arriendo, remate y proyecto nuevo), comparabilidad, ajustes fundamentados, estrategia comercial, confianza y control de calidad del informe. Esta guía complementa el MVP y no implica que las funciones automatizadas estén ya implementadas en la interfaz o motor. Pendientes de desarrollo: capturar todas las categorías, producir el reporte cliente estandarizado, calcular/publicar confianza por reglas auditables y calibrar ajustes con datos verificados.

## Implementación parcial del estándar (en desarrollo)
- Se incorporó `BOT03/evidence_classifier.py` para clasificar evidencia A-F y desconocida.
- El motor ahora excluye del cálculo directo observaciones contextuales como arriendos, remates, proyectos nuevos, ofertas históricas y categorías desconocidas; estas no se deben interpretar como comparables de venta.
- Las categorías de cálculo directo son transacción/verificación y oferta de venta vigente.
- Se añadieron pruebas de clasificación y exclusión contextual.
- Esta implementación es parcial: aún no genera el informe completo, los ajustes comerciales explicables ni el registro enriquecido de fuentes automáticamente.
