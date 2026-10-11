from kb_creator.pipeline.language_context import skill_context


def test_roll_cue_does_not_cross_sentence_into_ordinary_science():
    text = 'They pursued it "in the name of science". With a Psychology roll, they know why.'
    assert skill_context("Science", text)["applicability"] == "excluded_non_skill_context"
    assert skill_context("Psychology", text)["applicability"] == "required_skill"
    assert skill_context("Science", "A Science: Forensics roll reveals evidence.")["applicability"] == "required_skill"


def test_named_exclusion_binds_only_the_actual_occurrence():
    text = "Anyone with law enforcement Influences (or INT check) recognises him. A Law roll helps."
    result = skill_context("Law", text)
    assert result["required_occurrences"] == 1
    assert result["excluded_occurrences"] == 1
    assert skill_context("History", "Incan History books are here. A History roll helps.")["required_occurrences"] == 1


def test_parenthesized_skill_action_binds_to_the_matched_occurrence():
    navigate = "Either planning the route (Navigate) or driving quickly (Drive Auto) gets the PCs there faster."
    stealth = "To get close to either building, PCs can sneak up (Stealth) or move up directly."
    assert skill_context("Navigate", navigate)["applicability"] == "required_skill"
    assert skill_context("Stealth", stealth)["applicability"] == "required_skill"

    topic_name = "The route (Navigate) is discussed as a topic in the guide."
    assert skill_context("Navigate", topic_name)["applicability"] != "required_skill"

    nearby_skill = "The route (Navigate) is discussed as a topic. A Stealth roll helps."
    assert skill_context("Navigate", nearby_skill)["applicability"] != "required_skill"
    assert skill_context("Stealth", nearby_skill)["applicability"] == "required_skill"


def test_kremlin_explicit_roll_check_and_standalone_heading_are_required():
    assert skill_context("Listen Roll", "Listen Roll")["applicability"] == "required_skill"
    assert skill_context("Spot Hidden Roll", "Spot Hidden Roll")["applicability"] == "required_skill"
    assert skill_context("Library Use", "# LIBRARY USE")["applicability"] == "required_skill"
    assert skill_context("Library Use", "## Library Use ##")["applicability"] == "required_skill"


def test_kremlin_context_rules_stay_bounded_and_fail_closed():
    assert skill_context("History", "a professor of History and Architecture")["applicability"] == "excluded_non_skill_context"
    assert skill_context("Architecture", "a professor of History and Architecture")["applicability"] == "excluded_non_skill_context"
    assert skill_context("History", "a professor of History. History roll decides the result.")["required_occurrences"] == 1
    assert skill_context("History", "History is taught at the university.")["applicability"] == "ambiguous"
    assert skill_context("Library Use", "Library Use reference notes")["applicability"] == "ambiguous"


def test_authorized_skill_context_accepts_only_bounded_local_notation():
    authorized = {"Navigate", "Spot Hidden", "Library Use"}
    assert skill_context(
        "Navigate", "They try (Navigate or Spot Hidden) to find the route.", authorized_skills=authorized,
    )["applicability"] == "required_skill"
    assert skill_context(
        "Library Use", "Library Use (+20%) reveals the archive.", authorized_skills=authorized,
    )["applicability"] == "required_skill"
    assert skill_context(
        "Library Use", "Library Use, Spot Hidden.", authorized_skills=authorized,
        predecessor_text="Selection of skills:",
    )["applicability"] == "required_skill"
    assert skill_context(
        "Fast Talk", 'They convince a friend (such as Yuri) to borrow a vehicle (Fast Talk).',
        authorized_skills={"Fast Talk"},
    )["applicability"] == "required_skill"
    assert skill_context("Navigate", "The route (Navigate) is a topic.", authorized_skills=authorized)["applicability"] != "required_skill"


def test_narrative_parenthesized_action_is_distinct_from_route_topic():
    assert skill_context(
        "Fast Talk", 'They might convince someone to let them "borrow" a car (Fast Talk -10%).',
    )["applicability"] == "required_skill"
    assert skill_context("Navigate", "The route (Navigate) is a topic.")["applicability"] != "required_skill"
