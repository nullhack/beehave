# Public package surface for beehave v2.
#
# - `step` is the executable `with`-block CM (re-exported; lives in
#   `beehave.step`).
# - `__version__` is the single source of truth (interview L1 Constraint 3;
#   the `== "2.0.0"` assertion is deferred to deliver — only the
#   declaration lives here).
from beehave.step import step as step

__version__: str
