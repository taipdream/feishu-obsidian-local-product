from feishu_obsidian_local_backend.product_config import ProductConfigStore


def test_product_config_store_round_trips_machine_local_settings(tmp_path):
    store = ProductConfigStore(tmp_path / "config.json")
    store.save(
        {
            "vault_root": "/Users/test/Documents/InsightVault",
            "provider_type": "minimax",
            "provider_base_url": "https://api.minimax.io/v1",
        }
    )

    loaded = store.load()

    assert loaded["vault_root"] == "/Users/test/Documents/InsightVault"
    assert loaded["provider_type"] == "minimax"
