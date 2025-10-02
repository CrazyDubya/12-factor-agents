"""
KnowledgeGraphManager - Core Neo4j database interaction for narrative consistency.

This class manages the Neo4j knowledge graph that stores and tracks all
narrative elements and their relationships for consistency validation.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import json
import time

from neo4j import GraphDatabase, Result
from neo4j.exceptions import ServiceUnavailable, TransientError

from ..config import neo4j_config

logger = logging.getLogger(__name__)

@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    labels: List[str]
    properties: Dict[str, Any]

@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph."""
    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: Dict[str, Any]

class KnowledgeGraphManager:
    """
    Manages the Neo4j knowledge graph for narrative consistency tracking.

    This class provides high-level operations for storing, querying, and
    maintaining the knowledge graph that underpins narrative consistency.
    """

    def __init__(self, uri: str = None, user: str = None, password: str = None,
                 database: str = None):
        """
        Initialize the knowledge graph manager.

        Args:
            uri: Neo4j URI (defaults to config)
            user: Neo4j username (defaults to config)
            password: Neo4j password (defaults to config)
            database: Neo4j database name (defaults to config)
        """
        self.uri = uri or neo4j_config.uri
        self.user = user or neo4j_config.user
        self.password = password or neo4j_config.password
        self.database = database or neo4j_config.database

        self.driver = None
        self.logger = logging.getLogger(__name__)

        # Schema constraints and indexes
        self.constraints = [
            "CREATE CONSTRAINT world_id_unique IF NOT EXISTS FOR (w:World) REQUIRE w.world_id IS UNIQUE",
            "CREATE CONSTRAINT character_id_unique IF NOT EXISTS FOR (c:Character) REQUIRE c.character_id IS UNIQUE",
            "CREATE CONSTRAINT location_id_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.document_id IS UNIQUE",
            "CREATE CONSTRAINT event_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE"
        ]

        self.indexes = [
            "CREATE INDEX world_theme_index IF NOT EXISTS FOR (w:World) ON (w.theme)",
            "CREATE INDEX character_name_index IF NOT EXISTS FOR (c:Character) ON (c.name)",
            "CREATE INDEX location_name_index IF NOT EXISTS FOR (l:Location) ON (l.name)",
            "CREATE INDEX document_type_index IF NOT EXISTS FOR (d:Document) ON (d.type)",
            "CREATE INDEX event_timestamp_index IF NOT EXISTS FOR (e:Event) ON (e.timestamp)"
        ]

    def connect(self) -> bool:
        """
        Connect to the Neo4j database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

            # Test connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]

                if test_value == 1:
                    self.logger.info("Successfully connected to Neo4j database")
                    self._setup_schema()
                    return True
                else:
                    self.logger.error("Neo4j connection test failed")
                    return False

        except ServiceUnavailable as e:
            self.logger.error(f"Neo4j service unavailable: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the Neo4j database."""
        if self.driver:
            self.driver.close()
            self.logger.info("Disconnected from Neo4j database")

    def _setup_schema(self):
        """Set up database schema with constraints and indexes."""
        try:
            with self.driver.session(database=self.database) as session:
                # Create constraints
                for constraint in self.constraints:
                    try:
                        session.run(constraint)
                    except Exception as e:
                        # Constraints may already exist
                        self.logger.debug(f"Constraint creation warning: {str(e)}")

                # Create indexes
                for index in self.indexes:
                    try:
                        session.run(index)
                    except Exception as e:
                        # Indexes may already exist
                        self.logger.debug(f"Index creation warning: {str(e)}")

            self.logger.info("Database schema setup completed")

        except Exception as e:
            self.logger.error(f"Failed to setup database schema: {str(e)}")

    def create_world(self, world_id: str, theme: str, properties: Dict[str, Any] = None) -> bool:
        """
        Create a new world node in the knowledge graph.

        Args:
            world_id: Unique identifier for the world
            theme: Theme or genre of the world
            properties: Additional properties for the world

        Returns:
            True if creation successful, False otherwise
        """
        try:
            world_props = {
                "world_id": world_id,
                "theme": theme,
                "created_at": time.time(),
                **(properties or {})
            }

            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    CREATE (w:World $props)
                    RETURN w.world_id as world_id
                    """,
                    props=world_props
                )

                created_world = result.single()
                if created_world:
                    self.logger.info(f"Created world: {world_id}")
                    return True
                else:
                    self.logger.error(f"Failed to create world: {world_id}")
                    return False

        except Exception as e:
            self.logger.error(f"Error creating world {world_id}: {str(e)}")
            return False

    def create_character(self, world_id: str, character_data: Dict[str, Any]) -> bool:
        """
        Create a character node and link it to a world.

        Args:
            world_id: ID of the world this character belongs to
            character_data: Character information

        Returns:
            True if creation successful, False otherwise
        """
        try:
            char_props = {
                "character_id": character_data["id"],
                "name": character_data["name"],
                "role": character_data.get("role", ""),
                "type": character_data.get("type", ""),
                "personality": character_data.get("personality", ""),
                "motivations": character_data.get("motivations", ""),
                "background": character_data.get("background", ""),
                "skills": character_data.get("skills", ""),
                "flaws": character_data.get("flaws", ""),
                "created_at": time.time()
            }

            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    CREATE (c:Character $char_props)
                    CREATE (c)-[:BELONGS_TO]->(w)
                    RETURN c.character_id as character_id
                    """,
                    world_id=world_id,
                    char_props=char_props
                )

                created_char = result.single()
                if created_char:
                    self.logger.info(f"Created character: {character_data['name']}")
                    return True
                else:
                    self.logger.error(f"Failed to create character: {character_data['name']}")
                    return False

        except Exception as e:
            self.logger.error(f"Error creating character {character_data.get('name', 'unknown')}: {str(e)}")
            return False

    def create_location(self, world_id: str, location_data: Dict[str, Any]) -> bool:
        """
        Create a location node and link it to a world.

        Args:
            world_id: ID of the world this location belongs to
            location_data: Location information

        Returns:
            True if creation successful, False otherwise
        """
        try:
            loc_props = {
                "location_id": location_data["id"],
                "name": location_data["name"],
                "type": location_data.get("type", ""),
                "description": location_data.get("description", ""),
                "inhabitants": location_data.get("inhabitants", ""),
                "significance": location_data.get("significance", ""),
                "connections": location_data.get("connections", ""),
                "created_at": time.time()
            }

            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    CREATE (l:Location $loc_props)
                    CREATE (l)-[:LOCATED_IN]->(w)
                    RETURN l.location_id as location_id
                    """,
                    world_id=world_id,
                    loc_props=loc_props
                )

                created_loc = result.single()
                if created_loc:
                    self.logger.info(f"Created location: {location_data['name']}")
                    return True
                else:
                    self.logger.error(f"Failed to create location: {location_data['name']}")
                    return False

        except Exception as e:
            self.logger.error(f"Error creating location {location_data.get('name', 'unknown')}: {str(e)}")
            return False

    def create_document(self, world_id: str, document_data: Dict[str, Any]) -> bool:
        """
        Create a document node and link it to relevant entities.

        Args:
            world_id: ID of the world this document belongs to
            document_data: Document information

        Returns:
            True if creation successful, False otherwise
        """
        try:
            doc_props = {
                "document_id": document_data["id"],
                "type": document_data["type"],
                "title": document_data["title"],
                "author": document_data["author"],
                "content": document_data["content"],
                "context_notes": document_data.get("context_notes", ""),
                "word_count": document_data.get("metadata", {}).get("word_count", 0),
                "created_at": time.time()
            }

            with self.driver.session(database=self.database) as session:
                # Create document
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    CREATE (d:Document $doc_props)
                    CREATE (d)-[:PART_OF]->(w)
                    RETURN d.document_id as document_id
                    """,
                    world_id=world_id,
                    doc_props=doc_props
                )

                created_doc = result.single()
                if not created_doc:
                    self.logger.error(f"Failed to create document: {document_data['title']}")
                    return False

                # Link to author if it's a character
                if document_data["author"]:
                    session.run(
                        """
                        MATCH (d:Document {document_id: $doc_id})
                        MATCH (c:Character {name: $author_name})
                        MERGE (c)-[:AUTHORED]->(d)
                        """,
                        doc_id=document_data["id"],
                        author_name=document_data["author"]
                    )

                self.logger.info(f"Created document: {document_data['title']}")
                return True

        except Exception as e:
            self.logger.error(f"Error creating document {document_data.get('title', 'unknown')}: {str(e)}")
            return False

    def create_relationship(self, start_node_id: str, end_node_id: str,
                          relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """
        Create a relationship between two nodes.

        Args:
            start_node_id: ID of the starting node
            end_node_id: ID of the ending node
            relationship_type: Type of relationship
            properties: Additional relationship properties

        Returns:
            True if creation successful, False otherwise
        """
        try:
            rel_props = properties or {}
            rel_props["created_at"] = time.time()

            with self.driver.session(database=self.database) as session:
                result = session.run(
                    f"""
                    MATCH (a), (b)
                    WHERE a.character_id = $start_id OR a.location_id = $start_id OR a.document_id = $start_id
                    AND (b.character_id = $end_id OR b.location_id = $end_id OR b.document_id = $end_id)
                    CREATE (a)-[r:{relationship_type} $rel_props]->(b)
                    RETURN type(r) as rel_type
                    """,
                    start_id=start_node_id,
                    end_id=end_node_id,
                    rel_props=rel_props
                )

                created_rel = result.single()
                if created_rel:
                    self.logger.info(f"Created {relationship_type} relationship: {start_node_id} -> {end_node_id}")
                    return True
                else:
                    self.logger.error(f"Failed to create relationship: {start_node_id} -> {end_node_id}")
                    return False

        except Exception as e:
            self.logger.error(f"Error creating relationship {start_node_id} -> {end_node_id}: {str(e)}")
            return False

    def find_character_mentions(self, world_id: str, character_name: str) -> List[Dict[str, Any]]:
        """
        Find all documents that mention a specific character.

        Args:
            world_id: ID of the world to search in
            character_name: Name of the character to search for

        Returns:
            List of documents that mention the character
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (d:Document)-[:PART_OF]->(w)
                    WHERE toLower(d.content) CONTAINS toLower($char_name)
                       OR toLower(d.author) CONTAINS toLower($char_name)
                    RETURN d.document_id as document_id, d.title as title,
                           d.type as type, d.author as author
                    ORDER BY d.created_at DESC
                    """,
                    world_id=world_id,
                    char_name=character_name
                )

                mentions = []
                for record in result:
                    mentions.append({
                        "document_id": record["document_id"],
                        "title": record["title"],
                        "type": record["type"],
                        "author": record["author"]
                    })

                return mentions

        except Exception as e:
            self.logger.error(f"Error finding character mentions: {str(e)}")
            return []

    def find_location_mentions(self, world_id: str, location_name: str) -> List[Dict[str, Any]]:
        """
        Find all documents that mention a specific location.

        Args:
            world_id: ID of the world to search in
            location_name: Name of the location to search for

        Returns:
            List of documents that mention the location
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (d:Document)-[:PART_OF]->(w)
                    WHERE toLower(d.content) CONTAINS toLower($loc_name)
                    RETURN d.document_id as document_id, d.title as title,
                           d.type as type, d.content as content
                    ORDER BY d.created_at DESC
                    """,
                    world_id=world_id,
                    loc_name=location_name
                )

                mentions = []
                for record in result:
                    mentions.append({
                        "document_id": record["document_id"],
                        "title": record["title"],
                        "type": record["type"],
                        "content_snippet": record["content"][:200] + "..." if len(record["content"]) > 200 else record["content"]
                    })

                return mentions

        except Exception as e:
            self.logger.error(f"Error finding location mentions: {str(e)}")
            return []

    def get_character_relationships(self, world_id: str, character_id: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for a specific character.

        Args:
            world_id: ID of the world
            character_id: ID of the character

        Returns:
            List of character relationships
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (c1:Character {character_id: $char_id})-[:BELONGS_TO]->(w)
                    MATCH (c1)-[r]-(c2:Character)-[:BELONGS_TO]->(w)
                    RETURN c1.name as character1, c2.name as character2,
                           type(r) as relationship_type, properties(r) as properties
                    """,
                    world_id=world_id,
                    char_id=character_id
                )

                relationships = []
                for record in result:
                    relationships.append({
                        "character1": record["character1"],
                        "character2": record["character2"],
                        "relationship_type": record["relationship_type"],
                        "properties": dict(record["properties"])
                    })

                return relationships

        except Exception as e:
            self.logger.error(f"Error getting character relationships: {str(e)}")
            return []

    def check_consistency_violations(self, world_id: str) -> List[Dict[str, Any]]:
        """
        Check for potential consistency violations in the world.

        Args:
            world_id: ID of the world to check

        Returns:
            List of potential consistency issues
        """
        violations = []

        try:
            with self.driver.session(database=self.database) as session:
                # Check for duplicate character names
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (c:Character)-[:BELONGS_TO]->(w)
                    WITH toLower(c.name) as name, collect(c) as characters
                    WHERE size(characters) > 1
                    RETURN name, [c IN characters | c.character_id] as character_ids
                    """,
                    world_id=world_id
                )

                for record in result:
                    violations.append({
                        "type": "duplicate_character_names",
                        "severity": "major",
                        "description": f"Multiple characters with name '{record['name']}'",
                        "affected_ids": record["character_ids"]
                    })

                # Check for duplicate location names
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (l:Location)-[:LOCATED_IN]->(w)
                    WITH toLower(l.name) as name, collect(l) as locations
                    WHERE size(locations) > 1
                    RETURN name, [l IN locations | l.location_id] as location_ids
                    """,
                    world_id=world_id
                )

                for record in result:
                    violations.append({
                        "type": "duplicate_location_names",
                        "severity": "major",
                        "description": f"Multiple locations with name '{record['name']}'",
                        "affected_ids": record["location_ids"]
                    })

                # Check for orphaned documents (no author or mentions)
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    MATCH (d:Document)-[:PART_OF]->(w)
                    WHERE NOT EXISTS((d)<-[:AUTHORED]-()) AND d.author = ""
                    RETURN d.document_id as document_id, d.title as title
                    """,
                    world_id=world_id
                )

                for record in result:
                    violations.append({
                        "type": "orphaned_document",
                        "severity": "minor",
                        "description": f"Document '{record['title']}' has no clear author",
                        "affected_ids": [record["document_id"]]
                    })

        except Exception as e:
            self.logger.error(f"Error checking consistency violations: {str(e)}")

        return violations

    def get_world_stats(self, world_id: str) -> Dict[str, Any]:
        """
        Get statistics for a world.

        Args:
            world_id: ID of the world

        Returns:
            Dictionary of world statistics
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    OPTIONAL MATCH (c:Character)-[:BELONGS_TO]->(w)
                    OPTIONAL MATCH (l:Location)-[:LOCATED_IN]->(w)
                    OPTIONAL MATCH (d:Document)-[:PART_OF]->(w)
                    RETURN w.theme as theme,
                           count(DISTINCT c) as character_count,
                           count(DISTINCT l) as location_count,
                           count(DISTINCT d) as document_count
                    """,
                    world_id=world_id
                )

                record = result.single()
                if record:
                    return {
                        "world_id": world_id,
                        "theme": record["theme"],
                        "character_count": record["character_count"],
                        "location_count": record["location_count"],
                        "document_count": record["document_count"]
                    }
                else:
                    return {"error": f"World {world_id} not found"}

        except Exception as e:
            self.logger.error(f"Error getting world stats: {str(e)}")
            return {"error": str(e)}

    def delete_world(self, world_id: str) -> bool:
        """
        Delete a world and all its related entities.

        Args:
            world_id: ID of the world to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (w:World {world_id: $world_id})
                    OPTIONAL MATCH (w)<-[:BELONGS_TO|LOCATED_IN|PART_OF]-(entity)
                    DETACH DELETE w, entity
                    RETURN count(*) as deleted_count
                    """,
                    world_id=world_id
                )

                record = result.single()
                deleted_count = record["deleted_count"] if record else 0

                self.logger.info(f"Deleted world {world_id} and {deleted_count} related entities")
                return deleted_count > 0

        except Exception as e:
            self.logger.error(f"Error deleting world {world_id}: {str(e)}")
            return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()