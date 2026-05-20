from pathlib import Path

from gherkin import Parser

from beehave.check import check_pair
from beehave.config import Config
from beehave.discover import DiscoverError, discover_tests
from beehave.gherkin import detect_empty_rules, parse_feature


def compute_status(
    config: Config, include_orphaned: bool = False, json_output: bool = False
) -> None:
    features_dir = Path(config.features_dir)
    if not features_dir.is_dir():
        if json_output:
            import json as _json

            print(
                _json.dumps(
                    {"error": f"features directory '{config.features_dir}' not found"}
                )
            )
        else:
            print(
                f"Error: features directory '{config.features_dir}' not found",
                file=__import__("sys").stderr,
            )
        raise SystemExit(2)

    features = sorted(features_dir.rglob("*.feature"))
    feature_slugs = {f.stem for f in features}
    any_not_ok = False

    # Track function names across features for collision detection
    all_fn_sources: dict[str, list[str]] = {}

    # JSON data collection
    feature_data: list[dict] = []
    stage_counts: dict[str, int] = {
        "ok": 0,
        "broken": 0,
        "no_scenarios": 0,
        "needs_scenarios": 0,
        "needs_tests": 0,
        "needs_bodies": 0,
        "needs_fixes": 0,
    }

    def _emit(*args, **kwargs):
        """Print or discard based on json_output mode."""
        if not json_output:
            print(*args, **kwargs)

    first_feature = True
    for feature_file in features:
        slug = feature_file.stem
        content = feature_file.read_text(encoding="utf-8")
        try:
            doc = Parser().parse(content)
        except Exception as e:
            any_not_ok = True
            line = getattr(e, "line", 0) or 0
            if not first_feature and not json_output:
                print()
            first_feature = False
            _emit(f"{slug} (Bad Scenario)  broken")
            _emit(f"  {feature_file}:{line}: {e}")
            if json_output:
                feature_data.append(
                    {
                        "slug": slug,
                        "title": "Bad Scenario",
                        "stage": "broken",
                        "parse_error_message": str(e),
                        "scenarios": [],
                    }
                )
                stage_counts["broken"] += 1
            continue

        feature_title = doc["feature"]["name"]
        scenarios = parse_feature(feature_file, config)

        if not scenarios and not detect_empty_rules(doc):
            any_not_ok = True
            if not first_feature and not json_output:
                print()
            first_feature = False
            _emit(f"{slug} ({feature_title})  no scenarios")
            if json_output:
                feature_data.append(
                    {
                        "slug": slug,
                        "title": feature_title,
                        "stage": "no scenarios",
                        "scenarios": [],
                    }
                )
                stage_counts["no_scenarios"] += 1
            continue
        elif not scenarios and detect_empty_rules(doc):
            any_not_ok = True
            if not first_feature and not json_output:
                print()
            first_feature = False
            _emit(f"{slug} ({feature_title})  needs scenarios")
            if json_output:
                feature_data.append(
                    {
                        "slug": slug,
                        "title": feature_title,
                        "stage": "needs scenarios",
                        "scenarios": [],
                    }
                )
                stage_counts["needs_scenarios"] += 1
            continue

        rule_paths = {si.rule_path for si in scenarios.values()}
        feature_path = next(iter(scenarios.values())).feature_path
        test_dir = Path(config.tests_dir) / feature_path

        # Extract rule titles from the Gherkin doc
        rule_titles: dict[str, str] = {}
        for child in doc["feature"].get("children", []):
            if "rule" in child:
                rule_title = child["rule"]["name"]
                slug_key = rule_title.strip().lower().replace(" ", "_")
                rule_titles[slug_key + "_test"] = rule_title

        # Collect scenario-level statuses and violations
        scenario_statuses: dict[str, str] = {}
        scenario_violations: dict[str, list] = {}
        for rp in rule_paths:
            test_file = test_dir / f"{rp}.py"
            tests: dict = {}
            if test_file.exists():
                try:
                    tests = discover_tests(test_file)
                except DiscoverError:
                    tests = {}
            for fn in tests:
                all_fn_sources.setdefault(fn, []).append(slug)
            for fn, si in scenarios.items():
                if si.rule_path != rp:
                    continue
                ti = tests.get(fn)
                if ti is None:
                    scenario_statuses[fn] = "no test"
                elif ti.is_stub:
                    scenario_statuses[fn] = "no body"
                else:
                    violations = check_pair(si, ti, str(test_file), feature_file.name)
                    if violations:
                        scenario_violations[fn] = violations
                        scenario_statuses[fn] = f"{len(violations)} errors"
                    else:
                        scenario_statuses[fn] = "ok"

        unmapped_count = sum(1 for s in scenario_statuses.values() if s == "no test")
        all_stubs = all(s == "no body" for s in scenario_statuses.values())
        has_violation = any("errors" in s for s in scenario_statuses.values())

        if unmapped_count > 0:
            status_label = "needs tests"
        elif all_stubs:
            status_label = "needs bodies"
        elif has_violation:
            status_label = "needs fixes"
        else:
            status_label = "ok"

        if status_label != "ok":
            any_not_ok = True

        if not first_feature and not json_output:
            print()
        first_feature = False
        _emit(f"{slug} ({feature_title})  {status_label}")

        # Tree output for non-ok features (text mode only)
        if status_label != "ok" and not json_output:
            _print_tree(
                scenarios,
                scenario_statuses,
                scenario_violations,
                rule_paths,
                rule_titles,
            )

        if json_output:
            sc_list: list[dict] = []
            for fn, si in scenarios.items():
                sc_status = scenario_statuses.get(fn, "unknown")
                entry = {
                    "title": si.title,
                    "function_name": fn,
                    "status": sc_status,
                }
                if fn in scenario_violations:
                    entry["violations"] = [
                        {"type": v.error_type, "message": v.message}
                        for v in scenario_violations[fn]
                    ]
                sc_list.append(entry)

            feature_data.append(
                {
                    "slug": slug,
                    "title": feature_title,
                    "stage": status_label,
                    "scenarios": sc_list,
                }
            )
            stage_key = status_label.replace(" ", "_")
            stage_counts[stage_key] = stage_counts.get(stage_key, 0) + 1

    # Report orphaned test directories if flagged
    orphaned_dirs: list[str] = []
    if include_orphaned:
        tests_dir = Path(config.tests_dir)
        if tests_dir.is_dir():
            for test_subdir in sorted(tests_dir.iterdir()):
                if test_subdir.is_dir() and test_subdir.name not in feature_slugs:
                    orphaned_dirs.append(test_subdir.name)

    # Report collisions
    collisions = {fn: slugs for fn, slugs in all_fn_sources.items() if len(slugs) > 1}

    if json_output:
        result = {
            "features": feature_data,
            "summary": {
                "total_features": len(feature_data),
                **{
                    k: stage_counts.get(k, 0)
                    for k in [
                        "ok",
                        "broken",
                        "no_scenarios",
                        "needs_scenarios",
                        "needs_tests",
                        "needs_bodies",
                        "needs_fixes",
                    ]
                },
            },
            "orphaned_directories": orphaned_dirs,
            "collisions": [
                {"function_name": fn, "feature_slugs": slugs}
                for fn, slugs in sorted(collisions.items())
            ],
        }
        import json as _json

        print(_json.dumps(result))
    else:
        if orphaned_dirs:
            if not first_feature:
                print()
            for name in orphaned_dirs:
                print(f"orphaned: {name}")

        if collisions:
            if not first_feature or orphaned_dirs:
                print()
            for fn, slugs in sorted(collisions.items()):
                print(f"collision: {fn} appears in {', '.join(slugs)}")

    raise SystemExit(1 if any_not_ok else 0)


