import SwiftUI

@main
struct FeishuObsidianLocalApp: App {
    var body: some Scene {
        MenuBarExtra("Feishu Obsidian Local", systemImage: "tray.full") {
            StatusMenuView()
        }
    }
}
