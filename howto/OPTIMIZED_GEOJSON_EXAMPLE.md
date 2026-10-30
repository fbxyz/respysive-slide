# Système de Cache GeoJSON Optimisé

## Problème résolu

Avant cette optimisation, chaque carte MapLibre intégrait la totalité des données GeoJSON dans son HTML, provoquant :
- **Duplication massive** : Mêmes géométries dupliquées dans chaque carte
- **Taille de fichier énorme** : HTML final très lourd avec données redondantes
- **Performance dégradée** : Chargement lent et consommation mémoire excessive

## Solution implémentée

### 1. Cache côté client
- Les données GeoJSON sont stockées **une seule fois** dans un cache JavaScript
- Chaque carte référence les données via un **ID unique** au lieu de les dupliquer
- Système de **jointure côté client** pour associer données et géométries

### 2. Fonctionnement

```python
from respysive import Presentation, Slide

# 1. Créer la présentation et ajouter les données GeoJSON globalement (UNE SEULE FOIS)
p = Presentation()
p.add_global_geojson(
    "france_regions",
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"code_insee": "75", "name": "Paris"},
                "geometry": {"type": "Polygon", "coordinates": [...]},
            },
            {
                "type": "Feature",
                "properties": {"code_insee": "69", "name": "Lyon"},
                "geometry": {"type": "Polygon", "coordinates": [...]},
            },
        ],
    },
)

# 2. Créer plusieurs cartes avec jointures différentes - AUCUNE DUPLICATION
slide1 = Slide()
slide1.add_maplibre_choropleth_with_data_join(
    center=[2.3, 46.8],
    zoom=6,
    geojson_id="france_regions",  # Référence au cache, pas de données dupliquées
    join_data={"75": {"population": 2200000, "densite": 20000}, "69": {"population": 500000, "densite": 10000}},
    join_key="code_insee",  # Clé de jointure
    color_property="population",
    color_rules=[
        {"operator": ">=", "value": 1000000, "color": "#d73027"},
        {"operator": ">=", "value": 500000, "color": "#fc8d59"},
    ],
)

slide2 = Slide()
slide2.add_maplibre_choropleth_with_data_join(
    center=[2.3, 46.8],
    zoom=6,
    geojson_id="france_regions",  # MÊME référence, ZÉRO duplication
    join_data={"75": {"chomage": 8.5}, "69": {"chomage": 7.2}},
    join_key="code_insee",
    color_property="chomage",  # Différente propriété, même géométrie
    color_rules=[{"operator": ">=", "value": 8, "color": "#d73027"}, {"operator": "<", "value": 8, "color": "#4575b4"}],
)

p.add_slide(slide1)
p.add_slide(slide2)
```

### 3. Avantages

- **Efficacité** : GeoJSON stocké une seule fois, même pour 10+ cartes
- **Performance** : Chargement plus rapide, moins de consommation mémoire
- **Flexibilité** : Jointures dynamiques côté client avec données différentes
- **Compatibilité** : L'ancienne API continue de fonctionner

### 4. Architecture technique

```javascript
// Dans chaque iframe MapLibre, un cache global est créé :
var geojsonCache = {
    "france_regions": "{...géométries...}"  // Stocké UNE SEULE FOIS
};

// Fonction de jointure côté client
function joinDataWithGeometry(geojsonData, dataToJoin, joinKey, valueKey) {
    // Effectue la jointure entre géométries et données
    // Retourne GeoJSON enrichi avec nouvelles propriétés
}

// Au chargement de la carte
function resolveDataReferences() {
    if (config.choropleth._cache_ref) {
        var geojsonData = loadFromCache(config.choropleth._cache_ref);
        if (config.choropleth.joinData) {
            geojsonData = joinDataWithGeometry(
                geojsonData,
                config.choropleth.joinData,
                config.choropleth.joinKey,
                config.choropleth.colorProperty
            );
        }
        config.choropleth.geojson = geojsonData;
    }
}
```

### 5. Comparaison avant/après

**AVANT** (duplication) :
```html
<!-- Carte 1 -->
<iframe>...
var config = {
  choropleth: {
    geojson: {...énormes géométries...}  // 500KB
  }
}
</iframe>

<!-- Carte 2 -->  
<iframe>...
var config = {
  choropleth: {
    geojson: {...mêmes géométries...}    // 500KB dupliqué
  }
}
</iframe>
```

**APRÈS** (cache optimisé) :
```html
<!-- Carte 1 -->
<iframe>...
var geojsonCache = {"regions": {...géométries...}};  // 500KB UNE FOIS
var config = {
  choropleth: {
    _cache_ref: "regions",       // Juste une référence
    joinData: {...données...}    // Petites données spécifiques
  }
}
</iframe>

<!-- Carte 2 -->
<iframe>...  
var geojsonCache = {"regions": {...géométries...}};  // 500KB UNE FOIS
var config = {
  choropleth: {
    _cache_ref: "regions",       // Même référence
    joinData: {...autres...}     // Autres données spécifiques
  }
}
</iframe>
```

### 6. Migration

L'ancien code continue de fonctionner :
```python
# Ancien code (toujours supporté)
slide.add_maplibre_choropleth_map(
    center=[2.3, 46.8],
    zoom=6,
    geojson=huge_geojson_data,  # Duplication
    color_property="population",
)

# Nouveau code optimisé
presentation.add_global_geojson("regions", huge_geojson_data)  # Une fois
slide.add_maplibre_choropleth_with_data_join(
    geojson_id="regions",  # Référence
    join_data={...},  # Jointure
    color_property="population",
)
```

Cette optimisation permet de créer des présentations avec de nombreuses cartes sans exploser la taille du fichier final.