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
            TextField("Vault path", text: $vaultPath)
            TextField("Feishu App ID", text: $feishuAppID)
            SecureField("Feishu App Secret", text: $feishuAppSecret)
            SecureField("Feishu Verification Token", text: $feishuVerificationToken)
            SecureField("Feishu Encrypt Key", text: $feishuEncryptKey)
            SecureField("Tavily API Key", text: $tavilyAPIKey)
            Button("Save and Continue") {
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
        .frame(width: 480)
        .padding()
    }
}
