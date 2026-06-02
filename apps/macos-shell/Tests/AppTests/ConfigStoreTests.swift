import Testing
import Foundation
@testable import App

@Test
func testConfigStoreWritesMachineLocalJSON() throws {
    let temp = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    let store = ConfigStore(configURL: temp.appendingPathComponent("config.json"))
    try store.save([
        "vaultRoot": "/Users/test/Documents/InsightVault",
        "providerType": "minimax"
    ])

    let loaded = try store.load()
    #expect(loaded["providerType"] as? String == "minimax")
}
