import Foundation

protocol BackendStatusProviding {
    func fetchStatus() throws -> BackendStatus
}

struct HTTPBackendStatusProvider: BackendStatusProviding {
    var baseURL: URL = URL(string: "http://127.0.0.1:8787")!

    func fetchStatus() throws -> BackendStatus {
        let url = baseURL.appendingPathComponent("status")
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(BackendStatus.self, from: data)
    }
}
