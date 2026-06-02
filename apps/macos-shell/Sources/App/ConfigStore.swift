import Foundation

final class ConfigStore {
    let configURL: URL

    init(configURL: URL) {
        self.configURL = configURL
    }

    func save(_ payload: [String: Any]) throws {
        try FileManager.default.createDirectory(
            at: configURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        let data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted])
        try data.write(to: configURL)
    }

    func load() throws -> [String: Any] {
        guard FileManager.default.fileExists(atPath: configURL.path) else { return [:] }
        let data = try Data(contentsOf: configURL)
        return try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]
    }
}
