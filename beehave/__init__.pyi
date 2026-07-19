# Public package surface for beehave v2.3.
#
# - `step` is the Mode B executable `with`-block CM (lives in `beehave.step`).
# - `StepError` is raised on step/parametrize verification failure.
# - `NoActiveScenarioError` is raised when `step()` runs outside a known scenario.
# - `__version__` is the single source of truth.
from beehave._index import NoActiveScenarioError as NoActiveScenarioError
from beehave.step import StepError as StepError
from beehave.step import step as step

__version__: str
