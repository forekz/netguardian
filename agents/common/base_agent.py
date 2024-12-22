import asyncio
import platform
import psutil
import logging
from datetime import datetime
from typing import Dict, Any
from cryptography.fernet import Fernet
import aiohttp
import scapy.all as scapy

class BaseAgent:
    def __init__(self, server_url: str, encryption_key: bytes):
        self.server_url = server_url
        self.fernet = Fernet(encryption_key)
        self.system_info = self._collect_system_info()
        self.logger = self._setup_logging()
        self.packet_buffer = asyncio.Queue()
        self.is_running = False
        
    def _setup_logging(self):
        """Настройка логирования для агента"""
        logger = logging.getLogger(f'NetGuardian-Agent-{platform.node()}')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f'agent_{platform.node()}.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def _collect_system_info(self) -> Dict[str, Any]:
        """Сбор информации о системе"""
        return {
            'hostname': platform.node(),
            'os': platform.system(),
            'os_version': platform.version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'interfaces': scapy.get_if_list()
        }
        
    async def start(self):
        """Запуск агента"""
        self.is_running = True
        self.logger.info("Starting NetGuardian agent")
        
        tasks = [
            self._network_monitor(),
            self._system_monitor(),
            self._send_data_loop()
        ]
        
        await asyncio.gather(*tasks)
        
    async def _network_monitor(self):
        """Мониторинг сетевой активности"""
        def packet_callback(packet):
            if self.is_running:
                asyncio.run_coroutine_threadsafe(
                    self.packet_buffer.put({
                        'timestamp': datetime.now().isoformat(),
                        'packet_summary': packet.summary(),
                        'protocol': packet.name if hasattr(packet, 'name') else 'unknown',
                        'size': len(packet)
                    }), 
                    asyncio.get_event_loop()
                )
        
        # За��уск сниффера пакетов в отдельном потоке
        scapy.sniff(prn=packet_callback, store=0)
        
    async def _system_monitor(self):
        """Мониторинг системных ресурсов"""
        while self.is_running:
            system_stats = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict()
            }
            
            await self.packet_buffer.put({
                'type': 'system_stats',
                'data': system_stats
            })
            
            await asyncio.sleep(5)
            
    async def _send_data_loop(self):
        """Отправка данных на сервер"""
        async with aiohttp.ClientSession() as session:
            while self.is_running:
                try:
                    data = await self.packet_buffer.get()
                    encrypted_data = self.fernet.encrypt(str(data).encode())
                    
                    async with session.post(
                        f"{self.server_url}/data",
                        data=encrypted_data
                    ) as response:
                        if response.status != 200:
                            self.logger.error(
                                f"Failed to send data: {await response.text()}"
                            )
                            
                except Exception as e:
                    self.logger.error(f"Error sending data: {str(e)}")
                    await asyncio.sleep(5)
                    
    def stop(self):
        """Остановка агента"""
        self.is_running = False
        self.logger.info("Stopping NetGuardian agent")

if __name__ == '__main__':
    # Пример использования
    ENCRYPTION_KEY = b'your-encryption-key-here'
    SERVER_URL = 'http://localhost:8080'
    
    agent = BaseAgent(SERVER_URL, ENCRYPTION_KEY)
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        agent.stop() 