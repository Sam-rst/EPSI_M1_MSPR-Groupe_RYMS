"""
Modèle ORM : Prediction.

Prédictions électorales 2027 générées par les modèles Machine Learning.
"""

from sqlalchemy import Column, BigInteger, String, Integer, TIMESTAMP, CheckConstraint, Index, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import Base


class Prediction(Base):
    """
    Entité Prediction : Prédictions électorales ML.

    Output du pipeline Machine Learning avec traçabilité complète.
    Utilise le système polymorphe de territoire (id_territoire + type_territoire).

    Attributes:
        id_prediction: Identifiant auto-incrémenté (PK)
        id_territoire: Identifiant polymorphe du territoire (ex: '33063', '3301', '33')
        type_territoire: Type de territoire (COMMUNE, CANTON, DEPARTEMENT, REGION, NATIONAL)
        candidat: Nom candidat prédit
        parti: Parti politique
        annee_prediction: Année prédite (2025-2050)
        tour: Tour prédit (1 ou 2)
        pourcentage_predit: % voix prédit (0-100)
        intervalle_confiance_inf: Borne inférieure IC 95% (0-100)
        intervalle_confiance_sup: Borne supérieure IC 95% (0-100)
        modele_utilise: Nom du modèle (RandomForest, XGBoost, etc.)
        version_modele: Version modèle (ex: v1.2.0)
        metriques_modele: Métriques performance (R², MAE, RMSE) - JSONB
        features_utilisees: Liste des features ML - JSONB
        date_generation: Date de génération de la prédiction

    Contrainte Unicité:
        (id_territoire, type_territoire, candidat, tour, annee_prediction, version_modele) → Versioning prédictions

    Example:
        >>> prediction = Prediction(
        ...     id_territoire='33063',
        ...     type_territoire='COMMUNE',
        ...     candidat='Emmanuel MACRON',
        ...     parti='RE',
        ...     annee_prediction=2027,
        ...     tour=1,
        ...     pourcentage_predit=32.15,
        ...     intervalle_confiance_inf=29.80,
        ...     intervalle_confiance_sup=34.50,
        ...     modele_utilise='RandomForest',
        ...     version_modele='v1.2.0',
        ...     metriques_modele={'r2': 0.72, 'mae': 2.3, 'rmse': 3.1},
        ...     features_utilisees=['taux_chomage', 'criminalite', 'participation_2022']
        ... )
    """

    __tablename__ = "prediction"

    # Colonnes
    id_prediction = Column(BigInteger, primary_key=True, autoincrement=True)

    # Système polymorphe de territoire (comme resultat_participation/candidat/indicateur)
    id_territoire = Column(String(15), nullable=False, comment="ID polymorphe du territoire")
    type_territoire = Column(String(20), nullable=False, comment="Type de territoire")

    candidat = Column(String(100), nullable=False, comment="Nom candidat prédit")
    parti = Column(String(50), nullable=True, comment="Parti politique")
    annee_prediction = Column(Integer, default=2027, nullable=True, comment="Année prédite")
    tour = Column(Integer, nullable=False, comment="Tour prédit (1 ou 2)")
    pourcentage_predit = Column(Numeric(5, 2), nullable=False, comment="% voix prédit")
    intervalle_confiance_inf = Column(Numeric(5, 2), nullable=True, comment="Borne inf IC 95%")
    intervalle_confiance_sup = Column(Numeric(5, 2), nullable=True, comment="Borne sup IC 95%")
    modele_utilise = Column(String(50), nullable=False, comment="Nom du modèle ML")
    version_modele = Column(String(20), nullable=True, comment="Version modèle (ex: v1.2.0)")
    metriques_modele = Column(JSONB, nullable=True, comment="R², MAE, RMSE, etc.")
    features_utilisees = Column(JSONB, nullable=True, comment="Liste features ML")
    date_generation = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Contraintes
    __table_args__ = (
        # CHECK constraints
        CheckConstraint("tour IN (1, 2)", name='ck_prediction_tour'),
        CheckConstraint("annee_prediction BETWEEN 2025 AND 2050", name='ck_prediction_annee'),
        CheckConstraint("pourcentage_predit BETWEEN 0 AND 100", name='ck_prediction_pct'),
        CheckConstraint("intervalle_confiance_inf BETWEEN 0 AND 100", name='ck_prediction_ic_inf'),
        CheckConstraint("intervalle_confiance_sup BETWEEN 0 AND 100", name='ck_prediction_ic_sup'),
        CheckConstraint(
            "type_territoire IN ('BUREAU', 'CANTON', 'COMMUNE', 'ARRONDISSEMENT', 'DEPARTEMENT', 'REGION', 'NATIONAL')",
            name='ck_prediction_type_territoire'
        ),
        # Contrainte unicité (versioning + type_territoire)
        UniqueConstraint(
            'id_territoire', 'type_territoire', 'candidat', 'tour', 'annee_prediction', 'version_modele',
            name='unique_prediction_territoire_type'
        ),
        # Indexes
        Index('idx_prediction_territoire', 'id_territoire', 'type_territoire'),
        Index('idx_prediction_annee', 'annee_prediction'),
        Index('idx_prediction_modele', 'modele_utilise'),
        Index('idx_prediction_composite', 'id_territoire', 'type_territoire', 'annee_prediction'),
    )

    def __repr__(self):
        return f"<Prediction(territoire='{self.id_territoire}', type_terr='{self.type_territoire}', candidat='{self.candidat}', tour={self.tour}, %={self.pourcentage_predit})>"
