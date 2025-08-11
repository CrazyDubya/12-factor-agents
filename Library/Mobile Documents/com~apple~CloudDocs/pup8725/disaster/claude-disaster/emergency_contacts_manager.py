#!/usr/bin/env python3
"""
Emergency Contact Management System
Organize, prioritize, and quickly access emergency contacts during disasters
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class EmergencyContactsManager:
    def __init__(self, db_path: str = "emergency_contacts.db"):
        self.db_path = db_path
        self.init_database()
        self.contact_categories = {
            "immediate_family": {"priority": 1, "color": "red"},
            "extended_family": {"priority": 2, "color": "orange"},
            "medical": {"priority": 1, "color": "red"},
            "emergency_services": {"priority": 1, "color": "red"},
            "utilities": {"priority": 2, "color": "yellow"},
            "insurance": {"priority": 3, "color": "blue"},
            "work": {"priority": 3, "color": "green"},
            "school": {"priority": 2, "color": "orange"},
            "neighbors": {"priority": 2, "color": "green"},
            "support_network": {"priority": 3, "color": "blue"}
        }
    
    def init_database(self):
        """Initialize SQLite database for contact management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT,
                primary_phone TEXT,
                secondary_phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT,
                priority INTEGER DEFAULT 3,
                last_verified TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                description TEXT,
                activation_scenario TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INTEGER,
                contact_id INTEGER,
                notification_order INTEGER,
                FOREIGN KEY (group_id) REFERENCES contact_groups (id),
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                contact_type TEXT,
                status TEXT,
                notes TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_contact(self, category: str, name: str, primary_phone: str,
                   relationship: Optional[str] = None,
                   secondary_phone: Optional[str] = None,
                   email: Optional[str] = None,
                   address: Optional[str] = None,
                   notes: Optional[str] = None) -> int:
        """Add a new emergency contact"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        priority = self.contact_categories.get(category, {}).get("priority", 3)
        
        cursor.execute('''
            INSERT INTO contacts (category, name, relationship, primary_phone,
                                secondary_phone, email, address, notes, priority, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (category, name, relationship, primary_phone, secondary_phone,
              email, address, notes, priority, datetime.now().isoformat()))
        
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return contact_id
    
    def create_contact_group(self, group_name: str, description: str,
                           activation_scenario: str, contact_ids: List[int]) -> int:
        """Create a contact group for specific scenarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_groups (group_name, description, activation_scenario)
            VALUES (?, ?, ?)
        ''', (group_name, description, activation_scenario))
        
        group_id = cursor.lastrowid
        
        # Add members to group
        for order, contact_id in enumerate(contact_ids, 1):
            cursor.execute('''
                INSERT INTO group_members (group_id, contact_id, notification_order)
                VALUES (?, ?, ?)
            ''', (group_id, contact_id, order))
        
        conn.commit()
        conn.close()
        
        return group_id
    
    def get_priority_contacts(self, scenario: Optional[str] = None) -> List[Dict]:
        """Get contacts sorted by priority for a given scenario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if scenario:
            # Get contacts from relevant group
            cursor.execute('''
                SELECT c.*, gm.notification_order
                FROM contacts c
                JOIN group_members gm ON c.id = gm.contact_id
                JOIN contact_groups g ON gm.group_id = g.id
                WHERE g.activation_scenario LIKE ?
                ORDER BY gm.notification_order
            ''', (f'%{scenario}%',))
        else:
            # Get all contacts by priority
            cursor.execute('''
                SELECT * FROM contacts
                ORDER BY priority, category, name
            ''')
        
        columns = [desc[0] for desc in cursor.description]
        contacts = []
        
        for row in cursor.fetchall():
            contact = dict(zip(columns, row))
            contacts.append(contact)
        
        conn.close()
        return contacts
    
    def log_communication(self, contact_id: int, contact_type: str,
                         status: str, notes: Optional[str] = None):
        """Log communication attempts for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO communication_log (contact_id, contact_type, status, notes)
            VALUES (?, ?, ?, ?)
        ''', (contact_id, contact_type, status, notes))
        
        conn.commit()
        conn.close()
    
    def verify_contact(self, contact_id: int, verified: bool = True):
        """Mark contact as verified/updated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if verified:
            cursor.execute('''
                UPDATE contacts
                SET last_verified = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), contact_id))
        
        conn.commit()
        conn.close()
    
    def get_emergency_card(self, format: str = "text") -> str:
        """Generate emergency contact card for wallet/phone"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top priority contacts
        cursor.execute('''
            SELECT name, relationship, primary_phone, category
            FROM contacts
            WHERE priority = 1
            ORDER BY category, name
            LIMIT 10
        ''')
        
        if format == "text":
            card = "=== EMERGENCY CONTACTS ===\n"
            card += f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            for row in cursor.fetchall():
                name, rel, phone, cat = row
                card += f"{cat.upper()}:\n"
                card += f"  {name}"
                if rel:
                    card += f" ({rel})"
                card += f"\n  {phone}\n\n"
        
        elif format == "json":
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    "name": row[0],
                    "relationship": row[1],
                    "phone": row[2],
                    "category": row[3]
                })
            card = json.dumps({
                "emergency_contacts": contacts,
                "generated": datetime.now().isoformat()
            }, indent=2)
        
        conn.close()
        return card
    
    def get_verification_status(self) -> Dict:
        """Check which contacts need verification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contacts not verified in 6 months
        six_months_ago = datetime.now().timestamp() - (180 * 24 * 60 * 60)
        
        cursor.execute('''
            SELECT id, name, category, last_verified
            FROM contacts
            WHERE last_verified IS NULL 
            OR datetime(last_verified) < datetime('now', '-6 months')
            ORDER BY priority, category
        ''')
        
        needs_verification = []
        for row in cursor.fetchall():
            needs_verification.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "last_verified": row[3]
            })
        
        # Get verification statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN datetime(last_verified) >= datetime('now', '-6 months') THEN 1 END) as verified,
                COUNT(CASE WHEN datetime(last_verified) < datetime('now', '-6 months') THEN 1 END) as outdated,
                COUNT(CASE WHEN last_verified IS NULL THEN 1 END) as never_verified
            FROM contacts
        ''')
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "needs_verification": needs_verification,
            "statistics": {
                "total": stats[0],
                "verified": stats[1],
                "outdated": stats[2],
                "never_verified": stats[3],
                "verification_rate": round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 1)
            }
        }
    
    def export_contacts(self, filepath: str = "emergency_contacts_export.json"):
        """Export all contacts to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all contacts
        cursor.execute("SELECT * FROM contacts ORDER BY priority, category, name")
        columns = [desc[0] for desc in cursor.description]
        contacts = []
        for row in cursor.fetchall():
            contacts.append(dict(zip(columns, row)))
        
        # Get all groups
        cursor.execute("SELECT * FROM contact_groups")
        group_columns = [desc[0] for desc in cursor.description]
        groups = []
        for row in cursor.fetchall():
            groups.append(dict(zip(group_columns, row)))
        
        conn.close()
        
        with open(filepath, 'w') as f:
            json.dump({
                "contacts": contacts,
                "groups": groups,
                "exported": datetime.now().isoformat(),
                "total_contacts": len(contacts)
            }, f, indent=2)
        
        return filepath
    
    def initialize_default_services(self):
        """Add default emergency service contacts"""
        default_services = [
            ("emergency_services", "Emergency", "911", "Police/Fire/Medical", None, None, None, "Life-threatening emergencies only"),
            ("emergency_services", "Poison Control", "1-800-222-1222", "Poison Help", None, None, None, "24/7 poison emergency hotline"),
            ("emergency_services", "Non-Emergency Police", "311", "Non-Emergency", None, None, None, "Non-urgent police matters"),
            ("medical", "Hospital ER", "Update with local", "Emergency Room", None, None, None, "Nearest hospital emergency room"),
            ("utilities", "Gas Company Emergency", "Update with local", "Gas Leak", None, None, None, "Gas leak or emergency"),
            ("utilities", "Electric Company", "Update with local", "Power Outage", None, None, None, "Power outage reporting"),
            ("utilities", "Water Department", "Update with local", "Water Emergency", None, None, None, "Water main break or emergency")
        ]
        
        for service in default_services:
            self.add_contact(*service)

if __name__ == "__main__":
    # Example usage
    manager = EmergencyContactsManager()
    
    # Initialize with default emergency services
    manager.initialize_default_services()
    
    # Add family contacts
    manager.add_contact("immediate_family", "John Doe", "555-1234", 
                       "Spouse", "555-5678", "john@email.com",
                       "123 Main St", "Primary emergency contact")
    
    manager.add_contact("immediate_family", "Jane Doe", "555-2345",
                       "Parent", None, "jane@email.com",
                       "456 Oak Ave", "Lives nearby")
    
    # Create a contact group for evacuation scenario
    evacuation_group = manager.create_contact_group(
        "Evacuation Alert",
        "Contacts to notify during evacuation",
        "evacuation, fire, flood",
        [1, 2]  # Contact IDs
    )
    
    # Get emergency card
    print(manager.get_emergency_card())
    
    # Check verification status
    status = manager.get_verification_status()
    print(f"\nVerification Rate: {status['statistics']['verification_rate']}%")
    print(f"Needs Verification: {len(status['needs_verification'])} contacts")