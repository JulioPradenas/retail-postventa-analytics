# Insights de Negocio — Retail Postventa Analytics

## ⭐ Insight Estrella: OTD↔CPO

### Hallazgo

Cuando un pedido llega **atrasado**, la probabilidad de que el cliente
contacte al servicio postventa sube **2.4×**:

| Entrega | Órdenes | Con contacto | Tasa de contacto |
|---------|--------:|-------------:|-----------------:|
| En tiempo | 8,581 | 2,454 | **28.6%** |
| Atrasada  | 1,419 |   960 | **67.6%** |

**CPO global: 0.341** (3,414 contactos / 10,000 órdenes)

### Implicancias operativas

- El **14.2%** de las órdenes llegan con atraso.
- Cada punto porcentual de mejora en OTD reduce el CPO en ~0.04.
- Si OTD mejora del 85.8% → 95%, el CPO proyectado bajaría de 0.34 → ~0.26,
  equivalente a ~800 contactos evitables al año (escala 10K órdenes).

### Carriers con mayor tasa de atraso

Ver `mart_otd_vs_sla` — StarKen y Correos de Chile concentran los atrasos
con OTD en zona "regions" por debajo del promedio.

### Dónde verlo

- **Nivel orden**: `fct_orders` JOIN `fct_contacts` — comparar `is_late` vs
  presencia de contacto.
- **Nivel semanal**: `mart_correlacion_otd_cpo` — OTD y CPO por semana con
  bucket de OTD. La varianza semanal es baja porque el late rate es estable
  (~14%); el insight es más nítido a nivel individual.
- **Dashboard**: gráfico de dispersión orden × (is_late, has_contact).
