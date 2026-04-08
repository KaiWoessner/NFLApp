const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Cannot reach the Flask API at http://127.0.0.1:5001. Start the backend server or set VITE_API_BASE if your API is running somewhere else.",
    );
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return data;
}

export function fetchMeta(signal) {
  return request("/api/meta", { signal });
}

export function fetchGames(params, signal) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  return request(`/api/games?${search.toString()}`, { signal });
}

export function fetchGameDetails(payload, signal) {
  return request("/api/game-details", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function fetchRankings(season, signal) {
  return request(`/api/rankings?season=${season}`, { signal });
}
