import { apiRequest } from "@/services/api-client";

export interface GmailConnection {
  oauth_configured: boolean;
  connected: boolean;
  gmail_address: string | null;
  scopes: string[];
  status: string;
  last_error: string | null;
  last_synced_at: string | null;
  token_expires_at: string | null;
  send_acknowledgment_emails: boolean;
}

interface GmailConnectionResponse {
  success: boolean;
  message: string;
  data: GmailConnection;
}

interface GmailAuthorizationResponse {
  success: boolean;
  message: string;
  data: {
    authorization_url: string;
  };
}

export interface GmailProcessResult {
  messages_scanned: number;
  messages_processed: number;
  attachments_stored: number;
  duplicates_skipped: number;
  unsupported_skipped: number;
  errors: number;
}

interface GmailProcessResponse {
  success: boolean;
  message: string;
  data: GmailProcessResult;
}

export async function getGmailConnection(): Promise<GmailConnection> {
  const response = await apiRequest<GmailConnectionResponse>("/gmail/status");
  return response.data;
}

export async function getGmailAuthorizationUrl(): Promise<string> {
  const response = await apiRequest<GmailAuthorizationResponse>(
    "/gmail/oauth/authorize",
  );
  return response.data.authorization_url;
}

export async function disconnectGmail(): Promise<void> {
  await apiRequest("/gmail/connection", { method: "DELETE" });
}

export async function updateGmailSettings(
  sendAcknowledgmentEmails: boolean,
): Promise<GmailConnection> {
  const response = await apiRequest<GmailConnectionResponse>("/gmail/settings", {
    method: "PATCH",
    body: JSON.stringify({
      send_acknowledgment_emails: sendAcknowledgmentEmails,
    }),
  });
  return response.data;
}

export async function processGmailInbox(): Promise<GmailProcessResult> {
  const response = await apiRequest<GmailProcessResponse>("/gmail/process", {
    method: "POST",
    body: JSON.stringify({ max_messages: 25 }),
  });
  return response.data;
}
