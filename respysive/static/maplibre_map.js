// MapLibre map drawn inside an iframe. respysive defines `config` (the map
// options) and `geojsonCache` (GeoJSON strings keyed by id) before this script.

// GeoJSON stored on the slide, or once for the deck with add_global_geojson
// (a hidden element of the parent page, which shares the iframe's origin)
function loadFromCache(cacheRef) {
    var text = geojsonCache[cacheRef];
    if (text === undefined) {
        try {
            var element = window.parent.document.getElementById(cacheRef);
            text = element ? element.textContent : undefined;
        } catch (e) {
            text = undefined;
        }
    }
    if (text === undefined) {
        console.warn('respysive: GeoJSON not found:', cacheRef);
        return null;
    }
    try {
        return JSON.parse(text);
    } catch (e) {
        console.error('respysive: invalid GeoJSON for', cacheRef, e);
        return null;
    }
}

// Copy the properties of joined records into the matching features
function joinDataWithGeometry(geojsonData, dataToJoin, joinKey, valueKey) {
    if (!geojsonData || !geojsonData.features || !dataToJoin) return geojsonData;

    var dataIndex = {};
    if (Array.isArray(dataToJoin)) {
        dataToJoin.forEach(function(item) {
            if (item[joinKey] !== undefined) {
                dataIndex[item[joinKey]] = item;
            }
        });
    } else if (typeof dataToJoin === 'object') {
        dataIndex = dataToJoin;
    }

    geojsonData.features.forEach(function(feature) {
        var featureKey = feature.properties[joinKey];
        if (featureKey !== undefined && dataIndex[featureKey]) {
            Object.assign(feature.properties, dataIndex[featureKey]);
            if (valueKey && dataIndex[featureKey][valueKey] !== undefined) {
                feature.properties[valueKey] = dataIndex[featureKey][valueKey];
            }
        }
    });

    return geojsonData;
}

// Minimum, median and maximum of the circle values, for the legend
function calculateCircleStats(circles) {
    if (!circles || circles.length === 0) return null;

    var values = circles.map(function(circle) {
        return circle.value || 1;
    });

    values = values.filter(function(v) { return v !== undefined && v !== null; });
    values.sort(function(a, b) { return a - b; });

    if (values.length === 0) return { min: 1, median: 1, max: 1 };

    var min = values[0];
    var max = values[values.length - 1];
    var median = values.length % 2 === 0
        ? (values[values.length / 2 - 1] + values[values.length / 2]) / 2
        : values[Math.floor(values.length / 2)];

    return { min: min, median: median, max: max };
}

// Radius proportional to the square root of the value, so area follows value
function calculateRadius(value, minValue, maxValue, minRadius, maxRadius) {
    if (minValue === maxValue) return (minRadius + maxRadius) / 2;

    var normalizedValue = Math.sqrt(value) / Math.sqrt(maxValue);
    return minRadius + (maxRadius - minRadius) * normalizedValue;
}


// Function to resolve cache references client-side
function resolveDataReferences() {
    // Resolve choropleth references
    if (config.choropleth && config.choropleth._cache_ref) {
        var geojsonData = loadFromCache(config.choropleth._cache_ref);
        if (geojsonData) {
            if (config.choropleth.joinData && config.choropleth.joinKey) {
                geojsonData = joinDataWithGeometry(
                    geojsonData,
                    config.choropleth.joinData,
                    config.choropleth.joinKey,
                    config.choropleth.colorProperty
                );
            }
            config.choropleth.geojson = geojsonData;
        }
        delete config.choropleth._cache_ref;
    }

    // Resolve line references
    if (config.lines) {
        config.lines.forEach(function(line, index) {
            if (line._cache_ref) {
                var geojsonData = loadFromCache(line._cache_ref);
                if (geojsonData && geojsonData.features && geojsonData.features[0] && geojsonData.features[0].geometry) {
                    config.lines[index].coordinates = geojsonData.features[0].geometry.coordinates;
                }
                delete config.lines[index]._cache_ref;
            }
        });
    }

    // Resolve circle references
    if (config.circles) {
        config.circles.forEach(function(circle, index) {
            if (circle._cache_ref) {
                var geojsonData = loadFromCache(circle._cache_ref);
                if (geojsonData && geojsonData.features && geojsonData.features[0] && geojsonData.features[0].geometry) {
                    config.circles[index].coordinates = geojsonData.features[0].geometry.coordinates;
                    // Get value from properties if not defined
                    if (config.circles[index].value === undefined && geojsonData.features[0].properties) {
                        config.circles[index].value = geojsonData.features[0].properties.value || 1;
                    }
                }
                delete config.circles[index]._cache_ref;
            }
        });
    }
}

