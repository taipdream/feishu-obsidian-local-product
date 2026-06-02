import Foundation

final class AppState {
    let defaultVaultPath: String

    init() {
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        self.defaultVaultPath = "\(home)/Documents/InsightVault"
    }
}
