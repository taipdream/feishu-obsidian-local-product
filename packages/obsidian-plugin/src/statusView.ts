import type { BackendStatus } from "./settings";

export function renderStatusSummary(status: BackendStatus): string {
  return [
    `Backend running: ${status.backend_running}`,
    `Vault ready: ${status.vault_ready}`,
    `Feishu connected: ${status.feishu_connected}`,
  ].join("\n");
}
