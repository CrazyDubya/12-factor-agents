#!/usr/bin/env python3
"""
Neighborhood Emergency Coordination System
Coordinate with neighbors, share resources, and organize community response
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib

@dataclass
class Neighbor:
    id: int
    name: str
    address: str
    phone: str
    email: Optional[str]
    skills: List[str]
    resources: List[str]
    needs: List[str]
    availability: str

@dataclass
class ResourceRequest:
    id: int
    requester_id: int
    resource_type: str
    quantity: str
    urgency: str
    status: str
    created_date: str

class NeighborhoodCoordination:
    def __init__(self, db_path: str = "neighborhood.db"):
        self.db_path = db_path
        self.init_database()
        self.skill_categories = [
            "medical", "construction", "electrical", "plumbing", "mechanical",
            "cooking", "childcare", "elderly_care", "transportation", 
            "communication", "security", "search_rescue", "first_aid"
        ]
        self.resource_categories = [
            "food", "water", "medical_supplies", "tools", "fuel", "generator",
            "transportation", "shelter", "communication", "batteries", "lighting"
        ]
    
    def init_database(self):
        """Initialize SQLite database for neighborhood coordination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neighbors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                medical_conditions TEXT,
                special_needs TEXT,
                notes TEXT,
                privacy_level INTEGER DEFAULT 2,
                last_contact TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neighbor_skills (
                neighbor_id INTEGER,
                skill_category TEXT,
                skill_description TEXT,
                proficiency_level INTEGER,
                available INTEGER DEFAULT 1,
                FOREIGN KEY (neighbor_id) REFERENCES neighbors (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neighbor_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                neighbor_id INTEGER,
                resource_type TEXT,
                description TEXT,
                quantity TEXT,
                condition TEXT,
                sharable INTEGER DEFAULT 1,
                location TEXT,
                FOREIGN KEY (neighbor_id) REFERENCES neighbors (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER,
                resource_type TEXT,
                description TEXT,
                quantity_needed TEXT,
                urgency TEXT,
                status TEXT DEFAULT 'open',
                fulfilled_by INTEGER,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                fulfilled_date TEXT,
                FOREIGN KEY (requester_id) REFERENCES neighbors (id),
                FOREIGN KEY (fulfilled_by) REFERENCES neighbors (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                message_type TEXT,
                subject TEXT,
                content TEXT,
                priority TEXT DEFAULT 'normal',
                expires_date TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES neighbors (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evacuation_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                leader_id INTEGER,
                meeting_point TEXT,
                transportation_plan TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (leader_id) REFERENCES neighbors (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INTEGER,
                neighbor_id INTEGER,
                role TEXT,
                FOREIGN KEY (group_id) REFERENCES evacuation_groups (id),
                FOREIGN KEY (neighbor_id) REFERENCES neighbors (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_neighbor(self, name: str, address: str, phone: str,
                    email: Optional[str] = None,
                    emergency_contact_name: Optional[str] = None,
                    emergency_contact_phone: Optional[str] = None,
                    medical_conditions: Optional[str] = None,
                    special_needs: Optional[str] = None,
                    privacy_level: int = 2) -> int:
        """Add a new neighbor to the coordination system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO neighbors (name, address, phone, email, emergency_contact_name,
                                 emergency_contact_phone, medical_conditions, special_needs, privacy_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, email, emergency_contact_name,
              emergency_contact_phone, medical_conditions, special_needs, privacy_level))
        
        neighbor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return neighbor_id
    
    def add_neighbor_skill(self, neighbor_id: int, skill_category: str,
                          skill_description: str, proficiency_level: int = 3):
        """Add a skill to a neighbor's profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO neighbor_skills (neighbor_id, skill_category, skill_description, proficiency_level)
            VALUES (?, ?, ?, ?)
        ''', (neighbor_id, skill_category, skill_description, proficiency_level))
        
        conn.commit()
        conn.close()
    
    def add_neighbor_resource(self, neighbor_id: int, resource_type: str,
                            description: str, quantity: str = "1",
                            condition: str = "good", sharable: bool = True,
                            location: Optional[str] = None) -> int:
        """Add a resource to a neighbor's inventory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO neighbor_resources (neighbor_id, resource_type, description, 
                                          quantity, condition, sharable, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (neighbor_id, resource_type, description, quantity, condition, int(sharable), location))
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resource_id
    
    def create_resource_request(self, requester_id: int, resource_type: str,
                              description: str, quantity_needed: str,
                              urgency: str = "medium") -> int:
        """Create a new resource request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resource_requests (requester_id, resource_type, description,
                                         quantity_needed, urgency)
            VALUES (?, ?, ?, ?, ?)
        ''', (requester_id, resource_type, description, quantity_needed, urgency))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def fulfill_resource_request(self, request_id: int, fulfiller_id: int):
        """Mark a resource request as fulfilled"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE resource_requests 
            SET status = 'fulfilled', fulfilled_by = ?, fulfilled_date = ?
            WHERE id = ?
        ''', (fulfiller_id, datetime.now().isoformat(), request_id))
        
        conn.commit()
        conn.close()
    
    def find_neighbors_by_skill(self, skill_category: str, min_proficiency: int = 2) -> List[Dict]:
        """Find neighbors with specific skills"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.id, n.name, n.address, n.phone, ns.skill_description, 
                   ns.proficiency_level
            FROM neighbors n
            JOIN neighbor_skills ns ON n.id = ns.neighbor_id
            WHERE ns.skill_category = ? AND ns.proficiency_level >= ?
            AND ns.available = 1
            ORDER BY ns.proficiency_level DESC
        ''', (skill_category, min_proficiency))
        
        skilled_neighbors = []
        for row in cursor.fetchall():
            skilled_neighbors.append({
                "id": row[0],
                "name": row[1],
                "address": row[2],
                "phone": row[3],
                "skill_description": row[4],
                "proficiency": row[5]
            })
        
        conn.close()
        return skilled_neighbors
    
    def find_available_resources(self, resource_type: str) -> List[Dict]:
        """Find available resources of a specific type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nr.id, nr.description, nr.quantity, nr.condition, nr.location,
                   n.name, n.address, n.phone
            FROM neighbor_resources nr
            JOIN neighbors n ON nr.neighbor_id = n.id
            WHERE nr.resource_type = ? AND nr.sharable = 1
            ORDER BY nr.condition DESC
        ''', (resource_type,))
        
        resources = []
        for row in cursor.fetchall():
            resources.append({
                "resource_id": row[0],
                "description": row[1],
                "quantity": row[2],
                "condition": row[3],
                "location": row[4],
                "owner_name": row[5],
                "owner_address": row[6],
                "owner_phone": row[7]
            })
        
        conn.close()
        return resources
    
    def get_open_resource_requests(self, urgency_filter: Optional[str] = None) -> List[Dict]:
        """Get all open resource requests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT rr.id, rr.resource_type, rr.description, rr.quantity_needed,
                   rr.urgency, rr.created_date, n.name, n.address, n.phone
            FROM resource_requests rr
            JOIN neighbors n ON rr.requester_id = n.id
            WHERE rr.status = 'open'
        '''
        params = []
        
        if urgency_filter:
            query += ' AND rr.urgency = ?'
            params.append(urgency_filter)
        
        query += ' ORDER BY rr.urgency DESC, rr.created_date'
        
        cursor.execute(query, params)
        
        requests = []
        for row in cursor.fetchall():
            requests.append({
                "request_id": row[0],
                "resource_type": row[1],
                "description": row[2],
                "quantity_needed": row[3],
                "urgency": row[4],
                "created_date": row[5],
                "requester_name": row[6],
                "requester_address": row[7],
                "requester_phone": row[8]
            })
        
        conn.close()
        return requests
    
    def create_evacuation_group(self, group_name: str, leader_id: int,
                              meeting_point: str, transportation_plan: str,
                              member_ids: List[int]) -> int:
        """Create an evacuation coordination group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evacuation_groups (group_name, leader_id, meeting_point, transportation_plan)
            VALUES (?, ?, ?, ?)
        ''', (group_name, leader_id, meeting_point, transportation_plan))
        
        group_id = cursor.lastrowid
        
        # Add group members
        for member_id in member_ids:
            role = "leader" if member_id == leader_id else "member"
            cursor.execute('''
                INSERT INTO group_members (group_id, neighbor_id, role)
                VALUES (?, ?, ?)
            ''', (group_id, member_id, role))
        
        conn.commit()
        conn.close()
        
        return group_id
    
    def post_community_message(self, sender_id: int, message_type: str,
                             subject: str, content: str, priority: str = "normal",
                             expires_hours: Optional[int] = None) -> int:
        """Post a message to the community board"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_date = None
        if expires_hours:
            expires_date = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
        
        cursor.execute('''
            INSERT INTO community_messages (sender_id, message_type, subject, content, priority, expires_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sender_id, message_type, subject, content, priority, expires_date))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_community_messages(self, message_type: Optional[str] = None) -> List[Dict]:
        """Get active community messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT cm.id, cm.message_type, cm.subject, cm.content, cm.priority,
                   cm.created_date, n.name
            FROM community_messages cm
            JOIN neighbors n ON cm.sender_id = n.id
            WHERE (cm.expires_date IS NULL OR cm.expires_date > ?)
        '''
        params = [datetime.now().isoformat()]
        
        if message_type:
            query += ' AND cm.message_type = ?'
            params.append(message_type)
        
        query += ' ORDER BY cm.priority DESC, cm.created_date DESC'
        
        cursor.execute(query, params)
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row[0],
                "type": row[1],
                "subject": row[2],
                "content": row[3],
                "priority": row[4],
                "created": row[5],
                "sender": row[6]
            })
        
        conn.close()
        return messages
    
    def generate_neighborhood_directory(self) -> Dict:
        """Generate neighborhood emergency directory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get neighbors with skills
        cursor.execute('''
            SELECT n.id, n.name, n.address, n.phone, n.emergency_contact_phone,
                   GROUP_CONCAT(ns.skill_category) as skills,
                   n.special_needs, n.medical_conditions
            FROM neighbors n
            LEFT JOIN neighbor_skills ns ON n.id = ns.neighbor_id
            WHERE n.privacy_level >= 2
            GROUP BY n.id
            ORDER BY n.address
        ''')
        
        neighbors = []
        for row in cursor.fetchall():
            neighbors.append({
                "name": row[1],
                "address": row[2],
                "phone": row[3],
                "emergency_contact": row[4],
                "skills": row[5].split(',') if row[5] else [],
                "special_needs": row[6],
                "medical_conditions": row[7]
            })
        
        # Get resource summary
        cursor.execute('''
            SELECT resource_type, COUNT(*) as available_count
            FROM neighbor_resources
            WHERE sharable = 1
            GROUP BY resource_type
            ORDER BY available_count DESC
        ''')
        
        resource_summary = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "neighbors": neighbors,
            "resource_summary": resource_summary,
            "generated": datetime.now().isoformat(),
            "total_neighbors": len(neighbors)
        }

if __name__ == "__main__":
    # Example usage
    coord = NeighborhoodCoordination()
    
    # Add neighbors
    neighbor1 = coord.add_neighbor("John Smith", "123 Main St", "555-1234", 
                                  "john@email.com", "Jane Smith", "555-5678",
                                  "Diabetes", None, privacy_level=3)
    
    neighbor2 = coord.add_neighbor("Mary Johnson", "125 Main St", "555-2345",
                                  "mary@email.com", privacy_level=2)
    
    # Add skills
    coord.add_neighbor_skill(neighbor1, "medical", "Nurse - 20 years experience", 5)
    coord.add_neighbor_skill(neighbor2, "construction", "Contractor", 4)
    
    # Add resources
    coord.add_neighbor_resource(neighbor1, "medical_supplies", "First aid kit, bandages", "1 kit")
    coord.add_neighbor_resource(neighbor2, "tools", "Power tools, hand tools", "Complete set")
    
    # Create resource request
    request_id = coord.create_resource_request(neighbor1, "generator", 
                                             "Need backup power for medical equipment", 
                                             "1 portable generator", "high")
    
    # Post community message
    coord.post_community_message(neighbor1, "alert", "Weather Warning",
                                "Severe storm expected tonight. Check on elderly neighbors.", 
                                "high", 24)
    
    # Get community messages
    messages = coord.get_community_messages()
    print(f"Community messages: {len(messages)}")
    
    # Generate directory
    directory = coord.generate_neighborhood_directory()
    print(f"Neighborhood directory: {directory['total_neighbors']} neighbors")