"use client";

import { useEffect, useState } from "react";
import { getHistory, getDownloadUrl } from "@/lib/historyService";

export function ExtractionHistory({ onRefetch, refetchTrigger }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setHistory(data);
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [refetchTrigger]);

  if (loading && history.length === 0) {
    return (
      <div className="w-full max-w-lg bg-white rounded-xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Recent extractions
        </h2>
        <p className="text-sm text-gray-500">Loading…</p>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="w-full max-w-lg bg-white rounded-xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Recent extractions
        </h2>
        <p className="text-sm text-gray-500">
          No history yet. Process some PDFs to see them here. History is saved
          when Supabase is configured for the backend.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-lg bg-white rounded-xl shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-3">
        Recent extractions
      </h2>
      <ul className="space-y-3">
        {history.map((item) => (
          <li
            key={item.id}
            className="border border-gray-200 rounded-lg p-3 flex flex-col gap-2"
          >
            <div className="flex justify-between items-start gap-2">
              <span className="text-sm text-gray-500">
                {formatDate(item.created_at)}
              </span>
              <a
                href={getDownloadUrl(item.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-blue-600 hover:text-blue-800 whitespace-nowrap"
              >
                Download Excel
              </a>
            </div>
            <ul className="text-sm text-gray-700 space-y-0.5">
              {(item.input_file_names || []).map((name, i) => (
                <li key={i} className="truncate">
                  {name}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatDate(isoString) {
  if (!isoString) return "—";
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}
