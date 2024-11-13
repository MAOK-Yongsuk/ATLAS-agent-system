from typing import Dict, List, Optional
from neo4j import AsyncGraphDatabase
from pinecone import Pinecone
import asyncio, uuid, datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.neo4j = self._init_neo4j()
        self.pinecone = self._init_pinecone()
        
    def _init_neo4j(self):
        """Initialize Neo4j connection"""
        try:
            driver = AsyncGraphDatabase.driver(
                self.config["neo4j_uri"],
                auth=(self.config["neo4j_user"], self.config["neo4j_password"])
            )
            return driver
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {str(e)}")
            raise
    
    def _init_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            pc = Pinecone(api_key=self.config["pinecone_api_key"])
            return pc.Index(self.config["pinecone_index"])
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    async def setup_neo4j_schema(self):
        """Set up Neo4j schema with constraints and indexes"""
        queries = [
            # Student nodes
            """CREATE CONSTRAINT student_id IF NOT EXISTS 
               FOR (s:Student) REQUIRE s.id IS UNIQUE""",
            
            # Material nodes
            """CREATE CONSTRAINT material_id IF NOT EXISTS 
               FOR (m:Material) REQUIRE m.id IS UNIQUE""",
            
            # Concept nodes
            """CREATE CONSTRAINT concept_id IF NOT EXISTS 
               FOR (c:Concept) REQUIRE c.id IS UNIQUE""",
            
            # Task nodes
            """CREATE CONSTRAINT task_id IF NOT EXISTS 
               FOR (t:Task) REQUIRE t.id IS UNIQUE""",
            
            # Indexes
            """CREATE INDEX material_type IF NOT EXISTS 
               FOR (m:Material) ON (m.type)""",
            
            """CREATE INDEX concept_name IF NOT EXISTS 
               FOR (c:Concept) ON (c.name)"""
        ]
        
        async with self.neo4j.session() as session:
            for query in queries:
                try:
                    await session.run(query)
                except Exception as e:
                    logger.error(f"Failed to create schema: {str(e)}")
                    raise
    
    async def store_study_material(self, material: Dict) -> str:
        """Store study material in both databases"""
        try:
            # Store in Pinecone
            vector_id = await self._store_in_pinecone(material)
            
            # Store in Neo4j
            await self._store_material_in_neo4j(material, vector_id)
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Failed to store study material: {str(e)}")
            raise
    
    async def _store_in_pinecone(self, material: Dict) -> str:
        """Store embeddings in Pinecone"""
        try:
            vector_id = str(uuid.uuid4())
            
            self.pinecone.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": material["embedding"],
                    "metadata": {
                        "type": material["type"],
                        "title": material["title"],
                        "content": material["content"][:1000],  # Truncate for metadata
                        "created_at": str(datetime.now())
                    }
                }]
            )
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Failed to store in Pinecone: {str(e)}")
            raise
    
    async def _store_material_in_neo4j(self, material: Dict, vector_id: str):
        """Store material metadata and relationships in Neo4j"""
        query = """
        CREATE (m:Material {
            id: $id,
            vector_id: $vector_id,
            title: $title,
            type: $type,
            created_at: datetime()
        })
        WITH m
        UNWIND $concepts as concept
        MERGE (c:Concept {name: concept.name})
        ON CREATE SET c.description = concept.description
        CREATE (m)-[:CONTAINS]->(c)
        """
        
        params = {
            "id": str(uuid.uuid4()),
            "vector_id": vector_id,
            "title": material["title"],
            "type": material["type"],
            "concepts": material.get("concepts", [])
        }
        
        async with self.neo4j.session() as session:
            await session.run(query, params)
    
    async def cleanup(self):
        """Clean up database connections"""
        await self.neo4j.close()
       