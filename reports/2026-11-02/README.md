# Companion run — 2 November 2026

This is a new reproducible run based on the recovered notebook's workflow. It is not an exact reconstruction of the historical environment or figures.

- Input: 3,276 observations, ten columns; nine features, excluding `Potability`.
- Missing measurements filled with column medians: pH 491, sulfate 781 and trihalomethanes 162.
- StandardScaler; K-Means with k=3, seed 42 and explicit n_init=10; full-SVD PCA.
- Cluster counts: 0 = 1,139; 1 = 938; 2 = 1,199. These identifiers are arbitrary.
- Sampled silhouette score: **0.0766**, using 1,000 observations with seed 42. This suggests weak cluster separation under this setup; it does not support a strong-segmentation claim.
- First two PCA components explain approximately **25.97%** of variance. The projection leaves out most variance and should be interpreted accordingly.

The original notebook used an unspecified K-Means n_init default and assigned risk labels by cluster index. Those risk labels are not treated as validated findings here. k=3 follows the original study's design; the companion does not establish it as an optimal choice.

[Metrics and package versions](metrics.json) · [Elbow data](elbow.csv) · [Feature means by cluster](cluster_means.csv) · [Dataset provenance](../../data/README.md)

Reproduce from the repository root after downloading the source CSV:

```bash
python -m pip install -r requirements-reproduce.txt
python analysis.py --csv data/water_potability.csv --output-dir outputs/companion
```

`requirements-reproduce.txt` pins the core numerical and plotting packages used for this run. It is not a complete operating-system or transitive-dependency lock. Compare the CSV checksum and package versions before comparing metrics. The command generates a PCA plot, elbow plot, metrics and CSV summaries locally. Raw source and row-level outputs are not committed here.
