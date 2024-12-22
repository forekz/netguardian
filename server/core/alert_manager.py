import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import aiohttp
import yaml
from datetime import datetime
import asyncio
from kafka import KafkaProducer

class AlertManager:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger('AlertManager')
        self.alert_history = []
        self.kafka_producer = self._setup_kafka()
        
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['alerts']
            
    def _setup_kafka(self) -> KafkaProducer:
        """Настройка Kafka продюсера"""
        return KafkaProducer(
            bootstrap_servers=self.config.get('kafka_servers', ['localhost:9092']),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    async def process_alert(self, alert_data: Dict):
        """Обработка оповещения"""
        severity = self._calculate_severity(alert_data)
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        alert = {
            'id': alert_id,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'type': alert_data.get('type', 'unknown'),
            'description': alert_data.get('description', ''),
            'source': alert_data.get('source', {}),
            'data': alert_data
        }
        
        self.alert_history.append(alert)
        
        # Отправка в Kafka
        self.kafka_producer.send('alerts', alert)
        
        # Проверка пороговых значений и отправка уведомлений
        if severity >= self.config['thresholds'].get('notification_severity', 7):
            await self._send_notifications(alert)
            
    def _calculate_severity(self, alert_data: Dict) -> int:
        """Расчет уровня критичности оповещения"""
        base_severity = 5
        
        # Повышаем уровень для определенных типов событий
        if alert_data.get('type') == 'anomaly':
            base_severity += 2
            
        # Проверяем превышение пороговых значений
        thresholds = self.config['thresholds']
        if alert_data.get('cpu_percent', 0) > thresholds.get('cpu_percent', 90):
            base_severity += 1
        if alert_data.get('memory_percent', 0) > thresholds.get('memory_percent', 85):
            base_severity += 1
        if alert_data.get('suspicious_connections', 0) > thresholds.get('suspicious_connections', 100):
            base_severity += 2
            
        return min(base_severity, 10)  # Максимальный уровень - 10
        
    async def _send_notifications(self, alert: Dict):
        """Отправка уведомлений"""
        tasks = []
        
        if self.config['notifications']['email']['enabled']:
            tasks.append(self._send_email_alert(alert))
            
        if self.config['notifications']['slack']['enabled']:
            tasks.append(self._send_slack_alert(alert))
            
        await asyncio.gather(*tasks)
        
    async def _send_email_alert(self, alert: Dict):
        """Отправка уведомления по email"""
        email_config = self.config['notifications']['email']
        
        msg = MIMEMultipart()
        msg['Subject'] = f"NetGuardian Alert: {alert['type']} (Severity: {alert['severity']})"
        msg['From'] = email_config['username']
        msg['To'] = ', '.join(email_config['recipients'])
        
        body = self._format_alert_email(alert)
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            
    async def _send_slack_alert(self, alert: Dict):
        """Отправка уведомления в Slack"""
        slack_config = self.config['notifications']['slack']
        
        message = self._format_slack_message(alert)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    slack_config['webhook_url'],
                    json={'text': message}
                ) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to send Slack alert: {await response.text()}"
                        )
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")
            
    def _format_alert_email(self, alert: Dict) -> str:
        """Форматирование email сообщения"""
        return f"""
        <html>
            <body>
                <h2>NetGuardian Alert</h2>
                <p><strong>Type:</strong> {alert['type']}</p>
                <p><strong>Severity:</strong> {alert['severity']}/10</p>
                <p><strong>Time:</strong> {alert['timestamp']}</p>
                <p><strong>Description:</strong> {alert['description']}</p>
                <h3>Details:</h3>
                <pre>{json.dumps(alert['data'], indent=2)}</pre>
            </body>
        </html>
        """
        
    def _format_slack_message(self, alert: Dict) -> str:
        """Форматирование Slack сообщения"""
        severity_emoji = "🔴" if alert['severity'] >= 8 else "🟡" if alert['severity'] >= 5 else "🟢"
        
        return f"""
        {severity_emoji} *NetGuardian Alert*
        *Type:* {alert['type']}
        *Severity:* {alert['severity']}/10
        *Time:* {alert['timestamp']}
        *Description:* {alert['description']}
        ```
        {json.dumps(alert['data'], indent=2)}
        ```
        """ 