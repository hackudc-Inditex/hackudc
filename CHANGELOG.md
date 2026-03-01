## [Unreleased]

### Added
- **Automatización de Quality Gates**: Configuración de CI para ejecutar linters y tests automáticamente en cada Pull Request.
- **Cumplimiento REUSE**: Implementación de cabeceras SPDX en todos los archivos de datos y scripts para asegurar la claridad de la licencia a nivel de archivo.
- **Gobernanza**: Borrador del archivo `GOVERNANCE.md` para definir roles y toma de decisiones por consenso perezoso.

### Security
- **Auditoría de dependencias**: Configuración de herramientas para detectar vulnerabilidades en librerías de terceros (preparación para la CRA de septiembre 2026).

---

## [1.0.0] - 2026-03-01

### Added
- **Fase 1: Ingeniería Inversa de URLs**: 
  - Extracción de SKU de producto directamente de la URL de Zara.
  - Implementación de matching por Timestamp (`ts=`) para determinar la temporada (95% de éxito a < 90 días).
- **Fase 2: Filtrado Estadístico**: 
  - Eliminación de 53 categorías de "ruido" (cosméticos, hogar), reduciendo el catálogo en 1.649 productos.
  - Algoritmo de *Diversity Enforcement* para asegurar variedad en el Top-15 de recomendaciones.
- **Fase 3: Pipeline Visual (CLIP + YOLOv8)**: 
  - Detección de prendas individuales mediante YOLOv8 y generación de embeddings con CLIP ViT-L-14.
  - Integración de *Projection Head* de contraste con pérdida InfoNCE para optimizar el matching visual.
- **Fase 4: Grafos de Co-ocurrencia**: 
  - Motor de probabilidad dinámica basado en prendas que aparecen juntas frecuentemente.
- **Fase 5: Human-In-The-Loop**: 
  - Herramienta de anotación web propia (`server.py`) para validación humana con sistema de recompensas y penalizaciones.
  - Puntuación de ranking dinámica: 
    $$Score(p) = (Base\_Score \times W_{match}) + Bonus_{human}$$
- **Infraestructura de Repositorio**: 
  - Implementación del *Repository Baseline*: `README`, `LICENSE` (Apache-2.0), `CONTRIBUTING` (DCO/Sign-off), `CODE_OF_CONDUCT` y `SECURITY.md`.

### Changed
- Estructura de archivos optimizada para cumplir con los estándares de soberanía tecnológica y transparencia.
