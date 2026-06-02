import SwiftUI

@main
struct FeishuObsidianLocalApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        MenuBarExtra("Feishu Obsidian Local", systemImage: "tray.full") {
            StatusMenuView(appState: appState)
        }
        WindowGroup("Feishu Obsidian Local") {
            if appState.shouldShowOnboardingWindow {
                OnboardingView(appState: appState)
            } else {
                StatusMenuView(appState: appState)
            }
        }
    }
}
