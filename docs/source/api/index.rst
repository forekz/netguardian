Справочник по API
===============

NetGuardian предоставляет REST API для интеграции с внешними системами.

Аутентификация
------------

Все API-запросы требуют аутентификации с использованием JWT токена:

.. code-block:: bash

   curl -H "Authorization: Bearer <your_token>" https://api.netguardian.com/v1/metrics

Конечные точки
------------

Агенты
^^^^^

.. http:get:: /api/v1/agents

   Получение списка агентов.

   **Пример запроса**:

   .. sourcecode:: http

      GET /api/v1/agents HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "agents": [
          {
            "id": "agent_123",
            "hostname": "server1.example.com",
            "status": "active",
            "last_seen": "2024-01-22T15:30:00Z",
            "metrics": {
              "cpu_usage": 45.2,
              "memory_usage": 78.5
            }
          }
        ]
      }

Метрики
^^^^^^

.. http:get:: /api/v1/metrics

   Получение метрик системы.

   :query string timeframe: Временной интервал (1h, 24h, 7d)
   :query string agent_id: ID агента (опционально)
   :query string metric_type: Тип метрики (cpu, memory, network)

   **Пример запроса**:

   .. sourcecode:: http

      GET /api/v1/metrics?timeframe=24h&metric_type=cpu HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "metrics": {
          "cpu_usage": [
            {
              "timestamp": "2024-01-22T15:00:00Z",
              "value": 45.2
            }
          ]
        }
      }

Оповещения
^^^^^^^^

.. http:get:: /api/v1/alerts

   Получение списка оповещений.

   :query integer page: Номер страницы
   :query integer per_page: Количество элементов на странице
   :query integer min_severity: Минимальный уровень критичности

   **Пример запроса**:

   .. sourcecode:: http

      GET /api/v1/alerts?page=1&per_page=50&min_severity=7 HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "total": 125,
        "page": 1,
        "per_page": 50,
        "alerts": [
          {
            "id": "alert_456",
            "type": "anomaly",
            "severity": 8,
            "timestamp": "2024-01-22T15:30:00Z",
            "description": "Обнаружена подозрительная сетевая активность"
          }
        ]
      }

.. http:post:: /api/v1/alerts

   Создание нового оповещения.

   **Пример запроса**:

   .. sourcecode:: http

      POST /api/v1/alerts HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>
      Content-Type: application/json

      {
        "type": "anomaly",
        "severity": 8,
        "description": "Обнаружена подозрительная сетевая активность",
        "source": {
          "agent_id": "agent_123",
          "ip": "192.168.1.100"
        }
      }

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": "alert_789",
        "status": "created"
      }

Конфигурация
^^^^^^^^^^

.. http:get:: /api/v1/config

   Получение конфигурации системы.

   **Пример запроса**:

   .. sourcecode:: http

      GET /api/v1/config HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "monitoring": {
          "packet_capture": {
            "enabled": true,
            "interface": "any"
          },
          "system": {
            "interval": 5
          }
        }
      }

.. http:put:: /api/v1/config

   Обновление конфигурации системы.

   **Пример запроса**:

   .. sourcecode:: http

      PUT /api/v1/config HTTP/1.1
      Host: api.netguardian.com
      Authorization: Bearer <your_token>
      Content-Type: application/json

      {
        "monitoring": {
          "packet_capture": {
            "enabled": true,
            "interface": "eth0"
          }
        }
      }

   **Пример ответа**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "updated"
      }

WebSocket API
-----------

Обновления в реальном времени
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

   const socket = io('wss://api.netguardian.com', {
     auth: {
       token: 'your_token'
     }
   });

   // Подписка на обновления
   socket.on('update', (data) => {
     console.log('Получено обновление:', data);
   });

   // Подписка на оповещения
   socket.on('alert', (alert) => {
     console.log('Новое оповещение:', alert);
   });

Обработка ошибок
-------------

API использует стандартные HTTP коды состояния:

* 200 - OK
* 201 - Created (Создано)
* 400 - Bad Request (Неверный запрос)
* 401 - Unauthorized (Не авторизован)
* 403 - Forbidden (Запрещено)
* 404 - Not Found (Не найдено)
* 500 - Internal Server Error (Внутренняя ошибка сервера)

Пример ошибки:

.. sourcecode:: http

   HTTP/1.1 400 Bad Request
   Content-Type: application/json

   {
     "error": {
       "code": "invalid_parameter",
       "message": "Неверный параметр timeframe"
     }
   }

Ограничение запросов
-----------------

API имеет ограничение на количество запросов:

* 1000 запросов в час для базового плана
* 5000 запросов в час для pro плана
* Без ограничений для enterprise плана

При превышении лимита возвращается код 429 Too Many Requests:

.. sourcecode:: http

   HTTP/1.1 429 Too Many Requests
   Content-Type: application/json
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 0
   X-RateLimit-Reset: 1643734800

   {
     "error": {
       "code": "rate_limit_exceeded",
       "message": "Превышен лимит запросов. Пожалуйста, повторите позже."
     }
   }

Поддержка
--------

При возникновении проблем с API, пожалуйста, обращайтесь:

* GitHub Issues: https://github.com/forekz/netguardian/issues
* Email: forekz@example.com
* Telegram: @forekz

Автор
----

:Автор: forekz
:GitHub: https://github.com/forekz
:Email: forekz@example.com
:Лицензия: MIT 