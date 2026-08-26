const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const ACCESS_TOKEN_STORAGE_KEY = "brewmaster_access_token";

const RETRY_DELAYS_MS = [0, 5000, 15000, 30000];

type ApiRequestOptions = {
  retryOnTemporaryFailure?: boolean;
};

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

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

function isTemporaryServerError(status: number): boolean {
  return status === 502 || status === 503 || status === 504;
}

async function getErrorMessage(response: Response): Promise<string> {
  const data = await response.json().catch(() => null);

  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data &&
    typeof data.detail === "string"
  ) {
    return data.detail;
  }

  return "The request could not be completed.";
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  requestOptions: ApiRequestOptions = {},
): Promise<T> {
  const shouldRetry = requestOptions.retryOnTemporaryFailure ?? false;
  const delays = shouldRetry ? RETRY_DELAYS_MS : [0];
  let lastTemporaryError: Error | null = null;

  for (const [attempt, delay] of delays.entries()) {
    if (delay > 0) {
      await wait(delay);
    }

    try {
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

      if (response.ok) {
        return response.json() as Promise<T>;
      }

      const error = new Error(await getErrorMessage(response));

      if (
        shouldRetry &&
        isTemporaryServerError(response.status) &&
        attempt < delays.length - 1
      ) {
        lastTemporaryError = error;
        continue;
      }

      throw error;
    } catch (caughtError) {
      const error =
        caughtError instanceof Error
          ? caughtError
          : new Error("The request could not be completed.");

      const isNetworkError = caughtError instanceof TypeError;

      if (
        shouldRetry &&
        isNetworkError &&
        attempt < delays.length - 1
      ) {
        lastTemporaryError = error;
        continue;
      }

      throw error;
    }
  }

  throw new Error(
    lastTemporaryError
      ? "El servidor se está iniciando. Esperá un momento y reintentá."
      : "The request could not be completed.",
  );
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(
    path,
    {},
    { retryOnTemporaryFailure: true },
  );
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
  requestOptions: ApiRequestOptions = {},
): Promise<T> {
  return apiRequest<T>(
    path,
    {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    },
    requestOptions,
  );
}

export function apiDelete<T>(path: string): Promise<T> {
  return apiRequest<T>(path, {
    method: "DELETE",
  });
}