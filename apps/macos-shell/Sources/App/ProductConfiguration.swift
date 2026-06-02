import Foundation

struct ProductConfiguration: Codable, Equatable {
    let vaultRoot: String
    let feishuAppID: String
    let feishuAppSecret: String
    let feishuVerificationToken: String
    let feishuEncryptKey: String
    let tavilyAPIKey: String
}
