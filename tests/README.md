# Tests pour respysive-slide

Ce répertoire contient la suite de tests complète pour le package respysive-slide.

## Structure des tests

```
tests/
├── __init__.py                 # Package principal des tests
├── conftest.py                 # Configuration pytest et fixtures partagées
├── test_runner.py              # Script de lancement des tests
├── README.md                   # Cette documentation
├── unit/                       # Tests unitaires
│   ├── __init__.py
│   ├── test_slide.py          # Tests pour la classe Slide
│   ├── test_handlers.py       # Tests pour le système de handlers
│   ├── test_presentation.py   # Tests pour la classe Presentation
│   └── test_utilities.py      # Tests pour les utilitaires et données globales
├── integration/               # Tests d'intégration
│   └── __init__.py
└── fixtures/                  # Données de test réutilisables
```

## Lancement des tests

### Méthode 1: Via le script test_runner.py (Recommandée)

```bash
# Tous les tests
python tests/test_runner.py

# Tests unitaires seulement
python tests/test_runner.py --unit-only

# Tests avec verbosité
python tests/test_runner.py --verbose

# Tests avec couverture de code
python tests/test_runner.py --coverage

# Tests spécifiques (par marqueur)
python tests/test_runner.py -m maplibre
python tests/test_runner.py -m "handlers and not slow"

# Test spécifique (fichier ou fonction)
python tests/test_runner.py --test test_slide.py
python tests/test_runner.py --test test_slide.py::TestSlideBasic::test_slide_initialization

# Tests en parallèle (nécessite pytest-xdist)
python tests/test_runner.py --parallel

# Lister les marqueurs disponibles
python tests/test_runner.py --list-markers
```

### Méthode 2: Via pytest directement

```bash
# Depuis la racine du projet
pytest tests/

# Tests unitaires seulement
pytest tests/unit/

# Avec couverture
pytest tests/ --cov=respysive --cov-report=html

# Avec marqueurs
pytest -m maplibre
pytest -m "not slow"
```

## Types de tests

### Tests unitaires (`tests/unit/`)

- **test_slide.py**: Tests pour la classe `Slide`
  - Initialisation de base
  - Ajout de titres et contenu
  - Fonctionnalité des cartes
  - Intégration MapLibre
  - Pages de titre (simple et divisée)

- **test_handlers.py**: Tests pour le système de handlers
  - Détecteur de contenu (`ContentDetector`)
  - Handlers individuels (MapLibre, Plotly, Matplotlib, etc.)
  - Priorités et routage
  - Intégration entre handlers

- **test_presentation.py**: Tests pour la classe `Presentation`
  - Gestion des slides (ajout, insertion, suppression)
  - Données globales GeoJSON
  - Génération HTML
  - Configuration et thèmes
  - Opérations sur fichiers

- **test_utilities.py**: Tests pour les utilitaires
  - Gestion des données globales
  - Parsing des styles CSS
  - Traitement Markdown/LaTeX
  - Classe `Content`

### Marqueurs de tests

Les tests sont organisés avec des marqueurs pytest :

- `unit`: Tests unitaires
- `integration`: Tests d'intégration
- `slow`: Tests lents (à éviter en développement rapide)
- `maplibre`: Tests spécifiques MapLibre
- `handlers`: Tests du système de handlers
- `presentation`: Tests de la classe Presentation
- `slide`: Tests de la classe Slide
- `utilities`: Tests des fonctions utilitaires
- `requires_matplotlib`: Tests nécessitant matplotlib
- `requires_plotly`: Tests nécessitant plotly
- `requires_network`: Tests nécessitant un accès réseau

## Fixtures disponibles

Les fixtures suivantes sont définies dans `conftest.py` :

- `temp_directory`: Répertoire temporaire pour les tests
- `sample_geojson`: Données GeoJSON d'exemple
- `sample_plotly_data`: Données Plotly d'exemple
- `sample_altair_data`: Données Altair d'exemple
- `mock_matplotlib_figure`: Figure matplotlib mockée
- `sample_maplibre_configs`: Configurations MapLibre d'exemple
- `sample_custom_content_configs`: Configurations de contenu personnalisé

## Couverture de code

Pour générer un rapport de couverture :

```bash
# Via le test runner
python tests/test_runner.py --coverage

# Via pytest directement
pytest tests/ --cov=respysive --cov-report=html --cov-report=term-missing
```

Le rapport HTML sera généré dans `htmlcov/index.html`.

## Exemples d'utilisation

### Test d'une fonctionnalité spécifique

```bash
# Tests MapLibre seulement
python tests/test_runner.py -m maplibre -v

# Tests des cartes dans Slide
python tests/test_runner.py --test test_slide.py::TestSlideCards -v
```

### Debugging des tests

```bash
# Tests avec sortie complète et arrêt au premier échec
python tests/test_runner.py --pytest-args "-v -s -x"

# Tests avec pdb en cas d'échec
python tests/test_runner.py --pytest-args "--pdb"
```

### Tests rapides pendant le développement

```bash
# Tests rapides (exclut les tests lents)
python tests/test_runner.py -m "not slow" -q
```

## Ajout de nouveaux tests

### Pour ajouter un test unitaire :

1. Identifiez le fichier approprié dans `tests/unit/`
2. Ajoutez une nouvelle classe ou méthode de test
3. Utilisez les fixtures appropriées
4. Ajoutez des marqueurs si nécessaire

### Exemple :

```python
import pytest
from respysive.container import Slide

class TestSlideNewFeature:
    """Test new slide feature."""
    
    @pytest.mark.unit
    @pytest.mark.slide
    def test_new_feature(self):
        """Test the new feature functionality."""
        slide = Slide()
        # Test implementation
        assert slide.new_feature() == expected_result
```

## Intégration continue

Les tests sont conçus pour fonctionner dans les environnements CI/CD :

- Variables d'environnement : `CI`, `OFFLINE_TESTS`
- Tests réseau désactivés automatiquement
- Gestion des dépendances optionnelles
- Rapports de couverture compatibles

## Dépendances des tests

Tests de base (toujours exécutés) :
- `pytest` 
- `unittest.mock`

Tests étendus (avec dépendances) :
- `matplotlib` (pour tests graphiques)
- `plotly` (pour tests de charts)
- `pytest-cov` (pour couverture)
- `pytest-xdist` (pour exécution parallèle)

## Troubleshooting

### Erreur "Module not found"
```bash
# Assurez-vous d'être dans le répertoire racine du projet
cd /path/to/respysive-slide
python tests/test_runner.py
```

### Tests matplotlib qui échouent
```bash
# Installez matplotlib si nécessaire
pip install matplotlib

# Ou skipper ces tests
python tests/test_runner.py -m "not requires_matplotlib"
```

### Erreurs de permissions
```bash
# Vérifiez les permissions du test runner
chmod +x tests/test_runner.py
```