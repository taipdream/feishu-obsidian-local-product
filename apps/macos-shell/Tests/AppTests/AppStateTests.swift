import Foundation
import Testing
@testable import App

private final class FakeBackendController: BackendControlling {
    var isRunning: Bool = false
    var lastExecutableURL: URL?
    var lastEnvironment: [String: String] = [:]

    func startBackend(executableURL: URL?, environment: [String: String]) throws {
        isRunning = true
        lastExecutableURL = executableURL
        lastEnvironment = environment
    }

    func stopBackend() {
        isRunning = false
    }
}

@MainActor
@Test
func testDefaultVaultPathUsesDocumentsInsightVault() {
    let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    let store = ConfigStore(configURL: tempRoot.appendingPathComponent("config.json"))
    let state = AppState(configStore: store, backendController: FakeBackendController())
    #expect(state.defaultVaultPath.hasSuffix("/Documents/InsightVault"))
}

@MainActor
@Test
func testSaveConfigurationCreatesVaultSkeletonAndPersistsConfig() throws {
    let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    let vaultRoot = tempRoot.appendingPathComponent("InsightVault")
    let configURL = tempRoot.appendingPathComponent("config.json")
    let store = ConfigStore(configURL: configURL)
    let backendController = FakeBackendController()
    let state = AppState(configStore: store, backendController: backendController)

    let config = ProductConfiguration(
        vaultRoot: vaultRoot.path,
        feishuAppID: "app-id",
        feishuAppSecret: "app-secret",
        feishuVerificationToken: "verify-token",
        feishuEncryptKey: "encrypt-key",
        tavilyAPIKey: "tavily-key"
    )

    try state.saveConfiguration(config)

    let persisted = try store.loadConfiguration()
    #expect(persisted == config)
    #expect(FileManager.default.fileExists(atPath: vaultRoot.appendingPathComponent("00 Inbox").path))
    #expect(FileManager.default.fileExists(atPath: vaultRoot.appendingPathComponent("99 System").path))
    #expect(state.isConfigured)
}

@MainActor
@Test
func testStartBackendUsesSavedConfigurationEnvironment() throws {
    let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
    let vaultRoot = tempRoot.appendingPathComponent("InsightVault")
    let configURL = tempRoot.appendingPathComponent("config.json")
    let store = ConfigStore(configURL: configURL)
    let backendController = FakeBackendController()
    let state = AppState(configStore: store, backendController: backendController)

    let config = ProductConfiguration(
        vaultRoot: vaultRoot.path,
        feishuAppID: "app-id",
        feishuAppSecret: "app-secret",
        feishuVerificationToken: "verify-token",
        feishuEncryptKey: "encrypt-key",
        tavilyAPIKey: "tavily-key"
    )

    try state.saveConfiguration(config)
    try state.startBackend()

    #expect(backendController.isRunning)
    #expect(backendController.lastEnvironment["FEISHU_APP_ID"] == "app-id")
    #expect(backendController.lastEnvironment["FEISHU_VERIFICATION_TOKEN"] == "verify-token")
    #expect(backendController.lastEnvironment["VAULT_ROOT"] == vaultRoot.path)
}
