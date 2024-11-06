=========
SmartFood
=========


.. image:: https://img.shields.io/pypi/v/smartfood.svg
        :target: https://pypi.python.org/pypi/smartfood

.. image:: https://img.shields.io/travis/Jmartinezc-rgb/smartfood.svg
        :target: https://travis-ci.com/Jmartinezc-rgb/smartfood

.. image:: https://readthedocs.org/projects/smartfood/badge/?version=latest
        :target: https://smartfood.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Nutritional Recommendation from Images


* Free software: Apache Software License 2.0
* Documentation: https://smartfood.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

# Bot de Telegram para Recomendación Nutricional a partir de Imágenes

Este proyecto forma parte del Trabajo de Fin de Grado (TFG) titulado "Recomendación nutricional a partir de imágenes". El objetivo principal es desarrollar un sistema que proporcione recomendaciones e información nutricional a partir de imágenes de alimentos capturadas con un dispositivo móvil. Este bot de Telegram sirve como interfaz de usuario, permitiendo la interacción a través de mensajes y fotos.

## Objetivo del Proyecto

El sistema está diseñado para:
- Ofrecer recomendaciones e información nutricional basada en imágenes de alimentos.
- Utilizar Transfer Learning sobre arquitecturas previamente entrenadas para identificar alimentos.
- Integrarse con sistemas de mensajería (API de Telegram) para facilitar una comunicación en tiempo real con los usuarios.
- Explorar la puesta en producción del sistema mediante herramientas de orquestación de contenedores como Docker o Kubernetes.

Para más detalles, consulta el anteproyecto de TFG (adjunto en el proyecto).

## Estructura del Código

### Archivos Principales
- `nutri_bot.py`: Script principal del bot, que incluye la lógica de interacción y las secciones comentadas para integrar el modelo de Transfer Learning en el futuro.

### Requisitos
Este proyecto requiere:
- Python 3.7 o superior
- [aiogram](https://pypi.org/project/aiogram/)
- [Pillow](https://pypi.org/project/Pillow/)
- [Torch](https://pypi.org/project/torch/) (para la integración del modelo en el futuro)

### Instalación de Dependencias

Instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt



