# Notebook provenance

- `original_source.ipynb`: recovered from the Colab file linked in the original presentation. Code and markdown cell sources are preserved; execution outputs/counts and per-cell metadata were removed, and notebook metadata was reduced to a Python kernel declaration. It retains the original `/content/water_potability.csv` path and historical chart labels. It is an archive, not the supported local execution entry point.
- `reproduce.ipynb`: a new documented companion that invokes the repository's `analysis.py`. It uses local paths, explicit K-Means `n_init=10` and seed 42, deterministic full-SVD PCA and neutral cluster labels. It does not claim to reproduce the exact historical figures.

The recovered code uses **median imputation**, not dropping missing rows, and excludes `Potability` from clustering. This resolves the earlier uncertainty caused by inconsistent descriptions in the presentation. The original uses K-Means without an explicit `n_init`; its old dependency versions are not recorded.

The original notebook assigns low/medium/high risk names to cluster IDs by position. Such IDs are arbitrary; those labels are not reproduced as validated findings in the companion.
