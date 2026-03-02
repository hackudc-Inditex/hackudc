# HackUDC 2026 - Zara Visual Product Recognition

## El Problema

**Objetivo**: Dado una imagen de un modelo vistiendo productos de Zara (bundle), identificar qué productos del catálogo están presentes en la imagen.

### Datos proporcionados

| Dataset | Descripción |
|---------|-------------|
| `bundles_dataset.csv` | 1,507 imágenes de bundles con `bundle_asset_id`, `bundle_id_section` (sección comercial), `bundle_image_url` |
| `product_dataset.csv` | 27,688 productos con `product_asset_id`, `product_image_url`, `product_description` (categoría) |
| `bundles_product_match_train.csv` | Pares bundle-producto de entrenamiento (ground truth) |
| `bundles_product_match_test.csv` | Bundles de test (hay que predecir los productos) |

### Métricas de evaluación
- **Recall@15**: Se evalúan hasta 15 productos por bundle
- Cada bundle puede tener múltiples productos (promedio ~3-4)

### Desafíos principales
1. **Gran espacio de búsqueda**: 27,688 productos candidatos
2. **Variabilidad visual**: El mismo producto puede verse muy diferente en el bundle vs en el catálogo
3. **Múltiples productos por imagen**: Hay que detectar camiseta, pantalón, zapatos, accesorios...
4. **Categorías difíciles**: Zapatos, gorros y accesorios no son detectados por modelos estándar

---

## Nuestra Solución

### Arquitectura del Pipeline

```
Bundle Image
    │
    ├──► CLIP ViT-L-14 (embedding global 768d)
    │
    ├──► YOLOv8 DeepFashion2 (detecta prendas individuales)
    │         │
    │         ├──► Crop camiseta ──► CLIP ──► embedding 768d
    │         ├──► Crop pantalón ──► CLIP ──► embedding 768d
    │         └──► ...
    │
    └──► Zone Crops (zonas fijas para categorías que YOLO no detecta)
              ├──► Crop pies (zapatos) ──► CLIP ──► embedding 768d
              └──► Crop cabeza (gorros/gafas) ──► CLIP ──► embedding 768d

Product Image ──► CLIP ──► embedding 768d

         Projection Head (MLP 768→1536→768)
              │
              ├──► Contrastive Learning (InfoNCE loss)
              └──► Aprende: crop_prenda ⟺ producto_correcto

         FAISS (búsqueda por similitud coseno)
              │
         8 Scoring Signals ──► Top 15 productos
```

### Componentes Clave

#### 1. CLIP ViT-L-14
Modelo vision-lenguaje preentrenado de OpenAI que genera embeddings de 768 dimensiones. Captura semántica visual (color, forma, textura, estilo).

#### 2. YOLOv8 DeepFashion2
Detector de prendas entrenado en DeepFashion2 (13 categorías de ropa):
- `short_sleeved_shirt`, `long_sleeved_shirt`, `short_sleeved_outwear`
- `long_sleeved_outwear`, `vest`, `sling`, `shorts`, `trousers`
- `skirt`, `short_sleeved_dress`, `long_sleeved_dress`, `vest_dress`, `sling_dress`

Mapeamos cada detección YOLO a las categorías del catálogo de Zara.

#### 3. Zone Crops
Recortes fijos de la imagen para detectar categorías que YOLO **no detecta**:
- **Pies** (75%-100% inferior): zapatos, botas, sandalias
- **Cabeza** (0%-18% superior): gorros, gafas

Sin zone crops, ~18% del ground truth (zapatos) estaría completamente perdido.

#### 4. Projection Head + Contrastive Learning
MLP con residual connection que transforma embeddings CLIP de crops para mejorar el matching:

```python
class ProjectionHead(nn.Module):
    def __init__(self, dim, hidden_dim=None):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),  # 768 → 1536
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, dim),  # 1536 → 768
        )

    def forward(self, x):
        return F.normalize(self.net(x) + x, dim=-1)  # residual + L2 norm
```

Entrenado con **InfoNCE loss** (contrastive learning): el embedding del crop debe ser más similar al producto correcto que a productos negativos.

#### 5. FAISS
Búsqueda eficiente por similitud coseno entre embeddings de crops y embeddings de productos (índice brute-force L2).

#### 6. 8 Señales de Scoring

| Tier | Señal | Descripción | Peso |
|------|-------|-------------|------|
| 1 | **Human Labels** | Anotaciones manuales verificadas | 10,000 |
| 2 | **Model Candidates** | Predicciones del modelo CLIP+Projection | score × temporal |
| 3 | **Temporal Neighbors** | Bundles de training cercanos en tiempo | 0.2-0.3 |
| 4 | **Co-occurrence** | Productos que aparecen juntos frecuentemente | 5-7 |
| 5 | **SKU Prefix** | Código de producto compartido en URL | 28-100 |
| 6 | **Popularity** | Frecuencia por sección comercial | 0.15-0.5 |
| 7 | **Temporal Factor** | Penalización por diferencia de timestamps | 0.3-2.0× |
| 8 | **Section Constraints** | Filtro por categorías válidas en sección | binario |

