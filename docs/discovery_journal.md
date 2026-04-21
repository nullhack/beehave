# Discovery Journal: beehave

---

## 2026-04-21 — Session 1
Status: IN-PROGRESS

### General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Developers, testers and managers that use BDD as part of their development cycle. The tool should be extensible to other test frameworks (framework-agnostic), installable via extras like `pip install beehave[pytest]`, `pip install beehave[unittest]`, etc. Wrappers (e.g. `pytest-beehave`) can be developed on each framework for deeper integration, but that level of integration is out of scope. |
| Q2 | What does the product do at a high level? | Beehave keeps the living documentation reasonably up to date. It does not check implementation specifics or change test bodies. It flags, changes, and updates whatever is mandatory, following the mantra that `.feature` files are the source of truth and `tests/` should reflect that. |
| Q3 | Why does it exist — what problem does it solve? | It is too complicated to keep living documentation and code/tests in sync. Beehave tries to make that gap smaller. |
| Q4 | When and where is it used? | It can be used as a package, and it should also have CLI capabilities. |
| Q5 | Success — what does "done" look like? | Success is when stubs are generated and updated without destroying anything, and when the tool successfully informs the user when something changed that is beyond the scope of the project to handle. |
| Q6 | Failure — what must never happen? | Failure is when it breaks the user tests or fails to inform the user about something. Users must still be able to force changes and see dry-run changes. |
| Q7 | Out-of-scope — what are we explicitly not building? | Not doing any coding (i.e. not modifying test implementation bodies). There is a configurable structure for tests, and that structure will be followed. Corner cases like parameters need more thought — the stakeholder is unsure what to do with them. |
| Q8 | What is the public API surface — CLI, Python API, or both? | Both CLI and Python API. Commands should have a subtle bee-world-related flavor, but not overdone — only used when it feels natural. |
| Q9 | How do consumers (like pytest-beehave) register marker templates? | Stubs and changes will be templated per framework adapter. Start with pytest only, then add unittest. The difference between adapters is mostly marker style and framework conventions (e.g. behave splits into steps; in pytest one function or class can be used depending on the desired template). |
| Q10 | Who configures beehave — end developers or framework authors? | End developers. Framework authors can use it if they want to integrate, but that is not the primary concern. The primary concern is keeping living documentation in sync. |
| Q11 | What is the exact relationship between `beehave` and the future `pytest-beehave` wrapper? | `pytest-beehave` is a pytest-only wrapper using `beehave` under the hood. It adds specific pytest capabilities like automatic running, HTML acceptance criteria injection, and terminal acceptance criteria. |
| Q4-follow-up | Clarification: what are the exact usage modes? | Python: `from beehave import ...`; Bash: `beehave --<keywords>` |
| Q7-follow-up | Clarification: how should parameters and Scenario Outlines be handled? | Outlines should show completely in docstrings/templates per framework. Parameters should be handled the way each framework treats them natively (not universal). |
| Q8-follow-up | Clarification: what about bee-themed CLI commands? | Current options feel too limited and unnatural. Stakeholder wants more candidate names to choose from. |

