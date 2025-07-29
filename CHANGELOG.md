# Changelog

## [1.1.15] - 2025-07-29

### Added
- **Simplified GeoJSON sharing API**: Use `shared_data_ids` parameter directly in `add_content()`
- **Map types support**: Added support for plotly maps (choroplethmap, scattermap, lines)

### Changed  
- **API improvement**: Direct `shared_data_ids` parameter instead of manual `Content()` objects

### Fixed
- **MathJax compatibility**: Fixed SVG output conflicts with Plotly charts
- **GeoJSON data access**: Improved global data handling between Presentation and Content classes

## [1.1.14] - 2025-07-29

### Added
- **Global GeoJSON sharing**: Share GeoJSON data across the entire presentation
  - Add `add_global_geojson()` method to `Presentation` class
  - Add `add_optimized_plotly()` method to `Content` class for referencing global data
  - Reduces HTML file size when using maps across multiple slides

### Technical
- Added global GeoJSON storage in `presentation.py`
- Added optimized Plotly method in `content.py`

## [1.1.13] - 2025-07-29

### Added
- **Add split title page**:
  - Add `split_title_content()`

## [1.1.12] - 2025-07-25

### Added
- **Complete LaTeX support**: Automatic LaTeX integration with MathJax 3
  - Automatic LaTeX content detection (`$` and `$$` delimiters)
  - Automatic conversion: `$E = mc^2$` → `\(E = mc^2\)` (inline)
  - Automatic conversion: `$$\int_a^b f(x)dx$$` → `\[\int_a^b f(x)dx\]` (display)
  - LaTeX protection during Markdown processing
  - Fixed MathJax.Hub compatibility issues

### Improved
- Enhanced EFS theme CSS with new styles
- Fixed CSS styles for Plotly charts in EFS theme
- Updated documentation with LaTeX examples
- Improved `readme_example.py` with mathematical formulas

### Technical
- Added new utility functions in `utils.py` for LaTeX processing
- Updated automatic content detection in `container.py`
- Improved MathJax integration in `presentation.py`
- Updated `pyproject.toml` for new version

## Previous versions

### [1.1.11] and earlier
- Plotly support with new CDN
- Matplotlib support with SVG integration
- Altair/Vega-Lite support
- Bootstrap responsive grid system
- Custom CSS themes (EFS, ABM, etc.)
- Vertical slides support
- Animations and transitions
- Speaker View mode
- Automatic content type detection
- Local and remote image support
- Font Awesome icons integration

---
## Types of changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
