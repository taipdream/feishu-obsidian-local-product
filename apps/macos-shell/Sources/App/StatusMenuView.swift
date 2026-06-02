import SwiftUI

struct StatusMenuView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Feishu Obsidian Local")
                .font(.headline)
            Text("Status endpoint: http://127.0.0.1:8787/status")
                .font(.caption)
            Text("Action needed: Finish onboarding")
                .font(.caption)
        }
        .padding()
    }
}
