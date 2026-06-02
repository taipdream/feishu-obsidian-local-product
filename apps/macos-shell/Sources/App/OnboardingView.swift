import SwiftUI

struct OnboardingView: View {
    @State var vaultPath: String = "\(FileManager.default.homeDirectoryForCurrentUser.path)/Documents/InsightVault"
    @State var feishuAppID: String = ""
    @State var feishuAppSecret: String = ""

    var body: some View {
        Form {
            TextField("Vault path", text: $vaultPath)
            TextField("Feishu App ID", text: $feishuAppID)
            SecureField("Feishu App Secret", text: $feishuAppSecret)
            Button("Save and Continue") {}
        }
        .frame(width: 480)
        .padding()
    }
}
