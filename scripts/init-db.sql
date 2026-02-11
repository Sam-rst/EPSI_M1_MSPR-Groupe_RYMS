-- Script d'initialisation PostgreSQL - Electio-Analytics
-- Exécuté automatiquement au premier démarrage du conteneur

-- Activer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS postgis;          -- Données géospatiales
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- Génération UUID
CREATE EXTENSION IF NOT EXISTS btree_gin;        -- Index GIN sur types standards

-- Configuration PostgreSQL optimisée pour analytics
ALTER DATABASE electio_analytics SET timezone TO 'Europe/Paris';

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '✅ Base de données Electio-Analytics initialisée avec succès';
    RAISE NOTICE '   - Extension PostGIS activée';
    RAISE NOTICE '   - Extension UUID activée';
    RAISE NOTICE '   - Timezone: Europe/Paris';
END $$;
