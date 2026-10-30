# Guide d'Extensibilité - respysive-slide

Ce guide explique comment étendre respysive-slide avec de nouveaux handlers et bibliothèques externes.

## Architecture des Handlers

### Système de Handlers Modulaire

Le système de handlers permet d'ajouter facilement de nouveaux types de contenu :

1. **Détection Automatique** : Le `ContentDetector` analyse le contenu et trouve le handler approprié
2. **Priorité** : Les handlers avec une priorité plus basse sont traités en premier
3. **Extensibilité** : Nouveaux handlers peuvent être ajoutés sans modifier le code existant

### Handlers Existants

| Handler | Priorité | Détecte | Utilise |
|---------|----------|---------|---------|
| `MappyngHandler` | 7 | `mappyng.Map` / `mappyng.InteractiveMap` (SVG natif) | `to_string()` / `_repr_html_()` |
| `CustomJsonHandler` | 5 | Configuration JSON avec 'library' et 'config' | CDN externes |
| `MatplotlibHandler` | 10 | `matplotlib.figure.Figure` | `add_fig()` |
| `PlotlyHandler` | 20 | Dict/JSON avec structure Plotly | `add_plotly()` |
| `AltairHandler` | 30 | JSON avec schema vega-lite | `add_altair()` |
| `ImageHandler` | 40 | Fichiers/URLs d'images | `add_image()` |
| `LatexHandler` | 50 | Texte avec $, #, *, _, [ | Traitement markdown+LaTeX |
| `TextHandler` | 100 | Tout contenu (fallback) | `add_text()` ou `add_div()` |

## Créer un Nouveau Handler

### 1. Structure de Base

```python
from respysive.handlers.base import BaseHandler
from typing import Any, Optional


class MonNouveauHandler(BaseHandler):
    @property
    def priority(self) -> int:
        return 25  # Priorité personnalisée

    def can_handle(self, content: Any) -> bool:
        """Vérifie si ce handler peut traiter le contenu"""
        # Logique de détection
        return isinstance(content, MonTypePersonnalise)

    def handle(self, content: Any, shared_data_id: Optional[str] = None, **kwargs) -> str:
        """Traite le contenu et retourne du HTML"""
        # Traitement du contenu
        html = f"<div>Contenu traité: {content}</div>"
        return html
```

### 2. Enregistrement du Handler

```python
# Dans __init__ de la classe Slide
from respysive.handlers import MonNouveauHandler


class Slide:
    def __init__(self, center=False, **kwargs):
        # ... code existant ...

        # Ajouter le nouveau handler
        self._content_detector.register_handler(MonNouveauHandler, self.content_obj)
```

### 3. Exemple Concret : Handler CSV

```python
import pandas as pd
from respysive.handlers.base import BaseHandler


class CsvHandler(BaseHandler):
    @property
    def priority(self) -> int:
        return 35

    def can_handle(self, content) -> bool:
        if isinstance(content, str) and content.endswith(".csv"):
            return True
        return isinstance(content, pd.DataFrame)

    def handle(self, content, shared_data_id=None, **kwargs) -> str:
        if isinstance(content, str):
            df = pd.read_csv(content)
        else:
            df = content

        # Génère un tableau HTML Bootstrap
        html_table = df.to_html(classes="table table-striped table-responsive")
        return f'<div class="table-responsive">{html_table}</div>'
```

## Intégration de Bibliothèques Externes

### Méthode 1 : Configuration JSON (Recommandée)

Pour des bibliothèques avec API JavaScript simple :

```python
slide.add_custom_content(
    library="observable-plot",
    config={"marks": [{"type": "dot", "data": [1, 2, 3, 4, 5], "x": "data", "y": "data"}], "width": 600, "height": 400},
    cdn={"js": ["https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6"]},
    init_script="Plot.plot({config_placeholder})",
    div_style={"height": "450px"},
)
```

### Méthode 2 : Handler Spécialisé

Pour des intégrations plus complexes :

```python
class ObservablePlotHandler(BaseHandler):
    @property
    def priority(self) -> int:
        return 15

    def can_handle(self, content) -> bool:
        return isinstance(content, dict) and "marks" in content and isinstance(content["marks"], list)

    def handle(self, content, shared_data_id=None, **kwargs) -> str:
        import uuid
        import json

        chart_id = f"plot-{uuid.uuid4()}"
        config_json = json.dumps(content)

        return f"""
        <script src="https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6"></script>
        <div id="{chart_id}" style="height: 400px;"></div>
        <script>
            document.getElementById('{chart_id}')
                .appendChild(Plot.plot({config_json}));
        </script>
        """
```

## Exemples d'Intégration

### 1. Three.js (Visualisation 3D)

```python
slide.add_custom_content(
    library="three-js",
    config={"scene": "basic", "camera": {"position": [0, 5, 10]}, "objects": [{"type": "cube", "color": 0x00FF00}]},
    cdn={"js": ["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"]},
    init_script="""
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(600, 400);
        document.getElementById('{container}').appendChild(renderer.domElement);

        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);

        camera.position.z = 5;

        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    """.replace("{container}", "config.container"),
)
```

### 2. Leaflet (Cartes)

```python
# Configuration JSON pour Leaflet
leaflet_config = {
    "library": "leaflet",
    "config": {
        "center": [48.8566, 2.3522],
        "zoom": 13,
        "tileLayer": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    },
    "cdn": {
        "css": ["https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"],
        "js": ["https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"],
    },
    "init_script": """
        const map = L.map(config.container).setView(config.center, config.zoom);
        L.tileLayer(config.tileLayer).addTo(map);
        L.marker(config.center).addTo(map)
            .bindPopup('Paris, France').openPopup();
    """,
    "div_style": {"height": "400px"},
}

slide.add_content([leaflet_config])
```

## Bonnes Pratiques

### 1. Priorités des Handlers

- **1-10** : Handlers très spécifiques (formats propriétaires)
- **11-30** : Handlers de visualisation (charts, cartes)
- **31-50** : Handlers de contenu général (images, texte enrichi)
- **51-99** : Handlers de texte et formatage
- **100+** : Handlers de fallback

### 2. Gestion d'Erreurs

```python
def handle(self, content, shared_data_id=None, **kwargs) -> str:
    try:
        # Traitement du contenu
        result = self._process_content(content)
        return result
    except Exception as e:
        # Fallback gracieux
        return f'<div class="alert alert-danger">Erreur: {str(e)}</div>'
```

### 3. Performance

- Utiliser des CDN pour les bibliothèques externes
- Lazy loading pour les grandes bibliothèques
- Cache des ressources quand possible

### 4. Compatibilité

- Tester avec différentes versions de navigateurs
- Fournir des fallbacks pour les bibliothèques non disponibles
- Documenter les dépendances requises

## Contribution

Pour contribuer un nouveau handler au projet :

1. **Fork** le repository
2. **Créer** le handler dans `respysive/handlers/`
3. **Ajouter** des tests dans `tests/`
4. **Documenter** l'usage et les exemples
5. **Pull Request** avec description détaillée

Le système modulaire permet d'étendre facilement respysive-slide pour supporter de nouvelles bibliothèques et types de contenu sans compromettre la compatibilité existante.