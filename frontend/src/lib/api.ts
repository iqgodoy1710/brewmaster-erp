const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const ACCESS_TOKEN_STORAGE_KEY = "brewmaster_access_token";

export const isDemoMode =
  import.meta.env.VITE_DEMO_MODE === "true";

export const isAuthRequired =
  import.meta.env.VITE_AUTH_REQUIRED === "true";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const accessToken = getAccessToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken
        ? { Authorization: `Bearer ${accessToken}` }
        : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);

    throw new Error(
      data?.detail ?? "The request could not be completed.",
    );
  }

  return response.json() as Promise<T>;
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path);
}

export function apiPatch<T>(
  path: string,
  body: unknown,
): Promise<T> {
  return apiRequest<T>(path, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function apiPost<T>(
  path: string,
  body?: unknown,
): Promise<T> {
  return apiRequest<T>(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}