# Frozen ruptures source subset

Upstream: https://github.com/deepcharles/ruptures/tree/v1.1.10

The five files listed in `upstream.json` are copied unchanged from the release
tag v1.1.10. Their Git blob IDs are recorded for verification. The BSD 2-clause
license is retained in `LICENSE`.

Only Dynp and CostL2 are needed for this project. Local `__init__.py` files
provide the imports and an L2-only cost_factory; they are adapters authored
for this repository, not upstream files. Other models are intentionally
rejected. This is not a full installation of the ruptures distribution and
does not claim package-wide validation. Dynp's upstream default jump is 5;
the corrected runner explicitly passes jump=1. No optimization recurrence or
L2 cost calculation was changed. Do not use this subset for other algorithms.
