const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

interface ErrorResponse {
  message?: string;
  detail?: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  if (!API_URL) {
    throw new ApiError("NEXT_PUBLIC_API_URL is not configured.", 500);
  }

  const {
    data: { session },
  } = await getSupabaseBrowserClient().auth.getSession();

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(session?.access_token
          ? { Authorization: `Bearer ${session.access_token}` }
          : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Unable to reach the TalentFlow API. Make sure the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    const error = (await response.json().catch(() => ({}))) as ErrorResponse;
    throw new ApiError(
      error.message ?? error.detail ?? "The request could not be completed.",
      response.status,
    );
  }

  return response.json() as Promise<T>;
}
import { getSupabaseBrowserClient } from "@/lib/supabase/client";
