"use client";

import { useEffect, useState } from "react";
import { processReports } from "@/lib/reportService";

export function ReportProcessor() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [excelUrl, setExcelUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    return () => {
      if (excelUrl) {
        URL.revokeObjectURL(excelUrl);
      }
    };
  }, [excelUrl]);

  function handleFileChange(event) {
    setFiles(event.target.files);
    setExcelUrl(null);
    setError("");
  }

  async function handleProcess() {
    if (!files || files.length === 0) {
      setError("Please add at least one PDF to process.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const blob = await processReports(files);
      const url = window.URL.createObjectURL(blob);
      setExcelUrl(url);
    } catch (err) {
      console.error(err);
      setError("Something went wrong while processing the files.");
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    if (!excelUrl) return;

    const link = document.createElement("a");
    link.href = excelUrl;
    link.download = "pdf_report.xlsx";
    link.click();
  }

  return (
    <div className="w-full max-w-lg bg-white rounded-xl shadow-md p-6 space-y-6">
      <header className="text-center space-y-1">
        <h1 className="text-xl font-semibold text-gray-900">
          Earnings PDF Extractor
        </h1>
        <p className="text-sm text-gray-500">
          Upload earnings and export key metrics to Excel
        </p>
      </header>

      <div className="space-y-2">
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-md file:border-0
                     file:text-sm file:font-medium
                     file:bg-gray-100 file:text-gray-700
                     hover:file:bg-gray-200"
        />
      </div>

      {files && files.length > 0 && (
        <div className="border rounded-md p-3 bg-gray-50">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Selected files
          </h3>
          <ul className="text-sm text-gray-600 space-y-1 max-h-32 overflow-auto">
            {Array.from(files).map((file, index) => (
              <li key={index} className="truncate">
                {file.name}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleProcess}
          disabled={loading}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md
                     hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Processing…" : "Process"}
        </button>

        {excelUrl && (
          <button
            onClick={handleDownload}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md
                       hover:bg-green-700"
          >
            Download Excel
          </button>
        )}
      </div>
    </div>
  );
}