// Function to create legend dynamically
function createLegend() {
    var legendContainer = document.getElementById('legend-container');
    if (!config.legend || !legendContainer) return;

    var legendDiv = document.createElement('div');
    legendDiv.className = 'legend';

    // Apply custom legend styles if specified
    if (config.legend.style) {
        Object.keys(config.legend.style).forEach(function(styleProp) {
            legendDiv.style[styleProp] = config.legend.style[styleProp];
        });
    }

    // Handle titles with separate main title and subtitle
    if (config.legend.title && typeof config.legend.title === 'object') {
        // Title and subtitle given separately
        if (config.legend.title.main) {
            var mainTitle = document.createElement('div');
            mainTitle.className = 'legend-title';
            mainTitle.textContent = config.legend.title.main;

            // Apply custom styles to main title
            if (config.legend.titleStyle) {
                Object.keys(config.legend.titleStyle).forEach(function(styleProp) {
                    mainTitle.style[styleProp] = config.legend.titleStyle[styleProp];
                });
            }

            legendDiv.appendChild(mainTitle);
        }

        if (config.legend.title.subtitle) {
            var subtitle = document.createElement('div');
            subtitle.className = 'legend-subtitle';
            subtitle.textContent = config.legend.title.subtitle;

            // Apply custom styles to subtitle
            if (config.legend.subtitleStyle) {
                Object.keys(config.legend.subtitleStyle).forEach(function(styleProp) {
                    subtitle.style[styleProp] = config.legend.subtitleStyle[styleProp];
                });
            }

            legendDiv.appendChild(subtitle);
        }
    } else {
        // Legacy format with simple title (pre-processed Python-side)
        var titleDiv = document.createElement('div');
        titleDiv.className = 'legend-title';

        var title = config.legend.title;
        if (config.legend._useHTML) {
            titleDiv.innerHTML = title;
        } else {
            titleDiv.textContent = title;
            // CSS white-space: pre-line automatically handles \n
        }

        // Apply custom styles to title if specified
        if (config.legend.titleStyle) {
            Object.keys(config.legend.titleStyle).forEach(function(styleProp) {
                titleDiv.style[styleProp] = config.legend.titleStyle[styleProp];
            });
        }

        legendDiv.appendChild(titleDiv);
    }

    // Handle choropleth maps
    if (config.choropleth && config.legend && config.legend.choropleth) {
        var choroplethDiv = document.createElement('div');
        choroplethDiv.className = 'legend-choropleth';

        if (config.legend.choropleth.type === 'discrete') {
            // Discrete legend with fixed colors
            config.legend.choropleth.items.forEach(function(item) {
                var itemDiv = document.createElement('div');
                itemDiv.className = 'legend-color-item';

                var colorBox = document.createElement('div');
                colorBox.className = 'legend-color-box';
                colorBox.style.backgroundColor = item.color;

                var label = document.createElement('span');
                label.textContent = item.label;
                label.style.fontSize = '12px';

                itemDiv.appendChild(colorBox);
                itemDiv.appendChild(label);
                choroplethDiv.appendChild(itemDiv);
            });
        } else if (config.legend.choropleth.type === 'gradient') {
            // Gradient legend
            var gradientDiv = document.createElement('div');
            gradientDiv.className = 'legend-gradient';

            var colors = config.legend.choropleth.colors;
            var gradientCss = 'linear-gradient(to right, ' + colors.join(', ') + ')';
            gradientDiv.style.background = gradientCss;

            var labelsDiv = document.createElement('div');
            labelsDiv.className = 'legend-gradient-labels';

            config.legend.choropleth.labels.forEach(function(label) {
                var labelSpan = document.createElement('span');
                labelSpan.textContent = label;
                labelsDiv.appendChild(labelSpan);
            });

            choroplethDiv.appendChild(gradientDiv);
            choroplethDiv.appendChild(labelsDiv);
        } else if (config.legend.choropleth.type === 'horizontal') {
            // Horizontal legend with connected boxes and continuous bounds
            var horizontalDiv = document.createElement('div');
            horizontalDiv.className = 'legend-horizontal';

            var barDiv = document.createElement('div');
            barDiv.className = 'legend-horizontal-bar';

            // Create colored segments
            var ranges = config.legend.choropleth.ranges || [];
            var totalWidth = config.legend.choropleth.width || 200;
            var segmentHeight = config.legend.choropleth.height || 20;
            var segmentWidth = config.legend.choropleth.segmentWidth || (totalWidth / ranges.length);

            ranges.forEach(function(range, index) {
                var segment = document.createElement('div');
                segment.className = 'legend-horizontal-segment';
                segment.style.backgroundColor = range.color;
                segment.style.height = segmentHeight + 'px';
                segment.style.width = segmentWidth + 'px';
                barDiv.appendChild(segment);
            });

            // Create labels with continuous bounds
            var labelsDiv = document.createElement('div');
            labelsDiv.className = 'legend-horizontal-labels';
            // Adjust width according to actual segments
            var actualTotalWidth = segmentWidth * ranges.length;
            labelsDiv.style.width = actualTotalWidth + 'px';

            // Apply custom spacings
            var verticalSpacing = config.legend.choropleth.verticalSpacing || 8;
            var horizontalSpacing = config.legend.choropleth.horizontalSpacing || 0;
            labelsDiv.style.marginTop = verticalSpacing + 'px';
            labelsDiv.style.gap = horizontalSpacing + 'px';

            // Extract unique values from bounds
            var values = [];
            ranges.forEach(function(range, index) {
                if (index === 0) values.push(range.min);
                values.push(range.max);
            });

            // Position labels with optional rotation
            var labelRotation = config.legend.choropleth.labelRotation || 0;
            var useThousandsSeparator = config.legend.choropleth.thousandsSeparator !== false;
            var separator = config.legend.choropleth.separatorSymbol || ' ';

            values.forEach(function(value, index) {
                var label = document.createElement('span');
                label.className = 'legend-horizontal-label';

                // Format number with thousands separator if enabled
                var displayValue = value;
                if (useThousandsSeparator && typeof value === 'number' && value >= 1000) {
                    displayValue = value.toLocaleString('fr-FR').replace(/\\s/g, separator);
                }

                label.textContent = displayValue;

                // Calculate position (0% for first, 100% for last)
                var position = (index / (values.length - 1)) * 100;
                label.style.left = position + '%';

                // Apply rotation if specified
                if (labelRotation !== 0) {
                    label.style.transform = 'translateX(-50%) rotate(' + labelRotation + 'deg)';
                }

                labelsDiv.appendChild(label);
            });

            horizontalDiv.appendChild(barDiv);
            horizontalDiv.appendChild(labelsDiv);
            choroplethDiv.appendChild(horizontalDiv);
        }

        legendDiv.appendChild(choroplethDiv);
    }

    // Handle proportional circles
    if (config.circles && config.circles.length > 0) {
        var stats = calculateCircleStats(config.circles);
        var minRadius = config.minRadius || 5;
        var maxRadius = config.maxRadius || 50;

        var circlesDiv = document.createElement('div');
        circlesDiv.className = 'legend-circles';

        var values = [stats.min, stats.median, stats.max];
        var labels = ['Min', 'Median', 'Max'];
        var circleColor = config.circles[0].color || '#3b82f6';

        values.forEach(function(value, index) {
            var radius = calculateRadius(value, stats.min, stats.max, minRadius, maxRadius);
            var legendRadius = Math.max(2, radius * 0.4); // Reduced scale for legend

            var itemDiv = document.createElement('div');
            itemDiv.className = 'legend-circle-item';

            var circleDiv = document.createElement('div');
            circleDiv.className = 'legend-circle';
            circleDiv.style.width = (legendRadius * 2) + 'px';
            circleDiv.style.height = (legendRadius * 2) + 'px';
            circleDiv.style.borderColor = circleColor;
            circleDiv.style.backgroundColor = circleColor + '40'; // Transparence

            var labelDiv = document.createElement('div');
            labelDiv.textContent = labels[index];
            labelDiv.style.fontSize = '10px';
            labelDiv.style.textAlign = 'center';
            labelDiv.style.marginTop = '2px';

            var valueDiv = document.createElement('div');
            valueDiv.textContent = Math.round(value).toLocaleString();
            valueDiv.style.fontSize = '9px';
            valueDiv.style.textAlign = 'center';
            valueDiv.style.color = '#666';

            itemDiv.appendChild(circleDiv);
            itemDiv.appendChild(labelDiv);
            itemDiv.appendChild(valueDiv);
            circlesDiv.appendChild(itemDiv);
        });

        legendDiv.appendChild(circlesDiv);
    }

    // Handle other legend elements
    if (config.legend.items) {
        config.legend.items.forEach(function(item) {
            var itemDiv = document.createElement('div');
            itemDiv.className = 'legend-item';

            if (item.type === 'line') {
                var lineDiv = document.createElement('div');
                lineDiv.className = 'legend-line';
                lineDiv.style.backgroundColor = item.color;
                lineDiv.style.height = (item.width || 3) + 'px';
                itemDiv.appendChild(lineDiv);
            } else if (item.icon) {
                var iconElement = document.createElement('i');
                iconElement.className = item.icon;
                iconElement.style.color = item.color;
                iconElement.className += ' legend-icon';
                itemDiv.appendChild(iconElement);
            }

            var labelSpan = document.createElement('span');
            labelSpan.textContent = ' ' + item.label;
            itemDiv.appendChild(labelSpan);

            legendDiv.appendChild(itemDiv);
        });
    }

    legendContainer.appendChild(legendDiv);
}

