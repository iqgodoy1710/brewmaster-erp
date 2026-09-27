const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const ACCESS_TOKEN_STORAGE_KEY = "brewmaster_access_token";

const RETRY_DELAYS_MS = [0, 5000, 15000, 30000];

type ApiRequestOptions = {
  retryOnTemporaryFailure?: boolean;
};

export const isDemoMode = import.meta.env.VITE_DEMO_MODE === "true";

export const isAuthRequired = import.meta.env.VITE_AUTH_REQUIRED === "true";

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

const API_ERROR_TRANSLATIONS: Record<string, string> = {
  "Authentication is required.": "Debés iniciar sesión para continuar.",
  "Invalid or expired access token.":
    "La sesión venció o no es válida. Volvé a iniciar sesión.",
  "Invalid username or password.":
    "El nombre de usuario o la contraseña son incorrectos.",
  "You do not have permission to perform this action.":
    "No tenés permisos para realizar esta acción.",

  "The customer does not exist.": "El cliente no existe.",
  "The raw material does not exist.": "El insumo no existe.",
  "The beer presentation does not exist.": "La presentación no existe.",
  "The production batch does not exist.": "El lote de producción no existe.",
  "The recipe does not exist.": "La receta no existe.",
  "The keg does not exist.": "El barril no existe.",
  "The sale does not exist.": "La venta no existe.",
  "The delivery order does not exist.": "El pedido no existe.",

  "There is not enough stock for this movement.":
    "No hay stock suficiente para registrar este movimiento.",
  "There is not enough finished product stock for this picking quantity.":
    "No hay stock suficiente para preparar esta cantidad.",
  "There is not enough finished product stock to close this item.":
    "No hay stock suficiente para cerrar este ítem.",
  "Cannot pasteurize an inactive beer presentation.":
    "No se puede pasteurizar una presentación inactiva.",
  "Only bottle presentations can be pasteurized.":
    "Solo se pueden pasteurizar presentaciones de botella.",
  "The approved quantity cannot exceed the processed quantity.":
    "La cantidad aprobada no puede superar la cantidad procesada.",
  "There is not enough bottle stock for this pasteurization.":
    "No hay stock suficiente de botellas para esta pasteurización.",
  "The keg repackaging run does not exist.": "El embotellado no existe.",
  "The keg repackaging run has already been reversed.":
    "El embotellado ya fue revertido.",
  "The keg has subsequent movements and the repackaging cannot be reversed.":
    "El barril tiene movimientos posteriores y el embotellado no puede deshacerse.",
  "There is not enough bottle stock to reverse this repackaging.":
    "No hay stock suficiente de botellas para deshacer este embotellado.",
  "The original bottle stock movement does not exist.":
    "No se encontró el movimiento original de las botellas.",
  "The original keg movement does not exist.":
    "No se encontró el movimiento original del barril.",
};

function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return "La solicitud contiene datos incorrectos.";
    case 401:
      return "Debés iniciar sesión para continuar.";
    case 403:
      return "No tenés permisos para realizar esta acción.";
    case 404:
      return "No se encontró el recurso solicitado.";
    case 409:
      return "La operación no pudo realizarse por un conflicto con los datos actuales.";
    case 422:
      return "Revisá los datos ingresados: hay campos inválidos o incompletos.";
    default:
      if (status >= 500) {
        return "Ocurrió un error en el servidor. Intentá nuevamente.";
      }

      return "No se pudo completar la operación.";
  }
}

async function getErrorMessage(response: Response): Promise<string> {
  const data = await response.json().catch(() => null);

  if (typeof data === "object" && data !== null && "detail" in data) {
    if (typeof data.detail === "string") {
      return (
        API_ERROR_TRANSLATIONS[data.detail] ??
        getDefaultErrorMessage(response.status)
      );
    }

    if (Array.isArray(data.detail)) {
      return "Revisá los datos ingresados: hay campos inválidos o incompletos.";
    }
  }

  return getDefaultErrorMessage(response.status);
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
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
          ...options.headers,
        },
      });

      if (response.ok) {
        if (response.status === 204) {
          return undefined as T;
        }

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
      const isNetworkError = caughtError instanceof TypeError;

      const requestError = isNetworkError
        ? new Error(
            "No se pudo conectar con el servidor. Esperá unos segundos y volvé a intentarlo.",
          )
        : caughtError instanceof Error
          ? caughtError
          : new Error("No se pudo completar la operación.");

      if (shouldRetry && isNetworkError && attempt < delays.length - 1) {
        lastTemporaryError = requestError;
        continue;
      }

      throw requestError;
    }
  }

  throw new Error(
    lastTemporaryError
      ? "El servidor se está iniciando. Esperá un momento y reintentá."
      : "No se pudo completar la operación.",
  );
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path, {}, { retryOnTemporaryFailure: true });
}

export function apiPatch<T>(path: string, body: unknown): Promise<T> {
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
