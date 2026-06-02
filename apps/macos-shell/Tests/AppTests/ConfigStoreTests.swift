import Testing
import Foundation
@testable import App

@Test
func testConfigStoreWritesMachineLocalConfiguration() throws {
    let temp = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    let store = ConfigStore(configURL: temp.appendingPathComponent("config.json"))
    let config = ProductConfiguration(
        vaultRoot: "/Users/test/Documents/InsightVault",
        feishuAppID: "app-id",
        feishuAppSecret: "secret",
        feishuVerificationToken: "verification",
        feishuEncryptKey: "encrypt",
        tavilyAPIKey: "tavily"
    )

    try store.saveConfiguration(config)

    let loaded = try store.loadConfiguration()
    #expect(loaded == config)
}