#### 7. Noise Filter
Eliminamos 53 categorías (1,649 productos) que nunca o casi nunca aparecen en el ground truth:
- Cosméticos, perfumes, velas
- Ropa de casa (toallas, albornoces)
- Sets y ensembles
- Ropa de bebé específica (bodies, pijamas)

Esto reduce el espacio de búsqueda y evita falsos positivos.

#### 8. Human-in-the-Loop
Herramienta de anotación colaborativa para verificar manualmente bundles de test:
- Interfaz web (`annotation/index.html`)
- Servidor Python (`annotation/server.py`)
- Genera `human_labels.csv` (positivos) y `human_negatives.csv` (rechazados)
- ~120 bundles anotados manualmente

---

## Estructura del Proyecto

```
hackudc/
├── bundles_dataset.csv          # Dataset de bundles
├── product_dataset.csv          # Dataset de productos
├── bundles_product_match_train.csv  # Ground truth de training
├── bundles_product_match_test.csv   # Bundles de test
├── kaggle_submit_direct.ipynb   # Notebook de submission final
├── README.md                    # Este archivo
│
├── annotation/                  # Herramienta de anotación
│   ├── index.html              # Interfaz web
│   ├── server.py               # Servidor HTTP
│   ├── annotations.json        # Anotaciones guardadas
│   ├── candidates.json         # Candidatos del modelo
│   ├── human_labels.csv        # Labels positivos verificados
│   └── human_negatives.csv     # Labels rechazados
│
└── defensa/                     # Código para la defensa
    ├── pipeline.ipynb          # Pipeline completo documentado
    ├── defensa.html            # Presentación
    ├── submission_44pct.csv    # Mejor submission (44%)
    │
    │
    └── src/
        └── evaluate.py         # Evaluación local
```

---

## Cómo Ejecutar

### 1. Pipeline Completo (Kaggle)
Subir `defensa/pipeline.ipynb` a Kaggle con los datasets:
- `hackudc-images`: imágenes de bundles y productos
- `human-labels`: anotaciones manuales

```bash
# El notebook instala dependencias automáticamente
pip install open-clip-torch faiss-cpu ultralytics huggingface_hub
```

### 2. Submission Directa (sin GPU)
Para generar submission usando solo labels humanos y heurísticas:

```bash
# Subir kaggle_submit_direct.ipynb a Kaggle
# Requiere datasets: hackudc (CSVs) y human-labels
```

### 3. Herramienta de Anotación
```bash
cd annotation
python server.py --port 8080
# Abrir http://localhost:8080 en el navegador
```

### 4. Evaluación Local
```bash
python defensa/src/evaluate.py --evaluate submission.csv
```

---

## Resultados

| Versión | Método | Recall@15 |
|---------|--------|-----------|
| Baseline | CLIP directo (sin YOLO, sin training) | ~8% |
| V1 | CLIP + YOLO + Zone Crops | ~18% |
| V2 | + Projection Head (contrastive) | ~28% |
| V3 | + 8 Scoring Signals | ~36% |
| **V4** | **+ Human Labels (120 bundles)** | **~44%** |

### Análisis de Errores
- **Zapatos**: Mejora significativa con zone crops (de 2% a ~40%)
- **Accesorios**: Difíciles de detectar visualmente (bolsos, cinturones)
- **Colores similares**: Confusión entre productos del mismo color/estilo
- **Resolución baja**: Detalles de estampados difíciles de distinguir

---

## Tecnologías Utilizadas

- **Python 3.10+**
- **PyTorch** - Framework de deep learning
- **OpenCLIP** - Implementación abierta de CLIP
- **Ultralytics YOLOv8** - Detección de objetos
- **FAISS** - Búsqueda de similitud eficiente
- **Pandas/NumPy** - Procesamiento de datos
- **PIL** - Procesamiento de imágenes

---

## Equipo

Proyecto desarrollado durante **HackUDC 2026** (Hackathon Universidad de A Coruña) por el equipo "Pingüinos" (TOP-5 de la categoria y reto de Inditex):
Miembros/GitHub:

    - Jorge García Varela / jorgegarcia33
    - Sergio Rego Criado / sergiorego29 / srego92
    - David Diz Oubiña / daviddizou

---

## Licencia

Este proyecto es parte de una competición de Kaggle organizada por Zara/Inditex. El código es de uso educativo sientete libre para usarlo en lo que necesites. 
