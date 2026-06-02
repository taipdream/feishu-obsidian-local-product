export type BackendStatus = {
  backend_running: boolean;
  vault_ready: boolean;
  feishu_connected: boolean;
  last_ingest_status: string;
  last_reply_status: string;
  action_needed: string;
};

export async function fetchBackendStatus(baseUrl: string): Promise<BackendStatus> {
  const response = await fetch(`${baseUrl}/status`);
  return response.json() as Promise<BackendStatus>;
}
