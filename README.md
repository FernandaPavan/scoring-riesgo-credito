# 💳 Sistema de Evaluación de Riesgo y Score de Crédito

## 📌 Descripción del Proyecto

Este proyecto presenta un sistema completo de **Scoring de Crédito** desarrollado para apoyar decisiones de riesgo crediticio mediante técnicas de **Data Science, Machine Learning y analítica financiera**.

La aplicación fue construida con foco en:

* Evaluación automatizada de riesgo
* Segmentación de clientes
* Definición de límites sugeridos
* Interpretabilidad del modelo
* Monitoreo de estabilidad poblacional
* Simulación interactiva de solicitudes de crédito

El sistema transforma datos históricos de clientes en decisiones estructuradas de aprobación, revisión o rechazo de crédito.

---

# 🎯 Objetivo del Proyecto

El objetivo principal es demostrar cómo un modelo de scoring puede:

* Reducir el riesgo de incumplimiento
* Estandarizar decisiones crediticias
* Identificar perfiles de alto y bajo riesgo
* Mejorar la eficiencia operacional
* Apoyar procesos de concesión de crédito con datos

Además, el proyecto busca simular una arquitectura utilizada en instituciones financieras para análisis de riesgo de crédito.

---

# 🧠 Problema de Negocio

Instituciones financieras enfrentan constantemente el desafío de:

* Aprobar buenos clientes
* Reducir pérdidas por default
* Evitar rechazos innecesarios
* Equilibrar crecimiento y riesgo

Tomar decisiones manuales puede generar:

* Inconsistencias
* Subjetividad
* Lentitud operacional
* Aumento de riesgo financiero

El sistema propuesto automatiza este proceso mediante un modelo de Machine Learning combinado con reglas de negocio.

---

# 🏗️ Arquitectura del Proyecto