def _rule_aggregation(rule_statuses: dict[str, str]) -> str:
    """Build comma-joined aggregation string for a rule's scenario statuses."""
    counts: dict[str, int] = {}
    total_errors = 0
    for status in rule_statuses.values():
        if status == "ok":
            continue
        if "errors" in status:
            parts = status.split()
            try:
                total_errors += int(parts[0])
            except ValueError, IndexError:
                counts[status] = counts.get(status, 0) + 1
        else:
            counts[status] = counts.get(status, 0) + 1

    parts: list[str] = []
    for status in sorted(counts):
        parts.append(f"{counts[status]} {status}")
    if total_errors > 0:
        word = "error" if total_errors == 1 else "errors"
        parts.append(f"{total_errors} {word}")
    return ", ".join(parts)


def _print_tree(
    scenarios: dict,
    scenario_statuses: dict[str, str],
    scenario_violations: dict[str, list],
    rule_paths: set[str],
    rule_titles: dict[str, str],
) -> None:
    # Group scenarios by rule_path
    by_rule: dict[str, dict[str, str]] = {}
    for fn, si in scenarios.items():
        by_rule.setdefault(si.rule_path, {})[fn] = scenario_statuses[fn]

    sorted_rules = sorted(by_rule.keys())

    # If all scenarios are under "default_test", just show them directly
    if sorted_rules == ["default_test"]:
        scenarios_in_rule = by_rule["default_test"]
        sorted_fns = sorted(scenarios_in_rule.keys())
        for idx, fn in enumerate(sorted_fns):
            sn = scenarios[fn]
            status = scenario_statuses[fn]
            extra = _violation_codes(scenario_violations.get(fn))
            is_last = idx == len(sorted_fns) - 1
            prefix = "  └──" if is_last else "  ├──"
            line = f"{prefix} Scenario: {sn.title}  {status}"
            if extra:
                line += f"  {extra}"
            print(line)
        return

    # Multiple rules or single non-default rule: show rule nodes
    for rule_idx, rp in enumerate(sorted_rules):
        scenarios_in_rule = by_rule[rp]

        # Get rule title from doc or derive from rule_path
        rule_title = rule_titles.get(rp)
        if rule_title is None:
            if rp.endswith("_test"):
                rule_title = rp[:-5].replace("_", " ").title()
            else:
                rule_title = rp.replace("_", " ").title()

        # Build aggregation for this rule
        rule_statuses: dict[str, str] = {}
        for fn in scenarios_in_rule:
            if fn in scenario_statuses:
                rule_statuses[fn] = scenario_statuses[fn]

        agg = _rule_aggregation(rule_statuses)
        is_last_rule = rule_idx == len(sorted_rules) - 1
        rule_prefix = "  └──" if is_last_rule else "  ├──"

        if agg:
            print(f"{rule_prefix} Rule: {rule_title}  ({agg})")
        else:
            print(f"{rule_prefix} Rule: {rule_title}")

        sorted_fns = sorted(scenarios_in_rule.keys())
        for sc_idx, fn in enumerate(sorted_fns):
            sn = scenarios[fn]
            status = scenario_statuses[fn]
            extra = _violation_codes(scenario_violations.get(fn))
            is_last_sc = sc_idx == len(sorted_fns) - 1

            if is_last_rule:
                sc_prefix = "      " + ("└──" if is_last_sc else "├──")
            else:
                sc_prefix = "  │   " + ("└──" if is_last_sc else "├──")

            line = f"{sc_prefix} Scenario: {sn.title}  {status}"
            if extra:
                line += f"  {extra}"
            print(line)


def _violation_codes(violations: list | None) -> str:
    """Extract comma-joined violation identifiers for inline display."""
    if not violations:
        return ""
    codes: list[str] = []
    for v in violations:
        error_type = v.error_type
        if error_type == "missing-placeholder":
            # Message format: "'name' not found in function body"
            msg = v.message
            if "'" in msg:
                name = msg.split("'")[1]
                codes.append(name)
        elif error_type == "missing-literal":
            # Message format: "literal 'value' not found..."
            msg = v.message
            if msg.startswith("literal "):
                rest = msg[len("literal ") :]
                name = rest.split()[0].strip("'\"")
                codes.append(name)
    return ", ".join(codes)
