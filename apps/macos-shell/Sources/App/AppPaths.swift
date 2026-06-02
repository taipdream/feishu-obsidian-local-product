import Foundation

enum AppPaths {
    static let backendBundleDirectoryName = "backend-bundle"
    static let backendEntrypointName = "run_backend"
    static let requiredVaultDirectories = [
        "00 Inbox",
        "01 Sources",
        "02 Themes",
        "03 Ideas",
        "04 Playbooks",
        "05 Reviews",
        "06 Answers",
        "99 System",
        "Assets",
    ]

    static func defaultAppSupportDirectory(fileManager: FileManager = .default) -> URL {
        fileManager.homeDirectoryForCurrentUser
            .appendingPathComponent("Library")
            .appendingPathComponent("Application Support")
            .appendingPathComponent("FeishuObsidianLocal")
    }

    static func defaultConfigURL(fileManager: FileManager = .default) -> URL {
        defaultAppSupportDirectory(fileManager: fileManager)
            .appendingPathComponent("config.json")
    }
}
