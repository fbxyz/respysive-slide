# MapLibre - Guide de référence complet

Ce document réunit toutes les fonctionnalités et options disponibles pour les cartes MapLibre dans respysive-slide.

## 🆕 Nouveautés - Optimisation GeoJSON

**Version actuelle** : Support de l'optimisation GeoJSON avec cache côté client

### ✨ Fonctionnalités ajoutées
- **`add_maplibre_choropleth_with_data_join()`** - Nouvelle méthode optimisée
- **Cache global** - `presentation.add_global_geojson()` pour partager les géométries
- **Jointures côté client** - Association dynamique données/géométries en JavaScript
- **Réduction de taille** - Jusqu'à 63% de réduction pour les données importantes

## 🗺️ Table des matières

1. [Configuration de base](#configuration-de-base)
2. [Couches géographiques](#couches-géographiques)
3. [Légendes avancées](#légendes-avancées)
4. [Données partagées et optimisation](#données-partagées-et-optimisation)
5. [Méthodes disponibles](#méthodes-disponibles)
6. [Contrôles et interface](#contrôles-et-interface)
7. [Référence complète des paramètres](#référence-complète-des-paramètres)

---

## 🌍 Configuration de base

### Carte minimale
```python
config = {
    "center": [2.0, 46.0],  # Longitude, latitude
    "zoom": 6,  # Niveau de zoom
}
```

### Carte complète
```python
config = {
    "center": [2.0, 46.0],
    "zoom": 6,
    "style": "https://demotiles.maplibre.org/style.json",  # Style personnalisé
    "openstreetmap": True,  # Utiliser OpenStreetMap au lieu du style par défaut
    "navigation": False,  # Masquer les boutons de navigation (défaut: False)
    "scale": True,  # Afficher l'échelle (défaut: True)
}
```

---

## 🎯 Couches géographiques

### 1. Marqueurs

#### Marqueurs simples
```python
"markers": [
    {
        "coordinates": [2.3522, 48.8566],  # Paris
        "popup": "<strong>Paris</strong><br>Capitale de la France"
    }
]
```

#### Marqueurs avec icônes Font Awesome
```python
"markers": [
    {
        "coordinates": [2.3522, 48.8566],
        "icon": "fas fa-star",            # Classe Font Awesome
        "color": "#FFD700",               # Couleur de fond
        "popup": "<strong>Étoile</strong><br>Lieu remarquable"
    }
]
```

### 2. Lignes

#### Lignes simples
```python
"lines": [
    {
        "coordinates": [
            [2.0, 46.0], [3.0, 47.0], [4.0, 48.0]  # Points de la ligne
        ],
        "color": "#FF6B6B",
        "width": 4,
        "opacity": 0.8,
        "popup": "Itinéraire principal"
    }
]
```

#### Lignes depuis données partagées
```python
"lines": [
    {
        "coordinates": "trajectory_data",  # Référence à shared_data
        "color": "#4ECDC4",
        "width": 3
    }
]
```

### 3. Cercles proportionnels

#### Cercles simples
```python
"circles": [
    {
        "coordinates": [2.3522, 48.8566],
        "value": 2161000,                 # Valeur pour la taille
        "color": "#FF9F43",
        "popup": "<strong>Paris</strong><br>Pop: {value:,}"
    }
],
"minRadius": 5,                          # Rayon minimum
"maxRadius": 50                          # Rayon maximum
```

#### Cercles depuis données partagées
```python
"circles": [
    {
        "coordinates": "city_data",       # Référence à shared_data
        "value": 1000000,                # Valeur par défaut si absente
        "color": "#6C5CE7"
    }
]
```

### 4. Choroplèthes (cartes thématiques)

#### Configuration basique
```python
"choropleth": {
    "geojson": "regions_data",           # Référence à shared_data
    "colorProperty": "population",       # Propriété pour la couleur
    "colorRules": [
        {"operator": ">=", "value": 5000000, "color": "#d73027"},
        {"operator": ">=", "value": 2000000, "color": "#f46d43"},
        {"operator": ">=", "value": 1000000, "color": "#fdae61"},
        {"operator": ">=", "value": 0, "color": "#fee08b"}
    ],
    "defaultColor": "#f7f7f7",
    "popup": "<strong>{name}</strong><br>Population: {population:,}",
    "fillOpacity": 0.7,
    "strokeColor": "#ffffff",
    "strokeWidth": 1,
    "showBorders": True
}
```

---

## 🎨 Légendes avancées

### 1. Configuration du titre

#### Titre et sous-titre séparés (recommandé)
```python
"legend": {
    "title": {
        "main": "Population française",
        "subtitle": "Données INSEE 2023 (millions d'habitants)"
    },
    "titleStyle": {
        "fontSize": "16px",
        "color": "#2c3e50",
        "fontWeight": "bold",
        "textAlign": "center",
        "marginBottom": "6px"
    },
    "subtitleStyle": {
        "fontSize": "12px",
        "color": "#7f8c8d",
        "fontStyle": "italic",
        "textAlign": "center",
        "marginBottom": "12px"
    }
}
```

#### Titre simple (format legacy)
```python
"legend": {
    "title": "Population française\\nDonnées INSEE 2023",
    "titleStyle": {
        "fontSize": "14px",
        "textAlign": "center"
    }
}
```

### 2. Types de légendes

#### Légende discrète (verticale)
```python
"legend": {
    "choropleth": {
        "type": "discrete",
        "items": [
            {"color": "#d73027", "label": "5M+ habitants"},
            {"color": "#f46d43", "label": "2-5M habitants"},
            {"color": "#fdae61", "label": "1-2M habitants"},
            {"color": "#fee08b", "label": "< 1M habitants"}
        ]
    }
}
```

#### Légende en dégradé
```python
"legend": {
    "choropleth": {
        "type": "gradient",
        "colors": ["#fee08b", "#fdae61", "#f46d43", "#d73027"],
        "labels": ["0", "2M", "5M", "10M+"]
    }
}
```

#### Légende horizontale avec bornes continues
```python
"legend": {
    "choropleth": {
        "type": "horizontal",
        "width": 280,                    # Largeur totale
        "height": 30,                    # Hauteur des caissons
        "segmentWidth": 70,              # Largeur fixe par segment (optionnel)
        "labelRotation": 45,             # Rotation des textes (degrés)
        "verticalSpacing": 12,           # Espace caissons ↔ labels (px)
        "horizontalSpacing": 5,          # Espace horizontal entre labels (px)
        "thousandsSeparator": True,      # Séparateurs de milliers
        "separatorSymbol": " ",          # Symbole de séparation
        "ranges": [
            {"min": 0, "max": 1000000, "color": "#fee08b"},
            {"min": 1000000, "max": 2000000, "color": "#fdae61"},
            {"min": 2000000, "max": 5000000, "color": "#f46d43"},
            {"min": 5000000, "max": 10000000, "color": "#d73027"}
        ]
    }
}
```

### 3. Styles et positionnement

#### Style du conteneur
```python
"legend": {
    "style": {
        "maxWidth": "320px",
        "fontSize": "13px",
        "padding": "18px",
        "backgroundColor": "rgba(255, 255, 255, 0.95)",
        "borderRadius": "10px",
        "boxShadow": "0 4px 15px rgba(0,0,0,0.2)",
        # Positionnement personnalisé
        "top": "15px",
        "left": "15px",
        "right": "auto",    # Annuler positionnement par défaut
        "bottom": "auto"
    }
}
```

### 4. Formatage des nombres

```python
"legend": {
    "choropleth": {
        "thousandsSeparator": True,      # Activer les séparateurs (défaut: True)
        "separatorSymbol": " ",          # Symbole de séparation
        # Résultats possibles :
        # " " → 1 500 000 (format français)
        # "," → 1,500,000 (format anglo-saxon)
        # "." → 1.500.000 (format alternatif)
        # False → 1500000 (sans formatage)
    }
}
```

---

## 💾 Données partagées et optimisation

### Principe
Les données partagées permettent de référencer des datasets volumineux (GeoJSON) une seule fois dans la présentation, puis de les réutiliser dans plusieurs cartes avec un **système de cache optimisé** qui évite totalement la duplication.

### 🟢 Méthode optimisée (RECOMMANDÉE)

#### 1. Ajouter les données géographiques globalement
```python
# Dans votre code Python
p = Presentation()
p.add_global_geojson("regions_france", regions_geojson)  # UNE SEULE FOIS
```

#### 2. Créer des cartes avec jointures de données
```python
slide1 = Slide()
slide1.add_maplibre_choropleth_with_data_join(
    center=[2.0, 46.0],
    zoom=6,
    geojson_id="regions_france",  # Référence au cache (pas de duplication)
    join_data={  # Données spécifiques légères
        "75": {"population": 2200000},
        "69": {"population": 520000},
    },
    join_key="code_insee",  # Clé de jointure
    color_property="population",  # Propriété pour coloration
    color_rules=[...],
    popup="Population: {population}",
)

slide2 = Slide()
slide2.add_maplibre_choropleth_with_data_join(
    geojson_id="regions_france",  # MÊME référence, ZÉRO duplication
    join_data={  # Autres données légères
        "75": {"pib": 56500},
        "69": {"pib": 32500},
    },
    join_key="code_insee",
    color_property="pib",  # Autre propriété
    color_rules=[...],
    popup="PIB: {pib}€",
)
```

#### 3. Avantages mesurés
- 🚀 **Performance** : Cache côté client, jointures dynamiques JavaScript
- 💾 **Espace** : **63% de réduction** pour données importantes (test : 15MB → 5MB)
- 🔧 **Flexibilité** : Même géographie, indicateurs multiples
- ⚡ **Maintenance** : Une seule source de vérité géographique

### 🔴 Méthodes traditionnelles (toujours supportées)

#### Avec données directes (pour cartes uniques)
```python
slide.add_maplibre_choropleth_map(
    geojson=geojson_data,  # Données directes
    color_property="population",
)
```

#### Avec shared_data local (méthode legacy)
```python
slide.content_obj.add_shared_data("regions", geojson_data, "geojson")
config = {
    "choropleth": {
        "geojson": "regions"  # Référence locale
    }
}
```

### 📊 Comparaison des méthodes

| Méthode | Cartes multiples | Taille fichier | Performance | Usage recommandé |
|---------|------------------|----------------|-------------|------------------|
| **Optimisée** | ✅ Excellent | ✅ Minimal | 🚀 Maximum | **Production, données importantes** |
| Directe | ❌ Duplication | ❌ Lourd | ⚡ Correct | Prototypage, carte unique |
| Legacy | ⚠️ Duplication partielle | ⚠️ Moyen | ⚡ Correct | Migration progressive |

### 🎯 Quand utiliser chaque méthode ?

#### ✅ Méthode optimisée si :
- **Plusieurs cartes** avec mêmes géométries
- **Données importantes** (> 500 KB GeoJSON)
- **Indicateurs multiples** (population, PIB, chômage...)
- **Présentations de production**

#### ⚡ Méthode traditionnelle si :
- **Carte unique** ou géographies différentes
- **Données légères** (< 100 KB GeoJSON) 
- **Prototypage rapide**

### 🔧 Architecture technique du cache optimisé

```javascript
// Dans chaque iframe MapLibre
var geojsonCache = {
    "regions_france": "{...géométries...}"  // Stocké UNE FOIS
};

// Fonction de jointure côté client
function joinDataWithGeometry(geojsonData, dataToJoin, joinKey, valueKey) {
    // Associe dynamiquement les données aux géométries
    geojsonData.features.forEach(function(feature) {
        var key = feature.properties[joinKey];
        if (dataToJoin[key]) {
            Object.assign(feature.properties, dataToJoin[key]);
        }
    });
    return geojsonData;
}
```

---

## 🛠️ Méthodes disponibles

### Vue d'ensemble
Respysive-slide propose plusieurs méthodes pour créer des cartes MapLibre, chacune adaptée à des cas d'usage spécifiques.

### 🟢 Méthodes optimisées (recommandées)

#### 1. `add_maplibre_choropleth_with_data_join()` - Carte choroplèthe optimisée
```python
slide.add_maplibre_choropleth_with_data_join(
    center=[2.0, 46.0],
    zoom=6,
    geojson_id="regions_france",  # Référence au cache global
    join_data=population_data,  # Données à joindre
    join_key="code_insee",  # Clé de jointure
    color_property="population",  # Propriété pour coloration
    color_rules=[...],
    legend={...},
)
```
**Avantages** : Cache optimisé, jointures côté client, réduction massive de taille
**Usage** : Plusieurs cartes thématiques avec même géographie

#### 2. `presentation.add_global_geojson()` - Cache global
```python
presentation.add_global_geojson("regions", geojson_data)  # UNE FOIS
```
**Avantages** : Données partagées globalement, pas de duplication
**Usage** : À combiner avec les méthodes optimisées

### ⚡ Méthodes traditionnelles (toujours supportées)

#### 3. `add_maplibre_choropleth_map()` - Carte choroplèthe classique
```python
slide.add_maplibre_choropleth_map(
    center=[2.0, 46.0],
    zoom=6,
    geojson=geojson_data,  # Données directes
    color_property="population",
    color_rules=[...],
)
```
**Avantages** : Simple, direct
**Usage** : Carte unique, prototypage

#### 4. `add_maplibre_map()` - Carte de base avec marqueurs
```python
slide.add_maplibre_map(center=[2.0, 46.0], zoom=6, markers=[...], legend={...})
```
**Usage** : Cartes avec marqueurs, points d'intérêt

#### 5. `add_maplibre_lines_map()` - Carte avec lignes
```python
slide.add_maplibre_lines_map(center=[2.0, 46.0], zoom=6, lines=[...], markers=[...])
```
**Usage** : Trajets, réseaux, connexions

#### 6. `add_maplibre_circles_map()` - Carte avec cercles proportionnels
```python
slide.add_maplibre_circles_map(center=[2.0, 46.0], zoom=6, circles=[...], min_radius=5, max_radius=50)
```
**Usage** : Données quantitatives, populations, volumes

### 📊 Comparaison des méthodes

| Méthode | Optimisation | Cas d'usage | Complexité | Performance |
|---------|--------------|-------------|------------|-------------|
| `add_maplibre_choropleth_with_data_join` | ✅ Maximum | Cartes multiples thématiques | Moyenne | 🚀 Excellent |
| `add_maplibre_choropleth_map` | ❌ Aucune | Carte choroplèthe unique | Faible | ⚡ Bon |
| `add_maplibre_map` | ❌ Aucune | Marqueurs, POI | Faible | ⚡ Bon |
| `add_maplibre_lines_map` | ⚠️ Partielle | Trajets, réseaux | Faible | ⚡ Bon |
| `add_maplibre_circles_map` | ⚠️ Partielle | Données quantitatives | Faible | ⚡ Bon |

### 🎯 Guide de choix de méthode

#### Pour des cartes thématiques multiples :
1. `presentation.add_global_geojson('id', geojson)` 
2. `slide.add_maplibre_choropleth_with_data_join(geojson_id='id', ...)`

#### Pour une carte thématique unique :
`slide.add_maplibre_choropleth_map(geojson=data, ...)`

#### Pour des marqueurs/POI :
`slide.add_maplibre_map(markers=[...], ...)`

#### Pour des trajets :
`slide.add_maplibre_lines_map(lines=[...], ...)`

#### Pour des données quantitatives ponctuelles :
`slide.add_maplibre_circles_map(circles=[...], ...)`

---

## 🎛️ Contrôles et interface

### Contrôles de navigation
```python
"navigation": False,  # Masquer boutons zoom +/- et boussole (défaut: False)
"navigation": True    # Afficher les contrôles
```

### Échelle
```python
"scale": True,        # Afficher l'échelle métrique (défaut: True)
"scale": False        # Masquer l'échelle
```

### Popups interactifs
```python
# Variables disponibles dans les templates de popup
"popup": "<strong>{name}</strong><br>Population: {population:,}<br>Densité: {density} hab/km²"

# Pour les choroplèthes, toutes les propriétés GeoJSON sont disponibles
# Pour les cercles/lignes, utilisez les propriétés définies dans vos données
```

---

## 📚 Référence complète des paramètres

### Configuration générale
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `center` | `[float, float]` | `[0, 0]` | Coordonnées du centre [longitude, latitude] |
| `zoom` | `int` | `2` | Niveau de zoom initial |
| `style` | `string` | MapLibre défaut | URL du style de carte |
| `openstreetmap` | `bool` | `False` | Utiliser OpenStreetMap |
| `navigation` | `bool` | `False` | Afficher les contrôles de navigation |
| `scale` | `bool` | `True` | Afficher l'échelle |

### Marqueurs
| Paramètre | Type | Description |
|-----------|------|-------------|
| `coordinates` | `[float, float]` | Position du marqueur |
| `icon` | `string` | Classe Font Awesome (ex: `"fas fa-star"`) |
| `color` | `string` | Couleur de fond (ex: `"#FF6B6B"`) |
| `popup` | `string` | Contenu HTML du popup |

### Lignes
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `coordinates` | `array` ou `string` | - | Points de la ligne ou référence shared_data |
| `color` | `string` | `"#3b82f6"` | Couleur de la ligne |
| `width` | `int` | `3` | Épaisseur en pixels |
| `opacity` | `float` | `0.8` | Transparence (0-1) |
| `popup` | `string` | - | Contenu du popup |

### Cercles
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `coordinates` | `[float, float]` ou `string` | - | Position ou référence shared_data |
| `value` | `float` | `1` | Valeur pour calculer la taille |
| `color` | `string` | `"#3b82f6"` | Couleur de remplissage |
| `opacity` | `float` | `0.6` | Transparence du remplissage |
| `strokeWidth` | `int` | `2` | Épaisseur du contour |
| `strokeColor` | `string` | `"#ffffff"` | Couleur du contour |
| `popup` | `string` | - | Contenu du popup |
| `minRadius` | `int` | `5` | Rayon minimum (global) |
| `maxRadius` | `int` | `50` | Rayon maximum (global) |

### Choroplèthes - Méthode traditionnelle
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `geojson` | `string` ou `object` | - | Référence shared_data ou données directes |
| `colorProperty` | `string` | - | Propriété pour la couleur |
| `colorRules` | `array` | - | Règles de couleur |
| `defaultColor` | `string` | `"#cccccc"` | Couleur par défaut |
| `fillOpacity` | `float` | `0.7` | Transparence du remplissage |
| `strokeColor` | `string` | `"#ffffff"` | Couleur des bordures |
| `strokeWidth` | `int` | `1` | Épaisseur des bordures |
| `showBorders` | `bool` | `True` | Afficher les bordures |
| `popup` | `string` | - | Template du popup |

### Choroplèthes - Méthode optimisée (add_maplibre_choropleth_with_data_join)
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `center` | `[float, float]` | - | Centre de la carte [longitude, latitude] |
| `zoom` | `int` | `10` | Niveau de zoom |
| `geojson_id` | `string` | - | **Référence au cache global** (add_global_geojson) |
| `join_data` | `dict` | - | **Données à joindre** {clé: {propriétés}} |
| `join_key` | `string` | - | **Clé de jointure** dans le GeoJSON |
| `color_property` | `string` | - | Propriété pour la couleur (après jointure) |
| `color_rules` | `array` | - | Règles de couleur |
| `legend` | `dict` | - | Configuration de la légende |
| `openstreetmap` | `bool` | `False` | Utiliser OpenStreetMap |
| `scale` | `bool` | `True` | Afficher l'échelle |
| `navigation` | `bool` | `True` | Afficher les contrôles |
| `popup` | `string` | - | Template du popup |
| `columns` | `list` | `[12]` | Layout Bootstrap |
| `styles` | `list` | - | Styles CSS et classes |

### Légendes - Structure générale
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `title` | `string` ou `object` | - | Titre de la légende |
| `title.main` | `string` | - | Titre principal (nouveau format) |
| `title.subtitle` | `string` | - | Sous-titre (nouveau format) |
| `style` | `object` | - | Styles CSS du conteneur |
| `titleStyle` | `object` | - | Styles CSS du titre |
| `subtitleStyle` | `object` | - | Styles CSS du sous-titre |

### Légendes - Type horizontal
| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `type` | `string` | - | `"horizontal"` pour légende horizontale |
| `width` | `int` | `200` | Largeur totale en pixels |
| `height` | `int` | `20` | Hauteur des caissons en pixels |
| `segmentWidth` | `int` | calculé | Largeur fixe de chaque segment |
| `labelRotation` | `int` | `0` | Rotation des labels en degrés |
| `verticalSpacing` | `int` | `8` | Espace caissons ↔ labels (px) |
| `horizontalSpacing` | `int` | `0` | Espace horizontal entre labels (px) |
| `thousandsSeparator` | `bool` | `True` | Formatage des nombres |
| `separatorSymbol` | `string` | `" "` | Symbole de séparation |
| `ranges` | `array` | - | Tranches de valeurs |

### Règles de couleur (colorRules)
```python
{
    "operator": ">=",  # Opérateurs: >=, >, <=, <, ==
    "value": 1000000,  # Valeur de comparaison
    "color": "#d73027",  # Couleur résultante
}
```

### Styles CSS supportés

#### Pour `legend.style` (conteneur)
- Dimensions : `width`, `maxWidth`, `height`
- Typographie : `fontSize`, `lineHeight`, `fontFamily`
- Espacement : `padding`, `margin`, `marginTop`, etc.
- Apparence : `backgroundColor`, `background`, `borderRadius`, `border`, `boxShadow`
- Position : `top`, `bottom`, `left`, `right`, `position`

#### Pour `legend.titleStyle` et `legend.subtitleStyle`
- Typographie : `fontSize`, `color`, `fontWeight`, `fontStyle`, `textAlign`
- Espacement : `marginBottom`, `marginTop`, `padding`
- Décoration : `textDecoration`, `letterSpacing`, `textTransform`

---

## 🎯 Exemples d'usage complets

### 🟢 Carte optimisée avec réutilisation (RECOMMANDÉ)
```python
from respysive import Presentation, Slide

# Données géographiques
regions_data = { /* GeoJSON des régions françaises */ }

# 1. Ajouter les données UNE SEULE FOIS
p = Presentation()
p.add_global_geojson("regions_france", regions_data)

# 2. Première carte : Population
slide1 = Slide()
slide1.add_title("Population par région")
slide1.add_maplibre_choropleth_with_data_join(
    center=[2.0, 46.0], zoom=6,
    geojson_id='regions_france',           # Référence au cache
    join_data={                            # Données spécifiques
        '75': {'population': 2200000, 'densite': 1030},
        '69': {'population': 520000, 'densite': 113},
        '13': {'population': 870000, 'densite': 161}
    },
    join_key='code_insee',
    color_property='population',
    color_rules=[
        {'operator': '>=', 'value': 1000000, 'color': '#d73027'},
        {'operator': '>=', 'value': 500000, 'color': '#fc8d59'},
        {'operator': '<', 'value': 500000, 'color': '#fee08b'}
    ],
    legend={
        "title": "Population 2024",
        "choropleth": {
            "type": "discrete",
            "items": [
                {"color": "#d73027", "label": "> 1M habitants"},
                {"color": "#fc8d59", "label": "500k - 1M habitants"},
                {"color": "#fee08b", "label": "< 500k habitants"}
            ]
        }
    },
    popup="<b>{nom}</b><br>Population: {population:,}<br>Densité: {densite} hab/km²"
)

# 3. Deuxième carte : PIB (MÊME géométrie, ZÉRO duplication)
slide2 = Slide()
slide2.add_title("PIB par habitant")
slide2.add_maplibre_choropleth_with_data_join(
    geojson_id='regions_france',           # MÊME référence
    join_data={                            # Autres données
        '75': {'pib_hab': 56500},
        '69': {'pib_hab': 32500},
        '13': {'pib_hab': 31200}
    },
    join_key='code_insee',
    color_property='pib_hab',              # Autre propriété
    color_rules=[
        {'operator': '>=', 'value': 50000, 'color': '#1a9850'},
        {'operator': '>=', 'value': 35000, 'color': '#91bfdb'},
        {'operator': '<', 'value': 35000, 'color': '#f46d43'}
    ],
    popup="<b>{nom}</b><br>PIB/hab: {pib_hab:,} €"
)

p.add_slide(slide1)
p.add_slide(slide2)
```

### 🔴 Carte traditionnelle avec create_choropleth (toujours supporté)

```python
from respysive import Presentation, Slide
from temp.maplibre_choro import create_choropleth

# Données (normalement chargées depuis un fichier)
regions_data = { / * GeoJSON
des
régions * /}

# Ajouter les données globalement
p = Presentation()
p.add_global_geojson("regions", regions_data)

# Créer la configuration choroplèthe
color_mapping = {
    'A': {"color": "#67001f", "label": "Plus de 8M hab."},
    'B': {"color": "#b2182b", "label": "5-8M hab."},
    'C': {"color": "#d6604d", "label": "3-5M hab."},
    'D': {"color": "#f4a582", "label": "1-3M hab."},
    'E': {"color": "#fddbc7", "label": "Moins de 1M hab."}
}

choro_config = create_choropleth(
    color_column='population_class',
    color_mapping=color_mapping,
    use_shared_data=True,
    shared_data_id="regions",
    legend_title={"main": "Population par région", "subtitle": "France métropolitaine - INSEE 2023"},
    popup_template="<strong>{nom}</strong><br>Population: {population:,}"
)

config = {
    "center": [2.0, 46.0],
    "zoom": 6,
    "openstreetmap": True,
    "navigation": False,
    "choropleth": choro_config['choropleth'],
    "legend": choro_config['legend']
}

slide = Slide()
slide.add_content([config], columns=[12], shared_data_ids=["regions"])
```

### Carte multi-couches
```python
config = {
    "center": [2.3522, 48.8566],
    "zoom": 10,
    "openstreetmap": True,
    
    # Fond choroplèthe
    "choropleth": {
        "geojson": "arrondissements",
        "colorProperty": "income",
        "colorRules": [/* ... */]
    },
    
    # Points d'intérêt
    "markers": [
        {
            "coordinates": [2.3522, 48.8566],
            "icon": "fas fa-monument",
            "color": "#FFD700",
            "popup": "Tour Eiffel"
        }
    ],
    
    # Lignes de transport
    "lines": [
        {
            "coordinates": "metro_line_1",
            "color": "#FFCD00",
            "width": 4,
            "popup": "Métro Ligne 1"
        }
    ],
    
    # Stations importantes
    "circles": [
        {
            "coordinates": [2.3488, 48.8534],
            "value": 50000,
            "color": "#FF6B6B",
            "popup": "Gare du Nord<br>Trafic: 50k/jour"
        }
    ]
}
```

---

## 📋 Checklist de validation

Avant de finaliser votre carte, vérifiez :

### Données
- [ ] Les coordonnées sont au format [longitude, latitude]
- [ ] Les données GeoJSON sont valides
- [ ] Les références shared_data existent
- [ ] Les propriétés utilisées dans colorProperty et popups existent

### Légende
- [ ] Le type de légende correspond aux données
- [ ] Les couleurs de la légende correspondent aux colorRules
- [ ] Les plages de valeurs couvrent toutes les données
- [ ] Le formatage des nombres est approprié

### Apparence
- [ ] La carte est centrée correctement
- [ ] Le niveau de zoom est adapté
- [ ] Les couleurs sont accessibles (contraste suffisant)
- [ ] Les textes sont lisibles
- [ ] La légende ne masque pas d'éléments importants

### Performance  
- [ ] Les données voluminuses utilisent le système shared_data
- [ ] Les popups ne contiennent pas de HTML complexe
- [ ] Le nombre de marqueurs/cercles reste raisonnable (< 1000)

---

*Ce guide couvre toutes les fonctionnalités disponibles dans respysive-slide v1.x pour MapLibre. Pour des besoins spécifiques non couverts, consultez la documentation MapLibre GL JS officielle.*