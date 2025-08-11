#!/usr/bin/env python3
"""
Knowledge Base Search and Integration System
Makes all markdown guides and PDFs searchable with contextual recommendations
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib

class KnowledgeBaseSearch:
    def __init__(self, knowledge_dir: str = "disaster_knowledge_base", db_path: str = "knowledge_base.db"):
        self.knowledge_dir = knowledge_dir
        self.db_path = db_path
        self.init_database()
        self.index_built = False
        
        # Categories and their keywords for smart recommendations
        self.categories = {
            "water": ["water", "hydration", "purification", "filter", "boil", "distill", "rain", "collection"],
            "food": ["food", "nutrition", "cooking", "preservation", "storage", "foraging", "hunting", "calories"],
            "shelter": ["shelter", "housing", "warmth", "insulation", "construction", "building", "protection"],
            "medical": ["medical", "first aid", "injury", "medicine", "health", "wound", "emergency care", "pain"],
            "power": ["power", "electricity", "generator", "solar", "battery", "energy", "lighting", "fuel"],
            "communication": ["communication", "radio", "phone", "internet", "signal", "emergency broadcast"],
            "security": ["security", "defense", "protection", "safety", "perimeter", "locks", "surveillance"],
            "sanitation": ["sanitation", "hygiene", "waste", "toilet", "cleaning", "disposal", "disease"],
            "psychology": ["psychology", "mental", "stress", "community", "morale", "panic", "leadership"],
            "evacuation": ["evacuation", "bug out", "escape", "route", "transportation", "assembly"]
        }
    
    def init_database(self):
        """Initialize database for knowledge base indexing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_name TEXT,
                category TEXT,
                title TEXT,
                content TEXT,
                content_hash TEXT,
                file_type TEXT,
                last_indexed TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                section_title TEXT,
                section_content TEXT,
                section_level INTEGER,
                section_order INTEGER,
                FOREIGN KEY (document_id) REFERENCES knowledge_documents (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT,
                document_id INTEGER,
                section_id INTEGER,
                frequency INTEGER,
                positions TEXT,
                FOREIGN KEY (document_id) REFERENCES knowledge_documents (id),
                FOREIGN KEY (section_id) REFERENCES knowledge_sections (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactive_checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                checklist_title TEXT,
                items TEXT,
                category TEXT,
                priority INTEGER,
                FOREIGN KEY (document_id) REFERENCES knowledge_documents (id)
            )
        ''')
        
        # Create indexes for faster searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_term ON search_index (term)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_doc ON search_index (document_id)')
        
        conn.commit()
        conn.close()
    
    def index_knowledge_base(self, force_reindex: bool = False) -> Dict:
        """Index all markdown and text files in knowledge base"""
        indexed_files = 0
        skipped_files = 0
        errors = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find all markdown and text files
        knowledge_path = Path(self.knowledge_dir)
        if not knowledge_path.exists():
            conn.close()
            return {"error": f"Knowledge base directory not found: {self.knowledge_dir}"}
        
        for file_path in knowledge_path.rglob("*.md"):
            try:
                # Check if file needs indexing
                full_path = str(file_path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                # Check if already indexed
                cursor.execute('''
                    SELECT content_hash FROM knowledge_documents 
                    WHERE file_path = ?
                ''', (full_path,))
                
                existing = cursor.fetchone()
                
                if existing and existing[0] == content_hash and not force_reindex:
                    skipped_files += 1
                    continue
                
                # Determine category from path
                category = self._determine_category(full_path, content)
                
                # Extract title
                title = self._extract_title(content) or file_path.stem.replace('_', ' ').title()
                
                # Store document
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_documents 
                    (file_path, file_name, category, title, content, content_hash, file_type, last_indexed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (full_path, file_path.name, category, title, content, content_hash, 
                      'markdown', datetime.now().isoformat()))
                
                doc_id = cursor.lastrowid
                
                # Index sections
                sections = self._extract_sections(content)
                for i, section in enumerate(sections):
                    cursor.execute('''
                        INSERT INTO knowledge_sections 
                        (document_id, section_title, section_content, section_level, section_order)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (doc_id, section['title'], section['content'], section['level'], i))
                    
                    section_id = cursor.lastrowid
                    
                    # Create search index
                    self._index_content(cursor, doc_id, section_id, section['content'])
                
                # Extract checklists
                checklists = self._extract_checklists(content)
                for checklist in checklists:
                    cursor.execute('''
                        INSERT INTO interactive_checklists 
                        (document_id, checklist_title, items, category, priority)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (doc_id, checklist['title'], json.dumps(checklist['items']), 
                          category, checklist.get('priority', 5)))
                
                indexed_files += 1
                
            except Exception as e:
                errors.append(f"Error indexing {file_path}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        self.index_built = True
        
        return {
            "indexed": indexed_files,
            "skipped": skipped_files,
            "errors": errors,
            "total_documents": self._get_document_count()
        }
    
    def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search knowledge base for relevant information"""
        if not self.index_built:
            self.index_knowledge_base()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tokenize query
        terms = self._tokenize(query.lower())
        
        # Build search query
        results = {}
        
        for term in terms:
            sql = '''
                SELECT DISTINCT 
                    d.id, d.title, d.file_path, d.category,
                    s.section_title, s.section_content,
                    si.frequency
                FROM search_index si
                JOIN knowledge_documents d ON si.document_id = d.id
                LEFT JOIN knowledge_sections s ON si.section_id = s.id
                WHERE si.term LIKE ?
            '''
            params = [f'{term}%']
            
            if category:
                sql += ' AND d.category = ?'
                params.append(category)
            
            sql += ' ORDER BY si.frequency DESC LIMIT ?'
            params.append(limit * 2)  # Get more results for ranking
            
            cursor.execute(sql, params)
            
            for row in cursor.fetchall():
                doc_id = row[0]
                if doc_id not in results:
                    results[doc_id] = {
                        'id': doc_id,
                        'title': row[1],
                        'file_path': row[2],
                        'category': row[3],
                        'sections': [],
                        'relevance_score': 0
                    }
                
                # Add section if not already present
                section_info = {
                    'title': row[4],
                    'content': row[5][:200] + '...' if len(row[5]) > 200 else row[5],
                    'frequency': row[6]
                }
                
                if section_info not in results[doc_id]['sections']:
                    results[doc_id]['sections'].append(section_info)
                    results[doc_id]['relevance_score'] += row[6]
        
        conn.close()
        
        # Sort by relevance and return top results
        sorted_results = sorted(results.values(), key=lambda x: x['relevance_score'], reverse=True)
        
        return sorted_results[:limit]
    
    def get_contextual_recommendations(self, context: str) -> List[Dict]:
        """Get recommendations based on current context"""
        recommendations = []
        
        # Determine relevant categories from context
        relevant_categories = []
        context_lower = context.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in context_lower for keyword in keywords):
                relevant_categories.append(category)
        
        if not relevant_categories:
            relevant_categories = ["general"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top documents from relevant categories
        for category in relevant_categories[:3]:  # Top 3 categories
            cursor.execute('''
                SELECT id, title, file_path, category
                FROM knowledge_documents
                WHERE category = ?
                LIMIT 3
            ''', (category,))
            
            for row in cursor.fetchall():
                recommendations.append({
                    'id': row[0],
                    'title': row[1],
                    'file_path': row[2],
                    'category': row[3],
                    'reason': f"Relevant to {category} preparedness"
                })
        
        conn.close()
        
        return recommendations[:10]
    
    def get_checklists(self, category: Optional[str] = None) -> List[Dict]:
        """Get interactive checklists from knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT c.id, c.checklist_title, c.items, c.category, c.priority,
                       d.title as document_title
                FROM interactive_checklists c
                JOIN knowledge_documents d ON c.document_id = d.id
                WHERE c.category = ?
                ORDER BY c.priority DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT c.id, c.checklist_title, c.items, c.category, c.priority,
                       d.title as document_title
                FROM interactive_checklists c
                JOIN knowledge_documents d ON c.document_id = d.id
                ORDER BY c.priority DESC
            ''')
        
        checklists = []
        for row in cursor.fetchall():
            checklists.append({
                'id': row[0],
                'title': row[1],
                'items': json.loads(row[2]),
                'category': row[3],
                'priority': row[4],
                'source': row[5]
            })
        
        conn.close()
        
        return checklists
    
    def get_document(self, doc_id: int) -> Dict:
        """Get full document by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM knowledge_documents WHERE id = ?
        ''', (doc_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {}
        
        document = {
            'id': row[0],
            'file_path': row[1],
            'file_name': row[2],
            'category': row[3],
            'title': row[4],
            'content': row[5],
            'file_type': row[7],
            'last_indexed': row[8]
        }
        
        # Get sections
        cursor.execute('''
            SELECT section_title, section_content, section_level
            FROM knowledge_sections
            WHERE document_id = ?
            ORDER BY section_order
        ''', (doc_id,))
        
        document['sections'] = []
        for section in cursor.fetchall():
            document['sections'].append({
                'title': section[0],
                'content': section[1],
                'level': section[2]
            })
        
        conn.close()
        
        return document
    
    def _determine_category(self, file_path: str, content: str) -> str:
        """Determine category from file path and content"""
        path_lower = file_path.lower()
        content_lower = content.lower()[:1000]  # Check first 1000 chars
        
        # Check path for category
        for category in self.categories:
            if category in path_lower:
                return category
        
        # Check content for category keywords
        best_category = "general"
        best_score = 0
        
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                return line[2:].strip()
        return None
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from markdown content"""
        sections = []
        current_section = {'title': 'Introduction', 'content': '', 'level': 0}
        
        for line in content.split('\n'):
            if line.startswith('#'):
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {'title': title, 'content': '', 'level': level}
            else:
                current_section['content'] += line + '\n'
        
        # Add last section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_checklists(self, content: str) -> List[Dict]:
        """Extract checklists from markdown content"""
        checklists = []
        current_checklist = None
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Look for checklist headers
            if '## ' in line and ('checklist' in line.lower() or 'items' in line.lower()):
                if current_checklist and current_checklist['items']:
                    checklists.append(current_checklist)
                
                current_checklist = {
                    'title': line.replace('#', '').strip(),
                    'items': [],
                    'priority': 5
                }
            
            # Look for checklist items
            elif current_checklist and (line.strip().startswith('- [ ]') or 
                                       line.strip().startswith('- [x]') or
                                       line.strip().startswith('* ') or
                                       line.strip().startswith('- ')):
                item_text = re.sub(r'^[-*]\s*(\[.\])?\s*', '', line.strip())
                if item_text:
                    current_checklist['items'].append({
                        'text': item_text,
                        'checked': '[x]' in line
                    })
        
        # Add last checklist
        if current_checklist and current_checklist['items']:
            checklists.append(current_checklist)
        
        return checklists
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for indexing"""
        # Simple tokenization - could be enhanced
        tokens = re.findall(r'\b[a-z]+\b', text.lower())
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]
    
    def _index_content(self, cursor, doc_id: int, section_id: int, content: str):
        """Index content for search"""
        tokens = self._tokenize(content)
        
        # Count term frequency
        term_freq = {}
        for i, token in enumerate(tokens):
            if token not in term_freq:
                term_freq[token] = {'count': 0, 'positions': []}
            term_freq[token]['count'] += 1
            term_freq[token]['positions'].append(i)
        
        # Store in index
        for term, data in term_freq.items():
            cursor.execute('''
                INSERT INTO search_index (term, document_id, section_id, frequency, positions)
                VALUES (?, ?, ?, ?, ?)
            ''', (term, doc_id, section_id, data['count'], json.dumps(data['positions'])))
    
    def _get_document_count(self) -> int:
        """Get total number of indexed documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM knowledge_documents')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def generate_quick_reference_cards(self) -> List[Dict]:
        """Generate printable quick reference cards"""
        cards = []
        
        # Define essential topics for cards
        essential_topics = [
            ("Water Purification", "water"),
            ("Fire Starting", "shelter"),
            ("First Aid Basics", "medical"),
            ("Emergency Signals", "communication"),
            ("Knot Tying", "shelter"),
            ("Food Safety", "food")
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for topic, category in essential_topics:
            # Search for relevant content
            cursor.execute('''
                SELECT d.title, s.section_content
                FROM knowledge_documents d
                JOIN knowledge_sections s ON d.id = s.document_id
                WHERE d.category = ? AND s.section_title LIKE ?
                LIMIT 1
            ''', (category, f'%{topic.split()[0]}%'))
            
            result = cursor.fetchone()
            if result:
                # Create card with essential info
                card = {
                    'title': topic,
                    'category': category,
                    'content': self._summarize_for_card(result[1]),
                    'source': result[0]
                }
                cards.append(card)
        
        conn.close()
        
        return cards
    
    def _summarize_for_card(self, content: str, max_length: int = 300) -> str:
        """Summarize content for quick reference card"""
        # Extract key points (lines starting with bullets or numbers)
        key_points = []
        for line in content.split('\n'):
            if re.match(r'^[\-\*\d]+\.?\s', line.strip()):
                point = re.sub(r'^[\-\*\d]+\.?\s', '', line.strip())
                if point and len(point) < 100:
                    key_points.append(point)
        
        # Return first few key points that fit
        summary = ""
        for point in key_points[:5]:
            if len(summary) + len(point) < max_length:
                summary += f"• {point}\n"
        
        return summary or content[:max_length]

if __name__ == "__main__":
    # Example usage
    kb = KnowledgeBaseSearch()
    
    print("Indexing knowledge base...")
    result = kb.index_knowledge_base()
    print(f"Indexed {result['indexed']} files, skipped {result['skipped']}")
    
    # Test search
    print("\nSearching for 'water purification'...")
    results = kb.search("water purification")
    for r in results[:3]:
        print(f"  - {r['title']} ({r['category']})")
        if r['sections']:
            print(f"    Section: {r['sections'][0]['title']}")
    
    # Get checklists
    print("\nAvailable checklists:")
    checklists = kb.get_checklists()
    for cl in checklists[:3]:
        print(f"  - {cl['title']} ({len(cl['items'])} items)")
    
    # Generate quick reference cards
    print("\nGenerating quick reference cards...")
    cards = kb.generate_quick_reference_cards()
    for card in cards[:2]:
        print(f"\n📇 {card['title'].upper()}")
        print(card['content'])