#!/usr/bin/env python3
"""
Data Visualization Dashboard for Emergency Preparedness
Generate visual analytics and insights from preparedness data
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import os

class VisualizationDashboard:
    def __init__(self, data_dir: str = "preparedness_data"):
        self.data_dir = data_dir
        self.chart_width = 80
        self.chart_height = 20
        
        # Database connections
        self.dbs = {
            "supplies": f"{data_dir}/supplies.db",
            "contacts": f"{data_dir}/contacts.db",
            "alerts": f"{data_dir}/alerts.db",
            "neighborhood": f"{data_dir}/neighborhood.db",
            "drills": f"{data_dir}/drill_simulator.db"
        }
        
        # ASCII chart characters
        self.bar_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "reset": "\033[0m"
        }
    
    def generate_risk_heatmap(self) -> str:
        """Generate ASCII heatmap of disaster risks"""
        # Risk categories and their probabilities
        risks = {
            "Power Outage": {"probability": 96, "impact": 3, "duration": "hours"},
            "Severe Storm": {"probability": 80, "impact": 5, "duration": "hours"},
            "Water Disruption": {"probability": 45, "impact": 4, "duration": "days"},
            "Earthquake": {"probability": 15, "impact": 9, "duration": "minutes"},
            "Fire": {"probability": 8, "impact": 10, "duration": "minutes"},
            "Flood": {"probability": 25, "impact": 7, "duration": "days"},
            "Tornado": {"probability": 12, "impact": 8, "duration": "minutes"},
            "Pandemic": {"probability": 20, "impact": 6, "duration": "months"},
            "Economic Crisis": {"probability": 35, "impact": 5, "duration": "months"},
            "Cyber Attack": {"probability": 30, "impact": 4, "duration": "days"}
        }
        
        heatmap = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DISASTER RISK HEATMAP                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Impact ↑                                                                      ║
║   10   │ {"█" * 8} Fire                                                       ║
║    9   │ {"█" * 15} Earthquake                                                ║
║    8   │ {"█" * 12} Tornado                                                   ║
║    7   │ {"█" * 25} Flood                                                     ║
║    6   │ {"█" * 20} Pandemic                                                  ║
║    5   │ {"█" * 35} Economic    {"█" * 80} Storm                               ║
║    4   │ {"█" * 30} Cyber       {"█" * 45} Water                                ║
║    3   │ {"█" * 96} Power Outage                                              ║
║    2   │                                                                      ║
║    1   │                                                                      ║
║        └──────────────────────────────────────────────────────────────────→  ║
║         0    10   20   30   40   50   60   70   80   90   100  Probability % ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Legend: █ Size = Risk Level (Probability × Impact)                           ║
║         Position: X-axis = Probability, Y-axis = Impact Severity             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        # Calculate risk scores
        risk_scores = []
        for name, data in risks.items():
            score = (data["probability"] / 10) * data["impact"]
            risk_scores.append((name, score, data["probability"], data["impact"]))
        
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add top risks summary
        summary = "\n📊 TOP 5 RISKS BY COMBINED SCORE:\n"
        for i, (name, score, prob, impact) in enumerate(risk_scores[:5], 1):
            summary += f"  {i}. {name:<20} Score: {score:>5.1f} (P:{prob}% × I:{impact})\n"
        
        return heatmap + summary
    
    def generate_supply_inventory_chart(self) -> str:
        """Generate supply inventory status chart"""
        if not os.path.exists(self.dbs["supplies"]):
            return "No supply data available"
        
        conn = sqlite3.connect(self.dbs["supplies"])
        cursor = conn.cursor()
        
        # Get supply categories and quantities
        cursor.execute('''
            SELECT category, SUM(quantity) as total, COUNT(*) as items
            FROM supplies
            WHERE quantity > 0
            GROUP BY category
            ORDER BY total DESC
        ''')
        
        supplies = cursor.fetchall()
        conn.close()
        
        if not supplies:
            return "No supplies in inventory"
        
        chart = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         SUPPLY INVENTORY STATUS                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""
        
        # Calculate minimum levels (example thresholds)
        min_levels = {
            "water": 21,  # 3 days × 1 gal × 3 people × 7 days safety
            "food": 21000,  # 3 days × 2000 cal × 3 people
            "medication": 30,
            "first_aid": 2,
            "batteries": 20,
            "fuel": 10
        }
        
        max_qty = max(supplies, key=lambda x: x[1])[1] if supplies else 1
        
        for category, quantity, items in supplies:
            # Normalize bar length
            bar_length = int((quantity / max_qty) * 50) if max_qty > 0 else 0
            bar = "█" * bar_length
            
            # Check if below minimum
            min_level = min_levels.get(category, 0)
            if quantity < min_level:
                status = f"{self.colors['red']}⚠ LOW{self.colors['reset']}"
            elif quantity < min_level * 1.5:
                status = f"{self.colors['yellow']}↓ Fair{self.colors['reset']}"
            else:
                status = f"{self.colors['green']}✓ Good{self.colors['reset']}"
            
            chart += f"║ {category:12} │{bar:<50} {quantity:>6.0f} units {status:>10} ║\n"
        
        chart += """╠══════════════════════════════════════════════════════════════════════════════╣
