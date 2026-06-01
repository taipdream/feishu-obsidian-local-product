TAG_RULES = {
    "themes": [
        ("女性成长", ["女性成长", "女性", "成长"]),
        ("情绪价值", ["情绪价值"]),
        ("轻创业", ["轻创业", "副业", "小生意"]),
    ],
    "problems": [
        ("身份焦虑", ["身份焦虑"]),
        ("行动力不足", ["行动力不足", "启动成本", "拖延"]),
    ],
    "mechanisms": [
        ("轻量陪伴", ["轻陪伴", "陪伴", "有人陪着"]),
        ("情绪安慰", ["情绪安慰"]),
    ],
}


def suggest_tags(text: str) -> dict:
    normalized = text or ""
    result = {
        "themes": [],
        "problems": [],
        "mechanisms": [],
    }
    for bucket, rules in TAG_RULES.items():
        for label, keywords in rules:
            if any(keyword in normalized for keyword in keywords):
                result[bucket].append(label)
    return result
