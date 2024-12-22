Руководство по установке
=====================

Это руководство поможет вам установить и настроить NetGuardian в вашей среде.

Предварительные требования
------------------------

Перед установкой NetGuardian убедитесь, что у вас установлены следующие компоненты:

* Python 3.8 или выше
* pip (установщик пакетов Python)
* PostgreSQL 12 или выше
* Redis 6 или выше
* Elasticsearch 7.x
* Apache Kafka 2.8+
* Docker (опционально, для контейнеризации)

Системные требования
------------------

Минимальные системные требования для запуска NetGuardian:

* CPU: 2 ядра
* RAM: 4GB
* Дисковое пространство: 20GB
* Сеть: 100Mbps

Шаги установки
------------

1. Клонирование репозитория
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/forekz/netguardian.git
   cd netguardian

2. Создание виртуального окружения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate

3. Установка зависимостей
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Для разработки

4. Настройка базы данных
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Создание базы данных PostgreSQL
   createdb netguardian

   # Настройка подключения к базе данных
   cp config.example.yaml config.yaml
   # Отредактируйте config.yaml, указав ваши учетные данные

5. Настройка внешних сервисов
~~~~~~~~~~~~~~~~~~~~~~~~~~

Настройка Redis
^^^^^^^^^^^^^

.. code-block:: bash

   # Установка Redis
   sudo apt-get install redis-server
   sudo systemctl start redis

Настройка Elasticsearch
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Установка Elasticsearch
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.14.0-amd64.deb
   sudo dpkg -i elasticsearch-7.14.0-amd64.deb
   sudo systemctl start elasticsearch

Настройка Kafka
^^^^^^^^^^^^

.. code-block:: bash

   # Загрузка и распаковка Kafka
   wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz
   tar xzf kafka_2.13-2.8.0.tgz
   cd kafka_2.13-2.8.0

   # Запуск Zookeeper
   bin/zookeeper-server-start.sh config/zookeeper.properties

   # Запуск Kafka
   bin/kafka-server-start.sh config/server.properties

6. Инициализация приложения
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Генерация ключей шифрования
   python scripts/generate_keys.py

   # Инициализация базы данных
   python scripts/init_db.py

   # Создание администратора
   python scripts/create_admin.py

7. Запуск приложения
~~~~~~~~~~~~~~~~~

Сервер
^^^^^^

.. code-block:: bash

   # Запуск сервера
   python server/core/server.py

Агенты
^^^^^^

.. code-block:: bash

   # Запуск агента
   python agents/common/base_agent.py

Веб-интерфейс
^^^^^^^^^^^

.. code-block:: bash

   # Запуск веб-интерфейса
   python web_ui/app.py

Установка через Docker
-------------------

Альтернативно, вы можете использовать Docker Compose для запуска NetGuardian:

.. code-block:: bash

   # Сборка и запуск контейнеров
   docker-compose up -d

   # Просмотр логов
   docker-compose logs -f

Устранение неполадок
-----------------

Распространенные проблемы
^^^^^^^^^^^^^^^^^^^^^

1. Проблемы с подключением к базе данных
   
   * Проверьте статус службы PostgreSQL
   * Проверьте учетные данные в config.yaml
   * Убедитесь, что PostgreSQL принимает подключения

2. Ошибки подключения к Redis
   
   * Проверьте статус службы Redis
   * Проверьте настройки подключения к Redis
   * Убедитесь, что Redis не ограничен по памяти

3. Проблемы с Elasticsearch
   
   * Проверьте статус службы Elasticsearch
   * Проверьте здоровье кластера
   * Проверьте свободное место на диске

4. Проблемы с подключением к Kafka
   
   * Убедитесь, что Zookeeper запущен
   * Проверьте статус брокера Kafka
   * Проверьте конфигурацию топиков

Следующие шаги
------------

После установки вам следует:

1. Завершить настройку в руководстве :doc:`configuration`
2. Следовать руководству по быстрому старту :doc:`quickstart`
3. Ознакомиться с рекомендациями по безопасности :doc:`security`
4. Настроить мониторинг и оповещения

Для разработчиков также см.:

* :doc:`contributing`
* :doc:`api/index`

Автор
----

:Автор: forekz
:GitHub: https://github.com/forekz
:Email: forekz@example.com 