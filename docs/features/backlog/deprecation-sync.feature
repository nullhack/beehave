Feature: deprecation-sync — propagate @deprecated tags to test stubs

  When a .feature file carries a @deprecated tag at Feature, Rule, or Example level, beehave
  sync adds the adapter's deprecated marker to all affected test stub functions. The cascade is
  absolute in v1: a @deprecated on a Feature or Rule propagates to every child Example with no
  per-Example override mechanism.

  Status: ELICITING

  Rules (Business):
  - @deprecated on a Feature applies to all child Examples of that Feature
  - @deprecated on a Rule applies to all child Examples of that Rule
  - @deprecated on an Example applies to that Example only
  - There is no per-Example override of a parent @deprecated tag in v1

  Constraints:
  - Cascade direction is always parent → child; never child → parent
