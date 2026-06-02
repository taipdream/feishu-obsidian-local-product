import SwiftUI

struct StatusMenuView: View {
    @ObservedObject var appState: AppState

    var body: some View {
        Group {
            if appState.isConfigured {
                VStack(alignment: .leading, spacing: 8) {
                    Text(appState.statusHeadline)
                        .font(.headline)
                    Text(appState.statusDetail)
                        .font(.caption)
                    Text("Vault location")
                        .font(.caption2)
                        .fontWeight(.semibold)
                    if let configuration = appState.configuration {
                        Text(configuration.vaultRoot)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                    if let lastError = appState.lastError {
                        Text(lastError)
                            .font(.caption2)
                            .foregroundStyle(.red)
                    }
                    Button("Refresh Status") {
                        do {
                            try appState.refreshStatus()
                        } catch {
                            appState.lastError = error.localizedDescription
                        }
                    }
                    Button(appState.primaryActionLabel) {
                        do {
                            if appState.backendRunning {
                                appState.stopBackend()
                            } else {
                                try appState.startBackend()
                            }
                        } catch {
                            appState.lastError = error.localizedDescription
                        }
                    }
                }
                .padding()
                .frame(width: 320)
            } else {
                OnboardingView(appState: appState)
            }
        }
    }
}
