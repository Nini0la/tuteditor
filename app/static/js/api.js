export class ApiError extends Error {
  constructor(message, { code = "API_ERROR", status = 500, payload = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.payload = payload;
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  if (!text) {
    return null;
  }

  return { message: text };
}

export async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await parseResponse(response);

  if (!response.ok) {
    const errorCode = payload?.error?.code ?? `HTTP_${response.status}`;
    const errorMessage = payload?.error?.message ?? payload?.message ?? "Request failed";
    throw new ApiError(errorMessage, {
      code: errorCode,
      status: response.status,
      payload,
    });
  }

  return payload;
}
