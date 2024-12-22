Документация NetGuardian
=====================

.. toctree::
   :maxdepth: 2
   :caption: Содержание:

   installation
   quickstart
   architecture
   configuration
   modules/index
   api/index
   deployment
   security
   contributing
   changelog

О проекте NetGuardian
------------------

NetGuardian - это мощная распределенная система мониторинга сети, разработанная для обеспечения комплексного наблюдения за сетевой инфраструктурой в реальном времени.

Основные возможности
------------------

* Мониторинг сетевого трафика в реальном времени
* Обнаружение вторжений и аномалий с использованием ML
* Анализ производительности сети
* Шифрование всех коммуникаций
* Веб-интерфейс для управления и мониторинга
* Интеграция с Prometheus для метрик
* Распределенная архитектура с агентами

Системные требования
-----------------

* Python 3.8+
* PostgreSQL 12+
* Redis 6+ (для кэширования)
* Elasticsearch 7.x (для логов)
* Kafka 2.8+ (для очередей сообщений)

Быстрый старт
-----------

.. code-block:: bash

   # Клонирование репозитория
   git clone https://github.com/forekz/netguardian.git
   cd netguardian

   # Установка зависимостей
   pip install -r requirements.txt

   # Запуск сервера
   python server/core/server.py

Поддержка
--------

* GitHub: https://github.com/forekz/netguardian
* Email: forekz@example.com
* Telegram: @forekz

Автор
----

:Автор: forekz
:GitHub: https://github.com/forekz
:Лицензия: MIT

Индексы и таблицы
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 