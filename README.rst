\==========
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

* **Licencia:** Apache 2.0
* **Documentación:** [https://smartfood.readthedocs.io](https://smartfood.readthedocs.io)

## Descripción

**SmartFood** es un bot de Telegram que genera *recomendaciones de recetas* personalizadas a partir de los **ingredientes** que el usuario:

* introduce manualmente en el chat, **o**
* envía mediante una **foto** (detectados por YOLOv8).

El proyecto forma parte del Trabajo Fin de Grado *«Nutritional Recommendation from Images»* y está desplegado **completamente en Google Cloud** con una arquitectura *serverless* **Cloud Functions Gen2 + Pub/Sub**.

Arquitectura

```

::

   Telegram  ─▶  Webhook  ─┐
                           │   Pub/Sub: ingredientes_detectados  ─▶  Recomendador  ─▶  Pub/Sub: mensaje_respuesta  ─▶  Mensajero  ─▶  Telegram
   (foto opc.)             │
   └──────────────▶  Detector (YOLOv8) ────────────────────────────────────────────────────────────────────────────┘

* **Webhook** (HTTP) ‑ Guarda preferencias en Firestore y publica la lista de ingredientes.
* **Detector** (HTTP, opcional) ‑ YOLOv8‑n *best.pt* detecta ingredientes en la imagen.
* **Recomendador** (Pub/Sub) ‑ PyKEEN + Grafo de Conocimiento: calcula los mejores platos según filtros multi‑nutriente.
* **Mensajero** (Pub/Sub) ‑ Formatea la respuesta y la envía de vuelta al chat.

El *pipeline* es **100 % asíncrono**: cada función escala de manera independiente y sólo se factura por invocación.

Objetivos del proyecto
----------------------

* Detectar ingredientes en imágenes con Transfer Learning (**YOLOv8**).
* Recomendar platos equilibrados usando un **Grafo de Conocimiento** y **PyKEEN**.
* Permitir que el usuario configure preferencias nutricionales (calorías, grasas, azúcares, etc.) y el modo de entrada (texto o foto).
* Desplegar la solución en la nube minimizando *vendor‑lock‑in* y costes.

Estructura del código
---------------------

::

   SmartFood-pubsub/
   ├─ deploy.sh            # Script de despliegue (gcloud)
   ├─ webhook/             # Cloud Function – Telegram ↔ Pub/Sub
   ├─ recomendador/        # Cloud Function – KG inference (PyKEEN)
   ├─ mensajero/           # Cloud Function – Pub/Sub ↔ Telegram
   ├─ detector/            # Cloud Function – YOLOv8 inference (opcional)
   └─ notebooks/           # Experimentos y prototipos (no se despliegan)

La carpeta **``SmartFood-pubsub``** es la que se sube a Google Cloud; los *notebooks* contienen los experimentos de I+D.

Requisitos
----------

* Python 3.10
* ``ultralytics`` (YOLOv8)   /  ``torch >=2.1, <2.5``
* ``pykeen==1.10.2``
* ``pandas``, ``google‑cloud‑firestore``, ``google‑cloud‑pubsub``, ``google‑cloud‑storage``, ``functions‑framework``
* ``gcloud`` CLI con permisos **Cloud Functions + Pub/Sub + Firestore**.

Instalación local (desarrollo)
------------------------------

.. code-block:: bash

   git clone https://github.com/Jmartinezc-rgb/smartfood.git
   cd smartfood/SmartFood-pubsub
   python -m venv .venv && source .venv/bin/activate
   pip install -r recomendador/requirements.txt

Variables de entorno mínimas::

   BOT_TOKEN       # token del bot de Telegram
   MODEL_BUCKET    # bucket con model.pkl y triples.csv

Despliegue en Google Cloud
--------------------------

.. code-block:: bash

   ./deploy.sh   # crea topics, sube código y fija el webhook

El script ``deploy.sh``:

* Crea los topics **``ingredientes_detectados``** y **``mensaje_respuesta``**.
* Despliega las cuatro Cloud Functions Gen2.
* Carga las variables de entorno necesarias.
* Registra el webhook con Telegram.

Modelo YOLOv8
-------------

El detector se entrenó durante **100 epochs** sobre un subconjunto de 80 ingredientes; el mejor peso es ``best.pt`` (≈52 MB).

Publicarlo en el bucket::

   gsutil cp runs/detect/yolov8_ingredientes/weights/best.pt \
          gs://smartfood-models/yolo/best.pt

Luego desplegar la función *detector* pasando ``YOLO_MODEL_BLOB=yolo/best.pt``.

Dataset
-------

* **Detección:** conjunto propio de imágenes etiquetadas manualmente.
* **Recomendación:** triples en ``kge/new_triplets20_optimized.csv`` e **embedding** entrenado con PyKEEN.

Características destacadas
--------------------------

* Detección en **≈127 ms/img** (CPU en Cloud Run) con YOLOv8‑n.
* Recomendador multi‑nutriente: suma scores relacionales filtrando calorías, grasas, etc.
* Arquitectura *event‑driven* sin servidores, pago por invocación.
* Fácil de extender con nuevos filtros, modelos o canales de chat.

Créditos
--------

Creado con ``Cookiecutter``_ y la plantilla ``audreyr/cookiecutter‑pypackage``_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _audreyr/cookiecutter‑pypackage: https://github.com/audreyr/cookiecutter-pypackage

```
