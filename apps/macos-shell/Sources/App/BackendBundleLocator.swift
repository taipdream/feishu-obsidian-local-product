import Foundation

struct BackendBundleLocator {
    var fileManager: FileManager
    var environment: [String: String]
    var mainBundleResourceURL: URL?

    init(
        fileManager: FileManager = .default,
        environment: [String: String] = ProcessInfo.processInfo.environment,
        mainBundleResourceURL: URL? = Bundle.main.resourceURL
    ) {
        self.fileManager = fileManager
        self.environment = environment
        self.mainBundleResourceURL = mainBundleResourceURL
    }

    func backendEntryPoint() -> URL {
        if let override = environment["FEISHU_OBSIDIAN_LOCAL_BACKEND_ENTRYPOINT"], !override.isEmpty {
            return URL(fileURLWithPath: override)
        }

        let resourceURL = mainBundleResourceURL
            ?? URL(fileURLWithPath: fileManager.currentDirectoryPath)

        return resourceURL
            .appendingPathComponent(AppPaths.backendBundleDirectoryName)
            .appendingPathComponent(AppPaths.backendEntrypointName)
    }
}
