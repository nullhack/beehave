from beehave.decorators import Given, When, Then, Example
from hypothesis import strategies as st


initial_strategy = st.integers(min_value=0, max_value=1000)
amount_strategy = st.integers(min_value=0, max_value=500)
total_strategy = st.integers(min_value=0, max_value=1500)
remaining_strategy = st.integers(min_value=0, max_value=1000)


@Given("a hive with <initial> grams of honey")
@When("a forager bee brings back <amount> grams of nectar")
@Then("the hive should contain <total> grams of honey")
@Example(initial=10, amount=5, total=15)
def test_adding_nectar_to_the_honey_store_a1b2c3d4(initial, amount, total):
    assert initial + amount == total


@Given("a hive with <initial> grams of honey")
@When("the colony consumes <amount> grams over winter")
@Then("the hive should contain <remaining> grams of honey")
@Example(initial=100, amount=30, remaining=70)
def test_consuming_honey_during_winter_e5f6a7b8(initial, amount, remaining):
    assert initial - amount == remaining


@Given("a hive with <initial> grams of honey")
@When("the beekeeper splits it into <parts> equal jars")
@Then("each jar should contain <per_jar> grams of honey")
@Example(initial=90, parts=3, per_jar=30)
def test_splitting_honey_between_two_hives_c9d0e1f2(initial, parts, per_jar):
    assert initial == parts * per_jar