```text
.
├── app/
│   └── styles.py
│
├── data/
│   └── datasets
│
├── models/
│   └── modelo_entrenado.pkl
│
├── src/
│   ├── loader.py
│   ├── policy.py
│   ├── preprocessing.py
│   ├── training.py
│   └── metrics.py
│
├── sistema_riesgo_credito.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Tecnologías Utilizadas

| Tecnología      | Uso                            |
| --------------- | ------------------------------ |
| Python          | Desarrollo del proyecto        |
| Pandas          | Manipulación de datos          |
| Scikit-Learn    | Modelado de Machine Learning   |
| ScorecardPy     | Transformación WoE y Scorecard |
| Plotly          | Visualizaciones interactivas   |
| Streamlit       | Aplicación web interactiva     |
| Joblib / Pickle | Persistencia del modelo        |

---

# 📊 Dataset

El proyecto utiliza el dataset público **German Credit Dataset**, ampliamente utilizado en estudios de riesgo crediticio y Machine Learning aplicado a finanzas.

El conjunto de datos contiene información histórica de clientes utilizada para evaluar comportamiento crediticio y probabilidad de incumplimiento.

Variables utilizadas:

* Edad
* Ocupación
* Tipo de vivienda
* Cuenta de ahorro
* Cuenta corriente
* Finalidad del crédito
* Duración del crédito
* Monto solicitado

Variable objetivo:

* Riesgo crediticio (Bueno / Malo)

---

# 🔄 Metodología de Desarrollo

## 1. Análisis Exploratorio de Datos (EDA)

Se realizó un análisis exploratorio para:

* Identificar distribución de variables
* Detectar valores faltantes
* Evaluar correlaciones
* Analizar perfiles de riesgo
* Comprender patrones de default

---

## 2. Preprocesamiento

Etapas aplicadas:

* Limpieza de datos
* Conversión de variables categóricas
* Tratamiento de inconsistencias
* Transformación WoE (Weight of Evidence)
* Selección de variables relevantes

La transformación WoE fue utilizada para:

* Mejorar interpretabilidad
* Mantener estabilidad estadística
* Simular prácticas utilizadas en modelos bancarios reales

---

## 3. Entrenamiento del Modelo

Se evaluaron diferentes algoritmos de clasificación para identificar el mejor desempeño.

Métricas analizadas:

* Accuracy
* Precision
* Recall
* F1 Score
* AUC
* Gini
* KS

El modelo final fue seleccionado considerando principalmente los mejores resultados en las métricas:

* Gini
* KS
* AUC

Además, también se evaluaron:

* Capacidad predictiva
* Balance entre precisión y riesgo
* Interpretabilidad
* Robustez estadística

---

## 4. Generación del Score

Las probabilidades generadas por el modelo fueron convertidas en un score crediticio.

El sistema clasifica clientes en segmentos:

| Segmento    | Perfil            |
| ----------- | ----------------- |
| TOP PRIME   | Riesgo muy bajo   |
| SUPER PRIME | Riesgo bajo       |
| PRIME       | Buen perfil       |
| STANDARD    | Perfil moderado   |
| NEAR PRIME  | Riesgo controlado |
| REVIEW      | Requiere análisis |
| SUBPRIME    | Riesgo elevado    |

---

## 5. Política de Crédito

Además del modelo de Machine Learning, se implementó una política de negocio con reglas para:

* Aprobación automática
* Revisión manual
* Rechazo automático
* Definición de límite sugerido

Factores considerados:

* Score final
* Probabilidad de incumplimiento
* Perfil financiero
* Ahorro
* Liquidez
* Situación laboral
* Vivienda

---

## 6. Monitoreo de Estabilidad (PSI)

El proyecto incluye monitoreo mediante PSI (Population Stability Index).

Objetivo:

* Detectar cambios en el perfil de clientes
* Identificar data drift
* Monitorear estabilidad del modelo en producción

Interpretación:

| PSI         | Interpretación |
| ----------- | -------------- |
| < 0.10      | Estable        |
| 0.10 – 0.25 | Alerta         |
| > 0.25      | Inestable      |

---

# 🖥️ Aplicación Interactiva

La solución fue desplegada en Streamlit con una interfaz interactiva.

Funcionalidades:

✅ Simulación de solicitudes de crédito
✅ Score automático
✅ Probabilidad de riesgo
✅ Segmentación de clientes
✅ Límite sugerido
✅ Indicador visual de riesgo
✅ Métricas del modelo
✅ Matriz de confusión
✅ Monitoreo PSI

---

# 📈 Resultados del Modelo

El modelo alcanzó resultados consistentes para apoyo a decisiones crediticias.

Principales indicadores evaluados:

* Accuracy
* Precision
* Recall
* F1 Score
* AUC
* Gini
* KS

El sistema logró identificar patrones de riesgo relevantes y generar decisiones más estructuradas y consistentes.

---

# 🚀 Impacto del Proyecto

La solución permite:

* Automatizar evaluaciones de crédito
* Reducir subjetividad operacional
* Mejorar consistencia de decisiones
* Disminuir exposición al riesgo
* Optimizar análisis de clientes
* Simular procesos reales de instituciones financieras

---

# 📷 Vista de la Aplicación

## Simulación de Crédito

* Entrada de datos del cliente
* Evaluación automática
* Score crediticio
* Probabilidad de default
* Límite sugerido

## Desempeño del Modelo

* Métricas principales
* Matriz de confusión
* Evaluación estadística

## Estabilidad del Modelo

* PSI
* Interpretación de estabilidad
* Monitoreo de drift

---

# ▶️ Cómo Ejecutar el Proyecto

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

---

## 2. Entrar al proyecto

```bash
cd nombre_del_proyecto
```

---

## 3. Crear ambiente virtual

```bash
python -m venv venv
```

---

## 4. Activar ambiente virtual

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 6. Ejecutar la aplicación

```bash
streamlit run sistema_riesgo_credito.py
```

---

## 📌 Posibles Mejoras Futuras

- Incorporación de nuevas variables financieras como: Ingresos, Historial bancario, Nivel de endeudamiento, Relación ingreso/deuda.
- Monitoreo continuo del modelo
- Optimización de políticas de crédito
- Reentrenamiento automático
- Modelos avanzados de scoring

---

# 👩‍💻 Autor

**Fernanda Pavan**

Proyecto desarrollado como portfolio de Data Science aplicado a Riesgo de Crédito y Machine Learning.

---

# 📄 Licencia

Este proyecto tiene fines educativos y demostrativos.



