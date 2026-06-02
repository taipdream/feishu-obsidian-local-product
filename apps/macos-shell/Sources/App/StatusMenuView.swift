import SwiftUI

struct StatusMenuView: View {
    @ObservedObject var appState: AppState

    var body: some View {
        Group {
            if appState.isConfigured {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Feishu Obsidian Local")
                        .font(.headline)
                    Text(appState.statusMessage)
                        .font(.caption)
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
                    Button(appState.backendRunning ? "Stop Backend" : "Start Backend") {
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
