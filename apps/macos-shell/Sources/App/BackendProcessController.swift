import Foundation

final class BackendProcessController {
    private var process: Process?

    func startBackend(executableURL: URL) throws {
        let process = Process()
        process.executableURL = executableURL
        try process.run()
        self.process = process
    }

    func stopBackend() {
        process?.terminate()
        process = nil
    }
}
