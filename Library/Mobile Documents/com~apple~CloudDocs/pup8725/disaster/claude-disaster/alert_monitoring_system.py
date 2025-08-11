#!/usr/bin/env python3
"""
Real-time Weather and Alert Monitoring System
Monitor weather conditions, government alerts, and provide early warnings
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import time
from dataclasses import dataclass

@dataclass
class Alert:
    alert_type: str
    severity: str
    title: str
    description: str
    area: str
    start_time: str
    end_time: str
    source: str

class AlertMonitoringSystem:
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self.init_database()
        self.api_endpoints = {
            "nws_alerts": "https://api.weather.gov/alerts/active",
            "weather": "https://api.openweathermap.org/data/2.5/weather",
            "forecast": "https://api.openweathermap.org/data/2.5/forecast"
        }
        self.severity_levels = {
            "Minor": 1,
            "Moderate": 2, 
            "Severe": 3,
            "Extreme": 4
        }
    
    def init_database(self):
        """Initialize SQLite database for alert tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE,
                alert_type TEXT NOT NULL,
                severity INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                area TEXT,
                start_time TEXT,
                end_time TEXT,
                source TEXT,
                acknowledged INTEGER DEFAULT 0,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                wind_direction REAL,
                conditions TEXT,
                visibility REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_config (
                id INTEGER PRIMARY KEY,
                location_lat REAL,
                location_lon REAL,
                location_name TEXT,
                weather_api_key TEXT,
                alert_threshold INTEGER DEFAULT 2,
                check_interval INTEGER DEFAULT 300,
                active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                min_severity INTEGER,
                notification_method TEXT,
                contact_info TEXT,
                enabled INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def set_location(self, latitude: float, longitude: float, 
                    location_name: str, weather_api_key: Optional[str] = None):
        """Set monitoring location and API configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO monitoring_config 
            (id, location_lat, location_lon, location_name, weather_api_key)
            VALUES (1, ?, ?, ?, ?)
        ''', (latitude, longitude, location_name, weather_api_key))
        
        conn.commit()
        conn.close()
    
    def fetch_nws_alerts(self, area: Optional[str] = None) -> List[Alert]:
        """Fetch active alerts from National Weather Service"""
        try:
            url = self.api_endpoints["nws_alerts"]
            if area:
                url += f"?area={area}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            alerts = []
            
            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                
                alert = Alert(
                    alert_type=properties.get("event", "Unknown"),
                    severity=properties.get("severity", "Unknown"),
                    title=properties.get("headline", ""),
                    description=properties.get("description", ""),
                    area=", ".join(properties.get("areaDesc", [])),
                    start_time=properties.get("onset", ""),
                    end_time=properties.get("expires", ""),
                    source="NWS"
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            print(f"Error fetching NWS alerts: {e}")
            return []
    
    def fetch_weather_data(self, api_key: str, lat: float, lon: float) -> Dict:
        """Fetch current weather conditions"""
        try:
            url = f"{self.api_endpoints['weather']}?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {}
    
    def analyze_weather_risks(self, weather_data: Dict) -> List[str]:
        """Analyze weather conditions for potential risks"""
        risks = []
        
        if not weather_data:
            return risks
        
        main = weather_data.get("main", {})
        wind = weather_data.get("wind", {})
        visibility = weather_data.get("visibility", 10000)
        
        # Temperature risks
        temp = main.get("temp", 70)
        if temp <= 32:
            risks.append("Freezing temperatures - pipe freeze risk")
        elif temp >= 100:
            risks.append("Extreme heat - heat exhaustion risk")
        elif temp <= 10:
            risks.append("Extreme cold - hypothermia risk")
        
        # Wind risks
        wind_speed = wind.get("speed", 0)
        if wind_speed >= 39:  # Gale force
            risks.append("High winds - structural damage risk")
        elif wind_speed >= 25:
            risks.append("Strong winds - travel hazard")
        
        # Visibility risks
        if visibility < 1000:  # Less than 0.6 miles
            risks.append("Poor visibility - travel dangerous")
        
        # Pressure risks (storms)
        pressure = main.get("pressure", 1013)
        if pressure < 980:
            risks.append("Low pressure system - severe weather possible")
        
        # Humidity risks
        humidity = main.get("humidity", 50)
        if humidity >= 90 and temp >= 80:
            risks.append("High heat index - heat illness risk")
        
        return risks
    
    def store_alert(self, alert: Alert) -> bool:
        """Store alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        severity_num = self.severity_levels.get(alert.severity, 2)
        alert_id = f"{alert.source}_{alert.alert_type}_{alert.start_time}"
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO alerts 
                (alert_id, alert_type, severity, title, description, area, 
                 start_time, end_time, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, alert.alert_type, severity_num, alert.title,
                  alert.description, alert.area, alert.start_time, 
                  alert.end_time, alert.source))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error storing alert: {e}")
            return False
        finally:
            conn.close()
    
    def get_active_alerts(self, min_severity: int = 2) -> List[Dict]:
        """Get active alerts above minimum severity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT * FROM alerts
            WHERE severity >= ?
            AND (end_time IS NULL OR end_time > ?)
            AND acknowledged = 0
            ORDER BY severity DESC, start_time DESC
        ''', (min_severity, current_time))
        
        columns = [desc[0] for desc in cursor.description]
        alerts = []
        
        for row in cursor.fetchall():
            alerts.append(dict(zip(columns, row)))
        
        conn.close()
        return alerts
    
    def acknowledge_alert(self, alert_id: int):
        """Mark alert as acknowledged"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts SET acknowledged = 1 WHERE id = ?
        ''', (alert_id,))
        
        conn.commit()
        conn.close()
    
    def add_notification_rule(self, alert_type: str, min_severity: int,
                            notification_method: str, contact_info: str):
        """Add notification rule for specific alert types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notification_rules 
            (alert_type, min_severity, notification_method, contact_info)
            VALUES (?, ?, ?, ?)
        ''', (alert_type, min_severity, notification_method, contact_info))
        
        conn.commit()
        conn.close()
    
    def generate_alert_summary(self) -> Dict:
        """Generate summary of current alert status"""
        active_alerts = self.get_active_alerts(1)  # All severities
        
        summary = {
            "total_active": len(active_alerts),
            "by_severity": {"Minor": 0, "Moderate": 0, "Severe": 0, "Extreme": 0},
            "by_type": {},
            "highest_severity": 0,
            "urgent_count": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        severity_names = {1: "Minor", 2: "Moderate", 3: "Severe", 4: "Extreme"}
        
        for alert in active_alerts:
            severity = alert["severity"]
            severity_name = severity_names.get(severity, "Unknown")
            
            summary["by_severity"][severity_name] += 1
            summary["by_type"][alert["alert_type"]] = summary["by_type"].get(alert["alert_type"], 0) + 1
            
            if severity > summary["highest_severity"]:
                summary["highest_severity"] = severity
            
            if severity >= 3:  # Severe or Extreme
                summary["urgent_count"] += 1
        
        return summary
    
    def run_monitoring_cycle(self) -> Dict:
        """Run one complete monitoring cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get configuration
        cursor.execute("SELECT * FROM monitoring_config WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            conn.close()
            return {"error": "No monitoring configuration set"}
        
        lat, lon, location, api_key = config[1:5]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "new_alerts": 0,
            "weather_risks": [],
            "errors": []
        }
        
        # Fetch NWS alerts
        try:
            nws_alerts = self.fetch_nws_alerts()
            for alert in nws_alerts:
                if self.store_alert(alert):
                    results["new_alerts"] += 1
        except Exception as e:
            results["errors"].append(f"NWS alerts: {str(e)}")
        
        # Fetch weather data if API key available
        if api_key:
            try:
                weather_data = self.fetch_weather_data(api_key, lat, lon)
                results["weather_risks"] = self.analyze_weather_risks(weather_data)
                
                # Store weather data
                if weather_data:
                    main = weather_data.get("main", {})
                    wind = weather_data.get("wind", {})
                    cursor.execute('''
                        INSERT INTO weather_data 
                        (location, temperature, humidity, pressure, wind_speed, 
                         wind_direction, conditions, visibility)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (location, main.get("temp"), main.get("humidity"),
                          main.get("pressure"), wind.get("speed"),
                          wind.get("deg"), weather_data.get("weather", [{}])[0].get("description"),
                          weather_data.get("visibility")))
                    
            except Exception as e:
                results["errors"].append(f"Weather data: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return results

if __name__ == "__main__":
    # Example usage
    monitor = AlertMonitoringSystem()
    
    # Set location (example coordinates for a US city)
    monitor.set_location(40.7128, -74.0060, "New York, NY", "your_openweather_api_key_here")
    
    # Add notification rules
    monitor.add_notification_rule("Tornado Warning", 3, "emergency_contact", "555-1234")
    monitor.add_notification_rule("Flood Warning", 3, "emergency_contact", "555-1234")
    
    # Run monitoring cycle
    print("Running monitoring cycle...")
    results = monitor.run_monitoring_cycle()
    
    print(f"New alerts: {results['new_alerts']}")
    print(f"Weather risks: {len(results['weather_risks'])}")
    for risk in results['weather_risks']:
        print(f"  - {risk}")
    
    # Get alert summary
    summary = monitor.generate_alert_summary()
    print(f"\nActive alerts: {summary['total_active']}")
    print(f"Urgent alerts: {summary['urgent_count']}")
    print(f"Highest severity: {summary['highest_severity']}")