║ Status: ✓ Good = >150% minimum  ↓ Fair = 100-150%  ⚠ LOW = <100% minimum    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return chart
    
    def generate_alert_timeline(self) -> str:
        """Generate timeline of recent alerts"""
        if not os.path.exists(self.dbs["alerts"]):
            return "No alert data available"
        
        conn = sqlite3.connect(self.dbs["alerts"])
        cursor = conn.cursor()
        
        # Get recent alerts
        cursor.execute('''
            SELECT alert_type, severity, start_time, end_time, area
            FROM alerts
            WHERE datetime(start_time) > datetime('now', '-7 days')
            ORDER BY start_time DESC
            LIMIT 10
        ''')
        
        alerts = cursor.fetchall()
        conn.close()
        
        if not alerts:
            timeline = "No recent alerts in the past 7 days ✓"
        else:
            timeline = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ALERT TIMELINE (Past 7 Days)                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""
            
            severity_symbols = {1: "◇", 2: "◆", 3: "▲", 4: "█"}
            
            for alert_type, severity, start_time, end_time, area in alerts:
                symbol = severity_symbols.get(severity, "•")
                
                if severity >= 3:
                    color = self.colors['red']
                elif severity == 2:
                    color = self.colors['yellow']
                else:
                    color = self.colors['green']
                
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    time_str = start_dt.strftime("%m/%d %H:%M")
                except:
                    time_str = "Unknown"
                
                timeline += f"║ {color}{symbol}{self.colors['reset']} {time_str} │ {alert_type:<25} │ {area[:20]:<20} ║\n"
            
            timeline += """╠══════════════════════════════════════════════════════════════════════════════╣
║ Severity: ◇ Minor  ◆ Moderate  ▲ Severe  █ Extreme                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return timeline
    
    def generate_drill_performance_chart(self) -> str:
        """Generate drill performance statistics"""
        if not os.path.exists(self.dbs["drills"]):
            return "No drill data available"
        
        conn = sqlite3.connect(self.dbs["drills"])
        cursor = conn.cursor()
        
        # Get drill statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_drills,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                MIN(score) as worst_score,
                AVG(time_taken) as avg_time
            FROM drill_results
        ''')
        
        stats = cursor.fetchone()
        
        # Get performance by scenario type
        cursor.execute('''
            SELECT 
                ds.disaster_type,
                COUNT(*) as attempts,
                AVG(dr.score) as avg_score,
                MIN(dr.time_taken) as best_time
            FROM drill_results dr
            JOIN drill_scenarios ds ON dr.scenario_id = ds.id
            GROUP BY ds.disaster_type
        ''')
        
        by_type = cursor.fetchall()
        
        conn.close()
        
        if not stats or stats[0] == 0:
            return "No drill results recorded yet"
        
        total, avg_score, best, worst, avg_time = stats
        
        chart = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DRILL PERFORMANCE METRICS                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Overall Statistics:                                                           ║
║   Total Drills Completed: {total:<10}     Average Score: {avg_score or 0:>6.1f}/50         ║
║   Best Score: {best or 0:>6.1f}/50              Worst Score: {worst or 0:>6.1f}/50            ║
║   Average Response Time: {avg_time or 0:>6.1f} minutes                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Performance by Disaster Type:                                                ║
"""
        
        if by_type:
            for disaster_type, attempts, type_avg_score, best_time in by_type:
                # Create bar for average score
                bar_length = int((type_avg_score / 50) * 30) if type_avg_score else 0
                bar = "█" * bar_length
                
                chart += f"║ {disaster_type:12} │{bar:<30} {type_avg_score:>5.1f} ({attempts} drills) ║\n"
        
        chart += """╠══════════════════════════════════════════════════════════════════════════════╣
║ Score Range: 0-50 points  │  Response Time: Lower is better                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return chart
    
    def generate_neighborhood_resource_map(self) -> str:
        """Generate neighborhood resource availability map"""
        if not os.path.exists(self.dbs["neighborhood"]):
            return "No neighborhood data available"
        
        conn = sqlite3.connect(self.dbs["neighborhood"])
        cursor = conn.cursor()
        
        # Get neighbor count and skills
        cursor.execute("SELECT COUNT(*) FROM neighbors")
        neighbor_count = cursor.fetchone()[0]
        
        # Get skill distribution
        cursor.execute('''
            SELECT skill_category, COUNT(*) as skilled_neighbors
            FROM neighbor_skills
            WHERE available = 1
            GROUP BY skill_category
            ORDER BY skilled_neighbors DESC
        ''')
        
        skills = cursor.fetchall()
        
        # Get resource availability
        cursor.execute('''
            SELECT resource_type, COUNT(*) as available_count
            FROM neighbor_resources
            WHERE sharable = 1
            GROUP BY resource_type
            ORDER BY available_count DESC
        ''')
        
        resources = cursor.fetchall()
        
        conn.close()
        
        map_display = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      NEIGHBORHOOD RESOURCE NETWORK                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Network Size: {neighbor_count} participating neighbors                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Available Skills:                                                             ║
"""
        
        if skills:
            for skill, count in skills[:8]:  # Top 8 skills
                bar_length = min(count * 5, 40)
                bar = "▓" * bar_length
                map_display += f"║   {skill:15} │{bar:<40} {count} people ║\n"
        else:
            map_display += "║   No skills registered yet                                                   ║\n"
        
        map_display += """╠══════════════════════════════════════════════════════════════════════════════╣
║ Shared Resources:                                                            ║
"""
        
        if resources:
            for resource, count in resources[:8]:  # Top 8 resources
                bar_length = min(count * 3, 40)
                bar = "▓" * bar_length
                map_display += f"║   {resource:15} │{bar:<40} {count} items  ║\n"
        else:
            map_display += "║   No resources registered yet                                                ║\n"
        
        map_display += """╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return map_display
    
    def generate_preparedness_score_gauge(self, score: float) -> str:
        """Generate ASCII gauge for preparedness score"""
        # Score should be 0-100
        score = max(0, min(100, score))
        
        # Determine status
        if score >= 90:
            status = "EXCELLENT"
            color = self.colors['green']
        elif score >= 70:
            status = "GOOD"
            color = self.colors['green']
        elif score >= 50:
            status = "ADEQUATE"
            color = self.colors['yellow']
        elif score >= 30:
            status = "NEEDS WORK"
            color = self.colors['yellow']
        else:
            status = "CRITICAL"
            color = self.colors['red']
        
        # Create gauge
        filled = int(score / 2)  # 50 character width
        empty = 50 - filled
        
        gauge = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      OVERALL PREPAREDNESS SCORE                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   0%                           50%                          100%             ║
║   │{"─" * 24}┼{"─" * 24}│             ║
║   │{color}{"█" * filled}{self.colors['reset']}{"░" * empty}│ {score:>5.1f}%      ║
║   └{"─" * 49}┘             ║
║                                                                               ║
║                         Status: {color}{status:^12}{self.colors['reset']}                          ║
║                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Score Breakdown:                                                              ║
║   • Supplies & Inventory    : {"█" * 8}░░  80%                               ║
║   • Emergency Contacts      : {"█" * 7}░░░  70%                               ║
║   • Drill Performance       : {"█" * 6}░░░░  60%                               ║
║   • Neighborhood Network    : {"█" * 5}░░░░░  50%                               ║
║   • Alert Monitoring        : {"█" * 9}░  90%                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return gauge
    
    def generate_supply_burndown_chart(self, days: int = 30) -> str:
        """Generate supply consumption projection chart"""
        if not os.path.exists(self.dbs["supplies"]):
            return "No supply data available"
        
        conn = sqlite3.connect(self.dbs["supplies"])
        cursor = conn.cursor()
        
        # Get current water and food supplies
        cursor.execute('''
            SELECT category, SUM(quantity) as total
            FROM supplies
            WHERE category IN ('water', 'food')
            GROUP BY category
        ''')
        
        supplies = dict(cursor.fetchall())
        conn.close()
        
        # Consumption rates (per person per day)
        water_per_day = 1.0  # gallons
        food_per_day = 2000  # calories
        family_size = 3
        
        chart = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SUPPLY BURNDOWN PROJECTION ({days} Days)                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""
        
        # Water burndown
        water_current = supplies.get('water', 0)
        water_daily = water_per_day * family_size
        
        chart += "║ WATER (gallons):                                                             ║\n║  "
        
        for day in range(0, days + 1, 3):
            remaining = max(0, water_current - (water_daily * day))
            height = int((remaining / water_current * 8)) if water_current > 0 else 0
            
            if height >= 6:
                color = self.colors['green']
            elif height >= 3:
                color = self.colors['yellow']
            else:
                color = self.colors['red']
            
            bar = self.bar_chars[min(height, 7)] if height > 0 else "_"
            chart += f"{color}{bar * 2}{self.colors['reset']}"
        
        water_days = int(water_current / water_daily) if water_daily > 0 else 0
        chart += f"  Days until empty: {water_days}      ║\n"
        
        # Food burndown
        food_current = supplies.get('food', 0)
        food_daily = food_per_day * family_size
        
        chart += "║ FOOD (calories):                                                             ║\n║  "
        
        for day in range(0, days + 1, 3):
            remaining = max(0, food_current - (food_daily * day))
            height = int((remaining / food_current * 8)) if food_current > 0 else 0
            
            if height >= 6:
                color = self.colors['green']
            elif height >= 3:
                color = self.colors['yellow']
            else:
                color = self.colors['red']
            
            bar = self.bar_chars[min(height, 7)] if height > 0 else "_"
            chart += f"{color}{bar * 2}{self.colors['reset']}"
        
        food_days = int(food_current / food_daily) if food_daily > 0 else 0
        chart += f"  Days until empty: {food_days}      ║\n"
        
        chart += f"""║  Day: 0   3   6   9   12  15  18  21  24  27  30                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Consumption Rate: {family_size} people × {water_per_day} gal water/day × {food_per_day} cal food/day         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return chart
    
    def generate_full_dashboard(self) -> str:
        """Generate complete dashboard with all visualizations"""
        dashboard = f"""
{'='*80}
              EMERGENCY PREPAREDNESS VISUAL DASHBOARD
              Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*80}
"""
        
        # Add each visualization section
        dashboard += "\n" + self.generate_preparedness_score_gauge(75)
        dashboard += "\n" + self.generate_risk_heatmap()
        dashboard += "\n" + self.generate_supply_inventory_chart()
        dashboard += "\n" + self.generate_supply_burndown_chart()
        dashboard += "\n" + self.generate_alert_timeline()
        dashboard += "\n" + self.generate_drill_performance_chart()
        dashboard += "\n" + self.generate_neighborhood_resource_map()
        
        return dashboard
    
    def export_dashboard_html(self, filepath: str = "dashboard.html") -> str:
        """Export dashboard as HTML file"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Emergency Preparedness Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body {{
            background-color: #1a1a1a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            padding: 20px;
            line-height: 1.4;
        }}
        pre {{
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        h1 {{
            color: #ffff00;
            text-align: center;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 10px;
        }}
        .timestamp {{
            text-align: center;
            color: #888;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .warning {{ color: #ff0000; }}
        .good {{ color: #00ff00; }}
        .caution {{ color: #ffff00; }}
    </style>
</head>
<body>
    <h1>🚨 Emergency Preparedness Dashboard 🚨</h1>
    <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    
    <div class="section">
        <pre>{self.generate_preparedness_score_gauge(75)}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_risk_heatmap()}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_supply_inventory_chart()}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_supply_burndown_chart()}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_alert_timeline()}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_drill_performance_chart()}</pre>
    </div>
    
    <div class="section">
        <pre>{self.generate_neighborhood_resource_map()}</pre>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function(){{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>"""
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath

if __name__ == "__main__":
    # Example usage
    dashboard = VisualizationDashboard()
    
    print(dashboard.generate_full_dashboard())
    
    # Export to HTML
    html_file = dashboard.export_dashboard_html("emergency_dashboard.html")
    print(f"\n📊 Dashboard exported to: {html_file}")
    print("Open in browser for best viewing experience")