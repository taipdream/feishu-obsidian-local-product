import Foundation
import SwiftUI

@MainActor
final class AppState: ObservableObject {
    @Published private(set) var configuration: ProductConfiguration?
    @Published private(set) var backendRunning: Bool = false
    @Published private(set) var statusMessage: String
    @Published var lastError: String?

    let defaultVaultPath: String

    private let configStore: ConfigStore
    private let backendController: BackendControlling
    private let fileManager: FileManager

    var isConfigured: Bool {
        configuration != nil
    }

    init(
        configStore: ConfigStore = ConfigStore(configURL: AppPaths.defaultConfigURL()),
        backendController: BackendControlling = BackendProcessController(),
        fileManager: FileManager = .default
    ) {
        self.configStore = configStore
        self.backendController = backendController
        self.fileManager = fileManager
        self.defaultVaultPath = "\(fileManager.homeDirectoryForCurrentUser.path)/Documents/InsightVault"

        if let loaded = try? configStore.loadConfiguration() {
            self.configuration = loaded
            self.statusMessage = "Ready to start backend"
        } else {
            self.statusMessage = "Finish onboarding"
        }
    }

    func saveConfiguration(_ configuration: ProductConfiguration) throws {
        try ensureVaultSkeleton(vaultRoot: configuration.vaultRoot)
        try configStore.saveConfiguration(configuration)
        self.configuration = configuration
        self.statusMessage = "Configuration saved"
        self.lastError = nil
    }

    func startBackend() throws {
        guard let configuration else {
            statusMessage = "Finish onboarding"
            throw AppStateError.configurationMissing
        }

        try backendController.startBackend(executableURL: nil, environment: makeBackendEnvironment(from: configuration))
        backendRunning = backendController.isRunning
        statusMessage = backendRunning ? "Backend running" : "Backend failed to start"
        lastError = nil
    }

    func stopBackend() {
        backendController.stopBackend()
        backendRunning = backendController.isRunning
        statusMessage = configuration == nil ? "Finish onboarding" : "Backend stopped"
    }

    private func ensureVaultSkeleton(vaultRoot: String) throws {
        let root = URL(fileURLWithPath: vaultRoot)
        try fileManager.createDirectory(at: root, withIntermediateDirectories: true)
        for relative in AppPaths.requiredVaultDirectories {
            try fileManager.createDirectory(
                at: root.appendingPathComponent(relative),
                withIntermediateDirectories: true
            )
        }
    }

    private func makeBackendEnvironment(from configuration: ProductConfiguration) -> [String: String] {
        let vaultRoot = URL(fileURLWithPath: configuration.vaultRoot)
        return [
            "FEISHU_APP_ID": configuration.feishuAppID,
            "FEISHU_APP_SECRET": configuration.feishuAppSecret,
            "FEISHU_VERIFICATION_TOKEN": configuration.feishuVerificationToken,
            "FEISHU_ENCRYPT_KEY": configuration.feishuEncryptKey,
            "TAVILY_API_KEY": configuration.tavilyAPIKey,
            "VAULT_ROOT": configuration.vaultRoot,
            "INBOX_DIR": vaultRoot.appendingPathComponent("00 Inbox").path,
            "SOURCE_DIR": vaultRoot.appendingPathComponent("01 Sources").path,
            "IDEAS_DIR": vaultRoot.appendingPathComponent("03 Ideas").path,
            "ANSWERS_DIR": vaultRoot.appendingPathComponent("06 Answers").path,
            "ASSETS_DIR": vaultRoot.appendingPathComponent("Assets").path,
        ]
    }
}

enum AppStateError: Error {
    case configurationMissing
}
