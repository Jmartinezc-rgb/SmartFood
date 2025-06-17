\=========
SmartFood
=========

.. image:: [https://img.shields.io/pypi/v/smartfood.svg](https://img.shields.io/pypi/v/smartfood.svg)
\:target: [https://pypi.python.org/pypi/smartfood](https://pypi.python.org/pypi/smartfood)

.. image:: [https://img.shields.io/travis/Jmartinezc-rgb/smartfood.svg](https://img.shields.io/travis/Jmartinezc-rgb/smartfood.svg)
\:target: [https://travis-ci.com/Jmartinezc-rgb/smartfood](https://travis-ci.com/Jmartinezc-rgb/smartfood)

.. image:: [https://readthedocs.org/projects/smartfood/badge/?version=latest](https://readthedocs.org/projects/smartfood/badge/?version=latest)
\:target: [https://smartfood.readthedocs.io/en/latest/?version=latest](https://smartfood.readthedocs.io/en/latest/?version=latest)
\:alt: Documentation Status

# Recomendaciones nutricionales a partir de imágenes

* Software libre: Licencia Apache 2.0
* Documentación: [https://smartfood.readthedocs.io](https://smartfood.readthedocs.io)

## Descripción

**SmartFood** es un bot de Telegram que genera *recomendaciones de recetas* personalizadas a partir de **ingredientes detectados en una foto** o introducidos manualmente por el usuario. El proyecto forma parte del Trabajo Fin de Grado *“Nutritional Recommendation from Images”*.

En esta iteración se ha desplegado la solución **completamente en Google Cloud** usando una arquitectura *serverless* basada en **Cloud Functions + Pub/Sub**:

```
Telegram ▶ Webhook ─┐                  ┌─▶ Mensajero ▶ Telegram
                    │                  │
              Pub/Sub topic ▶ Recomendador
                    │
          YOLOv8 Detector (opcional)
```

1. **Webhook** (HTTP)   → Guarda preferencias en Firestore y publica los ingredientes.
2. **Recomendador** (Pub/Sub)   → PyKEEN + KG: infiere recetas con filtros multi‑nutriente.
3. **Mensajero** (Pub/Sub)   → Formatea la respuesta y la envía a Telegram.
4. **Detector** (HTTP, opcional)   → YOLOv8 "best.pt" detecta ingredientes en imágenes.

El *pipeline* es 100 % asíncrono; cada función escala de forma independiente.

## Objetivos del proyecto

* Detectar ingredientes en imágenes mediante Transfer Learning (YOLOv8).
* Recomendar platos equilibrados usando un Grafo de Conocimiento y PyKEEN.
* Permitir que el usuario seleccione sus preferencias nutricionales (calorías, grasas, azúcares, etc.) y el modo de entrada (texto o foto).
* Desplegar la solución en la nube minimizando el *vendor lock‑in* y los costes.

## Estructura del código

```
SmartFood-pubsub/
├─ deploy.sh            # Script de despliegue (gcloud)
├─ webhook/             # Cloud Function – Telegram ↔ Pub/Sub
├─ recomendador/        # Cloud Function – PyKEEN KG inference
├─ mensajero/           # Cloud Function – Pub/Sub ↔ Telegram
├─ detector/            # (opcional) Cloud Function – YOLOv8 inference
└─ notebooks/           # Experimentos y prototipos (no se despliegan)
```

La carpeta **`SmartFood-pubsub`** es la que se sube a Google Cloud. Los *notebooks* se conservan para replicar los experimentos de entrenamiento y análisis.

## Requisitos

* Python 3.10
* `ultralytics` (YOLOv8) / `torch>=2.1, <2.5`
* `pykeen==1.10.2`, `pandas`, `google-cloud-firestore`, `google-cloud-pubsub`, `google-cloud-storage`, `functions-framework`
* `gcloud CLI` configurado con un proyecto y cuenta de servicio con permisos **Cloud Functions + Pub/Sub + Firestore**.

## Instalación local (desarrollo)

.. code-block:: bash

git clone [https://github.com/Jmartinezc-rgb/smartfood.git](https://github.com/Jmartinezc-rgb/smartfood.git)
cd smartfood/SmartFood-pubsub
python -m venv .venv && source .venv/bin/activate
pip install -r recomendador/requirements.txt

Variables de entorno mínimas:

* `BOT_TOKEN`         → token del bot de Telegram.
* `MODEL_BUCKET`      → bucket con *model.pkl* y *triples.csv*.

## Despliegue en Google Cloud

Se automatiza con `deploy.sh`:

.. code-block:: bash

./deploy.sh   # crea topics, sube código y fija el webhook

El script:

* Crea los topics **`ingredientes_detectados`** y **`mensaje_respuesta`**.
* Despliega cada función Gen2 con **gcloud functions deploy**.
* Sube las variables de entorno necesarias.
* Registra el webhook de Telegram.

## Modelo YOLOv8

El detector se entrenó durante **100 epochs** sobre un subconjunto de 80 ingredientes — `best.pt` (≈52 MB). Para publicarlo:

.. code-block:: bash

gsutil cp runs/detect/yolov8\_ingredientes/weights/best.pt&#x20;
gs\://smartfood-models/yolo/best.pt

Luego desplegar la función `detector/` pasándole `YOLO_MODEL_BLOB=yolo/best.pt`.

# Dataset

*Detección*: conjunto propio + imágenes etiquetadas manualmente.

*Recomendación*: triples en `kge/new_triplets20_optimized.csv` y grafo entrenado con PyKEEN.

## Características destacadas

* Detección de ingredientes en **127 ms/img** (CPU en Cloud Run) con YOLOv8‑n.
* Recomendador explica preferencias multi‑nutriente sumando scores relacionales.
* Arquitectura *event‑driven* sin servidores; sólo se paga por invocación.
* Fácil de extender (nuevos filtros, nuevos modelos, nuevos canales de chat).

## Créditos

Creado con `Cookiecutter`\_ y la plantilla `audreyr/cookiecutter‑pypackage`\_.

.. \_Cookiecutter: [https://github.com/audreyr/cookiecutter](https://github.com/audreyr/cookiecutter)
.. \_audreyr/cookiecutter‑pypackage: [https://github.com/audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
