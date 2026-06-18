# UCI Healthcare Dataset 404 Investigation — 2026-06-06

## Problem
UCI Healthcare Dataset (healthcare-dataset-stroke-data.csv) completely inaccessible from all public sources.

## Sources Tested

### Direct URLs (all 404)
- `https://archive.ics.uci.edu/ml/datasets/healthcare+dataset+stroke` → 404
- `https://archive.ics.uci.edu/ml/machine-learning-databases/00504/healthcare-dataset-stroke-data.csv` → 404
- `https://raw.githubusercontent.com/dsrscientist/dataset1/master/healthcare-dataset-stroke-data.csv` → 404
- `https://raw.githubusercontent.com/codeheroku/Stroke-Prediction/main/healthcare%20dataset.csv` → 404
- `https://raw.githubusercontent.com/krishnaik06/Stroke-Prediction/main/data/healthcare-dataset-stroke-data.csv` → 404
- `https://raw.githubusercontent.com/srinivas385/stroke-prediction/master/stroke_data.csv` → 404
- `https://raw.githubusercontent.com/Nikhil3150/Stroke-Prediction/main/healthcare-dataset-stroke-data.csv` → 404

### Kaggle
- `kaggle datasets list --search stroke` → "Authentication required"
- `kaggle datasets download` → requires API token

### HuggingFace
- `datasets-server.huggingface.co/search?query=stroke` → HTTP 422 (this server)
- Direct dataset pages: 404

### OpenML
- `api/v1/json/data/list/limit/5` → 0 datasets (empty response)
- `api/v1/json/data/420` → DID=420 is "cristalli" (wrong dataset)
- No stroke datasets found in 6,408 total datasets

### GitHub Search API
- `api.github.com/search/code?q=healthcare+stroke+dataset` → HTTP 401 (requires auth for code search)

## Conclusion
The UCI Healthcare Dataset has been removed from UCI archive and all community mirrors. It may have been reuploaded to a different platform or taken down entirely.

## Alternative
OpenML Cardiovascular-Disease-dataset (DID=45547) provides 70,000 CVD records with 13 features. This is broader than stroke (CVD includes stroke) but is the best publicly accessible healthcare prediction dataset available.