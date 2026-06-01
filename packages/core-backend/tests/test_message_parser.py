from feishu_obsidian_local_backend.message_parser import parse_message_event


def test_parse_text_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"一个新灵感\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["content_type"] == "text"
    assert parsed["platform"] == "plain-text"
    assert parsed["raw_text"] == "一个新灵感"
    assert parsed["should_distill"] is False


def test_parse_link_like_text_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"https://example.com 很适合研究标题套路\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["content_type"] == "text-link"
    assert parsed["platform"] == "generic-web"
    assert parsed["original_link"] == "https://example.com"
    assert parsed["should_distill"] is True


def test_parse_save_command_strips_marker_and_saves_plain_text():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"#save\\n一个新灵感\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_distill"] is True
    assert parsed["raw_text"] == "一个新灵感"


def test_parse_distill_command_strips_marker():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"#distill\\nhttps://example.com 一个新灵感\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_distill"] is True
    assert parsed["raw_text"] == "https://example.com 一个新灵感"


def test_parse_idea_command_strips_marker():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"#idea\\n做一个女性成长轻陪伴产品\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_distill"] is True
    assert parsed["should_create_idea"] is True
    assert parsed["raw_text"] == "做一个女性成长轻陪伴产品"


def test_parse_question_message_routes_to_answer():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"我该不该先做女性成长轻陪伴产品？\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_answer"] is True
    assert parsed["should_distill"] is False
    assert parsed["should_create_idea"] is False


def test_parse_asksave_question_routes_to_answer_and_persists():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"#asksave\\n我该不该先做女性成长轻陪伴产品？\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_answer"] is True
    assert parsed["should_distill"] is False
    assert parsed["should_save_answer"] is True


def test_parse_follow_up_question_keeps_parent_and_root_ids():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "parent_id": "om_parent",
            "root_id": "om_root",
            "message": {
                "message_id": "om_child",
                "message_type": "text",
                "content": "{\"text\":\"你对这个怎么看？\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["should_answer"] is True
    assert parsed["message_id"] == "om_child"
    assert parsed["parent_id"] == "om_parent"
    assert parsed["root_id"] == "om_root"


def test_parse_wechat_link_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"https://mp.weixin.qq.com/s/example 这篇值得收\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["platform"] == "wechat-official-account"


def test_parse_structured_wechat_paste_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"标题：情绪价值不是安慰，而是让人敢继续往前走\\n公众号：示例公众号\\n链接：https://mp.weixin.qq.com/s/example\\n\\n第一段内容。\\n第二段内容。\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["platform"] == "wechat-official-account"
    assert parsed["title_hint"] == "情绪价值不是安慰，而是让人敢继续往前走"
    assert parsed["author_hint"] == "示例公众号"
    assert parsed["original_link"] == "https://mp.weixin.qq.com/s/example"
    assert "第一段内容" in parsed["body_hint"]


def test_parse_xiaohongshu_link_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"https://www.xiaohongshu.com/explore/abc 很适合参考\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["platform"] == "xiaohongshu"


def test_parse_structured_xiaohongshu_link_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"标题：这个选题为什么在小红书容易爆\\n作者：某某博主\\nhttps://www.xiaohongshu.com/explore/abc\\n这条适合研究标题结构和评论区承接。\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["platform"] == "xiaohongshu"
    assert parsed["title_hint"] == "这个选题为什么在小红书容易爆"
    assert parsed["author_hint"] == "某某博主"
    assert parsed["original_link"] == "https://www.xiaohongshu.com/explore/abc"
    assert "评论区承接" in parsed["body_hint"]


def test_parse_douyin_link_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_type": "text",
                "content": "{\"text\":\"https://v.douyin.com/abc123/ 这个表达方式不错\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["platform"] == "douyin"


def test_parse_image_message():
    payload = {
        "event": {
            "sender": {"sender_id": {"open_id": "ou_x"}},
            "message": {
                "message_id": "om_123",
                "message_type": "image",
                "content": "{\"image_key\":\"img_123\"}",
            },
        }
    }
    parsed = parse_message_event(payload)
    assert parsed["content_type"] == "image"
    assert parsed["platform"] == "image"
    assert parsed["should_distill"] is True
    assert parsed["image_key"] == "img_123"
    assert parsed["message_id"] == "om_123"
