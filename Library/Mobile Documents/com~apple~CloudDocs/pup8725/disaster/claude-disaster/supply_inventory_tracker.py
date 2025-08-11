#!/usr/bin/env python3
"""
Emergency Supply Inventory Tracking System
Track, monitor, and alert on emergency supply levels and expiration dates
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class SupplyInventoryTracker:
    def __init__(self, db_path: str = "emergency_supplies.db"):
        self.db_path = db_path
        self.init_database()
        self.categories = {
            "water": {"min_days": 3, "per_person_daily": 1.0, "unit": "gallons"},
            "food": {"min_days": 3, "per_person_daily": 2000, "unit": "calories"},
            "medication": {"min_days": 7, "per_person_daily": None, "unit": "doses"},
            "first_aid": {"min_quantity": 1, "unit": "kits"},
            "batteries": {"min_quantity": 20, "unit": "units"},
            "fuel": {"min_quantity": 5, "unit": "gallons"},
            "cash": {"min_amount": 500, "unit": "dollars"},
            "documents": {"min_quantity": 1, "unit": "sets"}
        }
    
    def init_database(self):
        """Initialize SQLite database for supply tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                expiration_date TEXT,
                location TEXT,
                notes TEXT,
                last_checked TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supply_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supply_id INTEGER,
                quantity_used REAL,
                usage_date TEXT DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                FOREIGN KEY (supply_id) REFERENCES supplies (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                acknowledged INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_supply(self, category: str, item_name: str, quantity: float, 
                   unit: str, expiration_date: Optional[str] = None,
                   location: Optional[str] = None, notes: Optional[str] = None) -> int:
        """Add a new supply item to inventory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO supplies (category, item_name, quantity, unit, 
                                 expiration_date, location, notes, last_checked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (category, item_name, quantity, unit, expiration_date, 
              location, notes, datetime.now().isoformat()))
        
        supply_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return supply_id
    
    def update_supply(self, supply_id: int, quantity: Optional[float] = None,
                      expiration_date: Optional[str] = None,
                      location: Optional[str] = None) -> bool:
        """Update existing supply item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)
        if expiration_date is not None:
            updates.append("expiration_date = ?")
            params.append(expiration_date)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        
        updates.append("last_checked = ?")
        params.append(datetime.now().isoformat())
        params.append(supply_id)
        
        if updates:
            query = f"UPDATE supplies SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        return True
    
    def use_supply(self, supply_id: int, quantity_used: float, reason: str = ""):
        """Record supply usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current quantity
        cursor.execute("SELECT quantity FROM supplies WHERE id = ?", (supply_id,))
        current = cursor.fetchone()
        
        if current and current[0] >= quantity_used:
            # Update supply quantity
            new_quantity = current[0] - quantity_used
            cursor.execute("UPDATE supplies SET quantity = ? WHERE id = ?",
                         (new_quantity, supply_id))
            
            # Log usage
            cursor.execute('''
                INSERT INTO supply_usage (supply_id, quantity_used, reason)
                VALUES (?, ?, ?)
            ''', (supply_id, quantity_used, reason))
            
            conn.commit()
        
        conn.close()
    
    def check_expiration_alerts(self, days_ahead: int = 30) -> List[Dict]:
        """Check for items expiring soon"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        
        cursor.execute('''
            SELECT id, item_name, expiration_date, quantity, unit
            FROM supplies
            WHERE expiration_date IS NOT NULL 
            AND expiration_date <= ?
            AND quantity > 0
            ORDER BY expiration_date
        ''', (cutoff_date,))
        
        expiring_items = []
        for row in cursor.fetchall():
            days_until = (datetime.fromisoformat(row[2]) - datetime.now()).days
            expiring_items.append({
                "id": row[0],
                "item": row[1],
                "expiration": row[2],
                "days_until": max(0, days_until),
                "quantity": row[3],
                "unit": row[4]
            })
        
        conn.close()
        return expiring_items
    
    def check_minimum_levels(self, family_size: int = 3) -> List[Dict]:
        """Check if supplies meet minimum recommended levels"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        alerts = []
        
        for category, requirements in self.categories.items():
            cursor.execute('''
                SELECT SUM(quantity), unit
                FROM supplies
                WHERE category = ? AND quantity > 0
                GROUP BY unit
            ''', (category,))
            
            result = cursor.fetchone()
            current_quantity = result[0] if result else 0
            
            # Calculate minimum needed
            if "min_days" in requirements and requirements.get("per_person_daily"):
                min_needed = requirements["min_days"] * requirements["per_person_daily"] * family_size
            elif "min_quantity" in requirements:
                min_needed = requirements["min_quantity"]
            elif "min_amount" in requirements:
                min_needed = requirements["min_amount"]
            else:
                continue
            
            if current_quantity < min_needed:
                shortage = min_needed - current_quantity
                alerts.append({
                    "category": category,
                    "current": current_quantity,
                    "minimum": min_needed,
                    "shortage": shortage,
                    "unit": requirements["unit"],
                    "severity": "high" if current_quantity < min_needed * 0.5 else "medium"
                })
        
        conn.close()
        return alerts
    
    def generate_shopping_list(self, family_size: int = 3) -> Dict:
        """Generate shopping list based on minimum levels"""
        shortages = self.check_minimum_levels(family_size)
        expiring = self.check_expiration_alerts(90)  # 3 months ahead
        
        shopping_list = {
            "urgent": [],
            "soon": [],
            "maintenance": []
        }
        
        # Add shortage items
        for item in shortages:
            priority = "urgent" if item["severity"] == "high" else "soon"
            shopping_list[priority].append({
                "category": item["category"],
                "quantity_needed": item["shortage"],
                "unit": item["unit"],
                "reason": "below_minimum"
            })
        
        # Add expiring items
        for item in expiring:
            if item["days_until"] <= 30:
                priority = "urgent"
            elif item["days_until"] <= 60:
                priority = "soon"
            else:
                priority = "maintenance"
            
            shopping_list[priority].append({
                "item": item["item"],
                "quantity": item["quantity"],
                "unit": item["unit"],
                "reason": f"expires_in_{item['days_until']}_days"
            })
        
        return shopping_list
    
    def get_inventory_summary(self) -> Dict:
        """Get comprehensive inventory summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Category totals
        cursor.execute('''
            SELECT category, COUNT(*), SUM(quantity)
            FROM supplies
            WHERE quantity > 0
            GROUP BY category
        ''')
        
        category_summary = {}
        for row in cursor.fetchall():
            category_summary[row[0]] = {
                "item_count": row[1],
                "total_quantity": row[2]
            }
        
        # Location summary
        cursor.execute('''
            SELECT location, COUNT(*)
            FROM supplies
            WHERE location IS NOT NULL AND quantity > 0
            GROUP BY location
        ''')
        
        location_summary = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent usage
        cursor.execute('''
            SELECT s.item_name, su.quantity_used, su.usage_date, su.reason
            FROM supply_usage su
            JOIN supplies s ON su.supply_id = s.id
            ORDER BY su.usage_date DESC
            LIMIT 10
        ''')
        
        recent_usage = []
        for row in cursor.fetchall():
            recent_usage.append({
                "item": row[0],
                "quantity": row[1],
                "date": row[2],
                "reason": row[3]
            })
        
        conn.close()
        
        return {
            "categories": category_summary,
            "locations": location_summary,
            "recent_usage": recent_usage,
            "last_updated": datetime.now().isoformat()
        }
    
    def export_inventory(self, filepath: str = "inventory_export.json"):
        """Export full inventory to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM supplies ORDER BY category, item_name")
        
        inventory = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            inventory.append(dict(zip(columns, row)))
        
        conn.close()
        
        with open(filepath, 'w') as f:
            json.dump({
                "inventory": inventory,
                "exported": datetime.now().isoformat(),
                "total_items": len(inventory)
            }, f, indent=2)
        
        return filepath

if __name__ == "__main__":
    # Example usage
    tracker = SupplyInventoryTracker()
    
    # Add some sample supplies
    tracker.add_supply("water", "Bottled Water (24 pack)", 4, "cases", 
                      "2025-12-31", "Basement", "Store in cool, dark place")
    tracker.add_supply("food", "Canned Beans", 24, "cans", 
                      "2026-06-30", "Pantry", "High protein")
    tracker.add_supply("medication", "Ibuprofen", 100, "tablets", 
                      "2025-08-15", "Medicine Cabinet", "200mg tablets")
    tracker.add_supply("batteries", "AA Batteries", 24, "units", 
                      None, "Utility Drawer", "Alkaline")
    
    # Check alerts
    print("=== EXPIRATION ALERTS ===")
    for item in tracker.check_expiration_alerts():
        print(f"- {item['item']}: expires in {item['days_until']} days")
    
    print("\n=== MINIMUM LEVEL ALERTS ===")
    for alert in tracker.check_minimum_levels():
        print(f"- {alert['category']}: {alert['current']}/{alert['minimum']} {alert['unit']}")
    
    print("\n=== SHOPPING LIST ===")
    shopping = tracker.generate_shopping_list()
    for priority, items in shopping.items():
        if items:
            print(f"\n{priority.upper()}:")
            for item in items:
                print(f"  - {item}")