var map = new maplibregl.Map({
    container: 'map',
    style: config.style,
    center: config.center,
    zoom: config.zoom
});
map.once('idle', function() {
    document.documentElement.setAttribute('data-rs-idle', '');
});

// Resize once loaded: the iframe may have been hidden while the map started
map.on('load', function() {
    // Resolve data references from cache BEFORE creating map elements
    resolveDataReferences();

    setTimeout(function() {
        map.resize();
    }, 100);

    // Add markers if specified
    if (config.markers && config.markers.length > 0) {
        config.markers.forEach(function(marker) {
            var popup = null;
            if (marker.popup) {
                popup = new maplibregl.Popup().setHTML(marker.popup);
            }

            // Font Awesome marker when an icon is given
            if (marker.icon && marker.icon.trim() !== '') {
                var el = document.createElement('div');
                el.className = 'custom-marker';
                el.style.backgroundColor = marker.color || '#3b82f6';
                el.innerHTML = '<i class="' + marker.icon + '"></i>';

                new maplibregl.Marker({ element: el })
                    .setLngLat(marker.coordinates || marker.center || config.center)
                    .setPopup(popup)
                    .addTo(map);
            } else {
                new maplibregl.Marker()
                    .setLngLat(marker.coordinates || marker.center || config.center)
                    .setPopup(popup)
                    .addTo(map);
            }
        });
    }

    // Add lines if specified
    if (config.lines && config.lines.length > 0) {
        config.lines.forEach(function(line, index) {
            var sourceId = 'line-' + index;
            var layerId = 'line-layer-' + index;

            var coordinates = line.coordinates;

            // Check that coordinates are properly resolved from cache
            if (!coordinates) {
                console.error('No coordinates available for line', index, '. Data should be resolved from cache.');
                return;
            }

            // Add data source for the line
            map.addSource(sourceId, {
                'type': 'geojson',
                'data': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': coordinates
                    }
                }
            });

            // Add line layer
            map.addLayer({
                'id': layerId,
                'type': 'line',
                'source': sourceId,
                'layout': {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                'paint': {
                    'line-color': line.color || '#3b82f6',
                    'line-width': line.width || 3,
                    'line-opacity': line.opacity || 0.8
                }
            });

            // Add popup for line if specified
            if (line.popup) {
                map.on('click', layerId, function(e) {
                    new maplibregl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(line.popup)
                        .addTo(map);
                });

                // Pointer cursor on hover
                map.on('mouseenter', layerId, function() {
                    map.getCanvas().style.cursor = 'pointer';
                });

                map.on('mouseleave', layerId, function() {
                    map.getCanvas().style.cursor = '';
                });
            }
        });
    }

    // Add circles if specified
    if (config.circles && config.circles.length > 0) {
        var stats = calculateCircleStats(config.circles);
        var minRadius = config.minRadius || 5;
        var maxRadius = config.maxRadius || 50;

        config.circles.forEach(function(circle, index) {
            var sourceId = 'circle-' + index;
            var layerId = 'circle-layer-' + index;

            var coordinates = circle.coordinates;
            var value = circle.value;

            // Check that coordinates are properly resolved from cache
            if (!coordinates) {
                console.error('No coordinates available for circle', index, '. Data should be resolved from cache.');
                return;
            }

            var radius = calculateRadius(value, stats.min, stats.max, minRadius, maxRadius);

            // Add data source for the circle
            map.addSource(sourceId, {
                'type': 'geojson',
                'data': {
                    'type': 'Feature',
                    'properties': {
                        'value': value,
                        'radius': radius
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': coordinates
                    }
                }
            });

            // Add circle layer
            map.addLayer({
                'id': layerId,
                'type': 'circle',
                'source': sourceId,
                'paint': {
                    'circle-radius': radius,
                    'circle-color': circle.color || '#3b82f6',
                    'circle-opacity': circle.opacity || 0.6,
                    'circle-stroke-width': circle.strokeWidth || 2,
                    'circle-stroke-color': circle.strokeColor || '#ffffff'
                }
            });

            // Add popup for circle if specified
            if (circle.popup) {
                map.on('click', layerId, function(e) {
                    new maplibregl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(circle.popup)
                        .addTo(map);
                });

                // Pointer cursor on hover
                map.on('mouseenter', layerId, function() {
                    map.getCanvas().style.cursor = 'pointer';
                });

                map.on('mouseleave', layerId, function() {
                    map.getCanvas().style.cursor = '';
                });
            }
        });
    }

    // Add choropleth if specified
    if (config.choropleth) {
        var geojsonData = config.choropleth.geojson;

        // Check that GeoJSON data is available (resolved client-side from cache)
        if (!geojsonData) {
            console.error('No geojson data available for choropleth. Data should be resolved from cache.');
            return;
        }

        if (geojsonData) {
            map.addSource('choropleth-source', {
                'type': 'geojson',
                'data': geojsonData
            });
        } else {
            console.error('No geojson data available for choropleth');
            return;
        }

        // Colour expression: the first matching rule wins
        var colorExpression = ['case'];
        if (config.choropleth.colorRules) {
            config.choropleth.colorRules.forEach(function(rule) {
                if (rule.operator === '>=') {
                    colorExpression.push(['>=', ['get', config.choropleth.colorProperty], rule.value]);
                } else if (rule.operator === '>') {
                    colorExpression.push(['>', ['get', config.choropleth.colorProperty], rule.value]);
                } else if (rule.operator === '<=') {
                    colorExpression.push(['<=', ['get', config.choropleth.colorProperty], rule.value]);
                } else if (rule.operator === '<') {
                    colorExpression.push(['<', ['get', config.choropleth.colorProperty], rule.value]);
                } else if (rule.operator === '==') {
                    colorExpression.push(['==', ['get', config.choropleth.colorProperty], rule.value]);
                }
                colorExpression.push(rule.color);
            });
        }

        // Colour when no rule matches
        colorExpression.push(config.choropleth.defaultColor || '#cccccc');

        map.addLayer({
            'id': 'choropleth-fill',
            'type': 'fill',
            'source': 'choropleth-source',
            'paint': {
                'fill-color': colorExpression,
                'fill-opacity': config.choropleth.fillOpacity || 0.7,
                'fill-outline-color': config.choropleth.strokeColor || '#ffffff'
            }
        });

        // Add contours if requested
        if (config.choropleth.showBorders !== false) {
            map.addLayer({
                'id': 'choropleth-stroke',
                'type': 'line',
                'source': 'choropleth-source',
                'paint': {
                    'line-color': config.choropleth.strokeColor || '#ffffff',
                    'line-width': config.choropleth.strokeWidth || 1,
                    'line-opacity': 0.8
                }
            });
        }

        // Add interactivity
        if (config.choropleth.popup) {
            map.on('click', 'choropleth-fill', function(e) {
                var properties = e.features[0].properties;
                var popupContent = config.choropleth.popup;

                // Fill {property} placeholders
                Object.keys(properties).forEach(function(key) {
                    var regex = new RegExp('{' + key + '}', 'g');
                    popupContent = popupContent.replace(regex, properties[key]);
                });

                new maplibregl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(popupContent)
                    .addTo(map);
            });

            // Pointer cursor on hover
            map.on('mouseenter', 'choropleth-fill', function() {
                map.getCanvas().style.cursor = 'pointer';
            });

            map.on('mouseleave', 'choropleth-fill', function() {
                map.getCanvas().style.cursor = '';
            });
        }
    }

    // Create legend after everything is loaded
    createLegend();

});

// Add navigation controls if enabled
if (config.navigation !== false) {
    map.addControl(new maplibregl.NavigationControl());
}

// Add scale control if enabled
if (config.scale !== false) {
    map.addControl(new maplibregl.ScaleControl({
        maxWidth: 100,
        unit: 'metric'
    }));
}

window.addEventListener('resize', function() {
    map.resize();
});

