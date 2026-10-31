# Example data sources

Open data used by the gallery, frozen here so the documentation builds
without downloading anything.

## cardio_mortalite_dep.csv
- Indicator: mortality from heart failure, standardised rate per
  100,000 inhabitants, 2020-2022 average, by department.
- Source: Sante publique France, ODISSE platform,
  dataset "Maladies cardio-neuro-vasculaires : taux standardises (Departement)".
- Licence: Licence Ouverte / Open Licence (Etalab).

## paris_africa_air_traffic.csv
- Indicator: air passengers carried in 2024 between the Paris airports
  (Charles-de-Gaulle and Orly, summed) and the main airport of each
  African city listed, with the city longitude/latitude.
- Source: Eurostat, dataset "avia_par_fr", measure PAS_CRD, 2024.
- Licence: Eurostat open data policy (free reuse with attribution).

## france_departments.geojson
- Geometry: departments of France (metropolitan and overseas), simplified
  to about 1 km and in longitude/latitude, with the department code.
- Source: IGN, GéoFLA.
- Licence: Licence Ouverte / Open Licence (Etalab).

## life_curves.png
- Picture: life expectancy at birth of each country, 1952-2007, with the
  world mean weighted by population. Drawn by `make_life_curves.py`.
- Source: Gapminder, data set shipped with Plotly (`px.data.gapminder()`).
