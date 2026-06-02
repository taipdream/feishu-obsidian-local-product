import Foundation

struct BackendStatus: Decodable {
    let backend_running: Bool
    let vault_ready: Bool
    let feishu_connected: Bool
    let last_ingest_status: String
    let last_reply_status: String
    let action_needed: String
}
