# Scientific production periodization — ISTL revision

The reproducible diagnostic pipeline lives in [`istl/`](istl/README.md).
Run `python istl/run.py` from the repository root. The three methods are
Gaussian derivatives, independent piecewise linear regression, and Dynp L2.

The root scripts `1_metodo_derivadas.py`, `2_metodo_S-Robledo.py`,
`3_metodo_nuevo.py`, `data_articles.py`, and `ArticuloEDO.ipynb` are **historical
versions**, retained unchanged for traceability. In particular, the notebook's
third method is K-means, despite its PELT heading; it must not be used as the
implementation of the revised third method. Historical root PNGs are not
outputs of the corrected pipeline.

This revision provides diagnostic results only. Published expert boundaries
and Table 2 accuracy metrics are not verified. No winning method is identified.

## Second delivery

The provisional published-K comparison is in [istl/v2](istl/v2/README.md).
Read the [director review and updated evidence status](istl/integration/REVIEW_ENTREGA02.md) before interpreting its results.
