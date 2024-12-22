import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class PacketAnalyzer:
    def __init__(self):
        self.connection_history = defaultdict(list)
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        self.training_data = []
        
    def analyze_packet(self, packet_data: Dict) -> Tuple[bool, float, str]:
        """Анализ пакета на предмет аномалий"""
        features = self._extract_features(packet_data)
        self.training_data.append(features)
        
        # Переобучаем модель каждые 1000 пакетов
        if len(self.training_data) % 1000 == 0:
            self._retrain_model()
            
        # Определяем аномалию
        scaled_features = self.scaler.transform([features])
        anomaly_score = self.anomaly_detector.score_samples([features])[0]
        is_anomaly = anomaly_score < -0.5
        
        reason = self._get_anomaly_reason(packet_data, anomaly_score) if is_anomaly else ""
        
        return is_anomaly, anomaly_score, reason
        
    def _extract_features(self, packet_data: Dict) -> List[float]:
        """Извлечение признаков из пакета"""
        features = [
            packet_data.get('size', 0),
            len(packet_data.get('packet_summary', '')),
            self._get_protocol_score(packet_data.get('protocol', 'unknown')),
            self._get_time_score(packet_data.get('timestamp', '')),
            self._get_connection_frequency(packet_data)
        ]
        return features
        
    def _get_protocol_score(self, protocol: str) -> float:
        """Оценка риска протокола"""
        risk_scores = {
            'tcp': 1.0,
            'udp': 2.0,
            'icmp': 3.0,
            'unknown': 5.0
        }
        return risk_scores.get(protocol.lower(), 5.0)
        
    def _get_time_score(self, timestamp: str) -> float:
        """Оценка временного паттерна"""
        try:
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour
            # Подозрительное время (ночные часы) получает более высокий ��кор
            if 1 <= hour <= 5:
                return 3.0
            return 1.0
        except:
            return 5.0
            
    def _get_connection_frequency(self, packet_data: Dict) -> float:
        """Оценка частоты соединений"""
        key = f"{packet_data.get('src_ip', '')}-{packet_data.get('dst_ip', '')}"
        now = datetime.now()
        
        # Очистка старых записей
        self.connection_history[key] = [
            ts for ts in self.connection_history[key]
            if now - ts < timedelta(minutes=5)
        ]
        
        # Добавление нового соединения
        self.connection_history[key].append(now)
        
        # Возвращаем частоту соединений за последние 5 минут
        return len(self.connection_history[key])
        
    def _retrain_model(self):
        """Переобучение модели обнаружения аномалий"""
        if len(self.training_data) > 100:
            data_array = np.array(self.training_data)
            self.scaler.fit(data_array)
            scaled_data = self.scaler.transform(data_array)
            self.anomaly_detector.fit(scaled_data)
            
    def _get_anomaly_reason(self, packet_data: Dict, score: float) -> str:
        """Определение причины аномалии"""
        reasons = []
        
        if score < -0.8:
            reasons.append("Крайне подозрительный паттерн трафика")
            
        if self._get_protocol_score(packet_data.get('protocol', 'unknown')) > 3:
            reasons.append("Подозрительный протокол")
            
        if self._get_time_score(packet_data.get('timestamp', '')) > 2:
            reasons.append("Подозрительное время активности")
            
        if self._get_connection_frequency(packet_data) > 100:
            reasons.append("Высокая частота соединений")
            
        return " | ".join(reasons) if reasons else "Неизвестная аномалия" 