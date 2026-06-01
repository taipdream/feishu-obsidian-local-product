from feishu_obsidian_local_backend.tag_suggester import suggest_tags


def test_suggest_tags_returns_high_confidence_matches():
    text = """
    这篇内容讨论女性成长中的情绪价值，不是泛安慰，而是让用户降低启动成本。
    它提到身份焦虑、行动力不足，以及一种有人陪着往前走的轻陪伴机制。
    """
    tags = suggest_tags(text)
    assert tags["themes"] == ["女性成长", "情绪价值"]
    assert tags["problems"] == ["身份焦虑", "行动力不足"]
    assert tags["mechanisms"] == ["轻量陪伴"]


def test_suggest_tags_returns_empty_lists_for_no_match():
    tags = suggest_tags("这是一段没有命中词表的普通内容。")
    assert tags == {
        "themes": [],
        "problems": [],
        "mechanisms": [],
    }
