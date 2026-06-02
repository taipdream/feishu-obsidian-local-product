import Foundation

final class BackendProcessController {
    private var process: Process?
    private let bundleLocator: BackendBundleLocator

    init(bundleLocator: BackendBundleLocator = BackendBundleLocator()) {
        self.bundleLocator = bundleLocator
    }

    func startBackend(executableURL: URL? = nil) throws {
        let process = Process()
        process.executableURL = executableURL ?? bundleLocator.backendEntryPoint()
        try process.run()
        self.process = process
    }

    func stopBackend() {
        process?.terminate()
        process = nil
    }
}
