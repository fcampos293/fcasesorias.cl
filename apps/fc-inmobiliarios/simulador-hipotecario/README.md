# Simulador Hipotecario — FC INMOBILIARIOS

Aplicación web estática e independiente de WordPress.

## Ejecutar localmente
Abre `index.html` en un navegador moderno. No requiere build ni dependencias externas.

## Publicación
La carpeta puede publicarse con GitHub Pages. El workflow `.github/workflows/pages.yml` publica el contenido de `apps/fc-inmobiliarios/simulador-hipotecario`.

## Funcionalidad
- Precio de propiedad en UF.
- Pie porcentual.
- Tasa anual nominal editable.
- Plazo en años.
- Valor UF editable.
- Dividendo mensual en UF y CLP.
- Monto de pie y financiamiento.
- Renta líquida referencial según porcentaje de dividendo.
- Compartir/copiar resumen de simulación.

## Supuestos y límites
La tasa mensual se aproxima como tasa nominal anual / 12. La cuota usa fórmula de anualidad con pagos mensuales constantes. El cálculo no incorpora seguros, gastos operacionales, impuestos, comisiones ni cargos bancarios. No consulta bancos ni determina aprobación crediticia.

Valor UF predeterminado: $41.391,69 CLP, referencia del 23-11-2026, Banco Central de Chile. El campo es editable y no se actualiza automáticamente.

## Pendientes para operación comercial
- Crear y conectar base CRM de Notion mediante backend/automatización segura.
- Configurar dominio y hosting.
- Definir endpoint de captura y consentimiento de datos.
- Agregar política de privacidad y contacto comercial aprobado.
- Ejecutar QA independiente y revisión de accesibilidad.

No incorporar secretos de Notion en el navegador ni en este repositorio.
