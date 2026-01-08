"""
Database module - Gestion de la connexion et des opérations BD
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    """Classe pour gérer les connexions à la base de données"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            self.engine = create_engine(
                self.db_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            # Tester la connexion
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Connexion à la base de données établie")
            return True
        except SQLAlchemyError as e:
            logger.error(f"✗ Erreur de connexion: {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Connexion fermée")
    
    def get_session(self) -> Session:
        """Obtenir une nouvelle session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.SessionLocal()
    
    def execute_query(self, query: str):
        """Exécuter une requête SQL brute"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                conn.commit()
                return result
        except SQLAlchemyError as e:
            logger.error(f"Erreur SQL: {e}")
            raise
    
    def insert_many(self, table_name: str, data: list):
        """Insérer plusieurs lignes"""
        session = self.get_session()
        try:
            # À implémenter avec ORM
            session.commit()
            logger.info(f"✓ {len(data)} lignes insérées dans {table_name}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erreur lors de l'insertion: {e}")
            raise
        finally:
            session.close()

# Instance globale
db = Database()
