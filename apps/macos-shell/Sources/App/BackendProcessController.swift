import Foundation

protocol BackendControlling: AnyObject {
    var isRunning: Bool { get }
    func startBackend(executableURL: URL?, environment: [String: String]) throws
    func stopBackend()
}

final class BackendProcessController: BackendControlling {
    private var process: Process?
    private let bundleLocator: BackendBundleLocator

    var isRunning: Bool {
        process?.isRunning ?? false
    }

    init(bundleLocator: BackendBundleLocator = BackendBundleLocator()) {
        self.bundleLocator = bundleLocator
    }

    func startBackend(executableURL: URL? = nil, environment: [String: String] = [:]) throws {
        let process = Process()
        process.executableURL = executableURL ?? bundleLocator.backendEntryPoint()
        if !environment.isEmpty {
            var merged = ProcessInfo.processInfo.environment
            for (key, value) in environment {
                merged[key] = value
            }
            process.environment = merged
        }
        try process.run()
        self.process = process
    }

    func stopBackend() {
        process?.terminate()
        process = nil
    }
}
