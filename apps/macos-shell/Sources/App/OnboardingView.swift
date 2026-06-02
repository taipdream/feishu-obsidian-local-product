import SwiftUI

struct OnboardingView: View {
    @ObservedObject var appState: AppState
    @State private var vaultPath: String
    @State private var feishuAppID: String = ""
    @State private var feishuAppSecret: String = ""
    @State private var feishuVerificationToken: String = ""
    @State private var feishuEncryptKey: String = ""
    @State private var tavilyAPIKey: String = ""

    init(appState: AppState) {
        self.appState = appState
        _vaultPath = State(initialValue: appState.defaultVaultPath)
    }

    var body: some View {
        Form {
            Section {
                Text(appState.onboardingTitle)
                    .font(.title3)
                    .fontWeight(.semibold)
                Text(appState.onboardingDescription)
                    .font(.callout)
                    .foregroundStyle(.secondary)
            }

            Section("Knowledge vault") {
                Text("Choose where this app should create and manage your Obsidian knowledge vault.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                TextField("Vault folder path", text: $vaultPath)
            }

            Section("Feishu connection") {
                Text("Paste the credentials from your Feishu app settings.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                TextField("App ID", text: $feishuAppID)
                SecureField("App Secret", text: $feishuAppSecret)
                SecureField("Verification Token", text: $feishuVerificationToken)
                SecureField("Encrypt Key", text: $feishuEncryptKey)
            }

            Section("Search enhancement") {
                Text("Optional, but recommended. This helps the assistant add relevant web context to saved content.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                SecureField("Tavily API Key", text: $tavilyAPIKey)
            }

            if let lastError = appState.lastError {
                Section {
                    Text(lastError)
                        .font(.caption)
                        .foregroundStyle(.red)
                }
            }

            Section {
                Button(appState.primaryActionLabel) {
                let config = ProductConfiguration(
                    vaultRoot: vaultPath,
                    feishuAppID: feishuAppID,
                    feishuAppSecret: feishuAppSecret,
                    feishuVerificationToken: feishuVerificationToken,
                    feishuEncryptKey: feishuEncryptKey,
                    tavilyAPIKey: tavilyAPIKey
                )
                do {
                    try appState.saveConfiguration(config)
                } catch {
                    appState.lastError = error.localizedDescription
                }
            }
            }
        }
        .formStyle(.grouped)
        .frame(width: 520)
        .padding()
    }
}
