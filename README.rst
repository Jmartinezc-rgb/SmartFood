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
* Documentation: https://smartfood.readthedocs.io

Description
-----------

SmartFood is a Telegram bot that provides nutritional recommendations based on images of food captured by a mobile device. This project is part of a Bachelor’s Thesis (TFG) titled "Nutritional Recommendation from Images". The main objective is to develop a system that offers nutritional information and/or recommendations (e.g., estimated calories or recipes) by processing food images. 

The bot serves as the user interface, enabling interaction through Telegram by exchanging messages and photos.

Project Objectives
------------------

The system is designed to:
- Offer recommendations and nutritional information based on food images.
- Use Transfer Learning on pretrained architectures to identify foods.
- Integrate with messaging systems (Telegram API) for real-time communication with users.
- Explore production deployment using container orchestration tools like Docker or Kubernetes.

For more details, refer to the TFG project document included in the repository.

Code Structure
--------------

### Main Files
- `nutri_bot.py`: Main script of the bot, including interaction logic and placeholder sections for integrating the Transfer Learning model.

Requirements
------------

This project requires:
- Python 3.7 or higher
- `aiogram <https://pypi.org/project/aiogram/>`_
- `Pillow <https://pypi.org/project/Pillow/>`_
- `Torch <https://pypi.org/project/torch/>`_ (for future model integration)

Installation
------------

Install the necessary dependencies by running the following command:

.. code-block:: bash

   pip install -r requirements.txt

Features
--------

- Nutritional information extraction from food images (future development).
- Real-time user interaction through Telegram API.
- Potential integration with Transfer Learning models for food recognition.
- Deployment-ready structure with Docker and Kubernetes support (optional).

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
