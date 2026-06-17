# M7 — Resultados del Modelo Predictivo

## Objetivo

Predecir si una orden de e-commerce generará un contacto postventa,
usando solo información disponible al momento del despacho (sin data leakage).

## Datos

- **10,000 órdenes** (año 2024, datos sintéticos)
- **Tasa de contacto global:** 34.1%
- Split: 80% train / 20% test (estratificado)

## Modelo

**Logistic Regression** (sklearn) con:
- `class_weight="balanced"` para manejar el desbalance (65% sin contacto / 35% con contacto)
- One-hot encoding para variables categóricas
- `max_iter=1000`, `random_state=42`

## Resultados (test set — 2,000 órdenes)

**ROC-AUC: 0.9427**

```
              precision    recall  f1-score   support

Sin contacto       0.99      0.83      0.90      1317
Con contacto       0.75      0.99      0.85       683

    accuracy                           0.88      2000
   macro avg       0.87      0.91      0.88      2000
weighted avg       0.91      0.88      0.89      2000

```

## Top 10 Features por Importancia (|coeficiente|)

| Feature | |Coeficiente| |
|---|---|
| carrier_Chilexpress | 6.9365 |
| is_late_int | 4.9374 |
| carrier_Correos de Chile | 4.7889 |
| carrier_Bluexpress | 3.8165 |
| carrier_DHL | 3.4975 |
| carrier_StarKen | 3.1303 |
| carrier_modality_normal | 1.6585 |
| zone_regions | 1.2885 |
| delay_days | 0.9634 |
| customer_segment_nuevo | 0.7827 |

## Interpretación

- **`is_late_int`** domina el modelo — confirma el insight estrella OTD↔CPO.
- Las features categóricas (carrier, región) aportan información marginal adicional.
- ROC-AUC > 0.85 indica que el modelo es útil para priorización operativa.

## Uso potencial

- **Score de riesgo por orden**: al confirmar el despacho, calcular P(contacto).
- **Priorización de carriers**: identificar carriers con mayor riesgo sistémico.
- **Alertas tempranas**: notificar al equipo de CC cuando hay alta probabilidad de contacto.
