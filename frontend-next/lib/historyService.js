const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Fetch recent extraction history from the backend.
 * @returns {Promise<Array<{ id: string, created_at: string, input_file_names: string[] }>>}
 */
export async function getHistory() {
  const response = await fetch(`${API_BASE_URL}/reports/history`);
  if (!response.ok) {
    return [];
  }
  const data = await response.json();
  return Array.isArray(data) ? data : [];
}

/**
 * URL to download an extraction's Excel file (opens in same tab or use as link href).
 * @param {string} extractionId
 * @returns {string}
 */
export function getDownloadUrl(extractionId) {
  return `${API_BASE_URL}/reports/history/${extractionId}/download`;
}
