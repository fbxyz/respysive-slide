# Changelog


## [1.1.13] - 2025-07-29

### Added
- **Shared Data Support for Plotly Charts**: Share large datasets across multiple charts without duplication
  - Add `add_shared_data()` method to store data once in a hidden div
  - Use `shared_data_id` parameter in `add_plotly()` to reference shared data
  - Reduces HTML file size when reusing data

### Technical
- Added LaTeX processing utilities in `utils.py`
- Improved automatic content type detection in `container.py`
- Better MathJax 3 integration in `presentation.py`
- New shared data architecture

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