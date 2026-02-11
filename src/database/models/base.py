"""
Base déclarative SQLAlchemy.

Tous les modèles héritent de cette classe Base.
"""

from sqlalchemy.ext.declarative import declarative_base

# Base déclarative pour tous les modèles
Base = declarative_base()

# Métadonnées partagées
metadata = Base.metadata
