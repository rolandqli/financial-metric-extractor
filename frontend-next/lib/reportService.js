const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Send one or more PDF files to the backend for processing.
 *
 * @param {FileList | File[]} files - The files to upload.
 * @returns {Promise<Blob>} - The Excel file as a Blob.
 */
export async function processReports(files) {
  if (!files || files.length === 0) {
    throw new Error("No files provided");
  }

  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE_URL}/reports/process`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Processing failed");
  }

  return response.blob();
}
