import Foundation

final class ConfigStore {
    let configURL: URL

    init(configURL: URL) {
        self.configURL = configURL
    }

    func saveConfiguration(_ payload: ProductConfiguration) throws {
        try FileManager.default.createDirectory(
            at: configURL.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )
        let data = try JSONEncoder().encode(payload)
        try data.write(to: configURL)
    }

    func loadConfiguration() throws -> ProductConfiguration? {
        guard FileManager.default.fileExists(atPath: configURL.path) else { return nil }
        let data = try Data(contentsOf: configURL)
        return try JSONDecoder().decode(ProductConfiguration.self, from: data)
    }
}
