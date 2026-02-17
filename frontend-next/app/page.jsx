"use client";

import { useState, useCallback } from "react";
import { ReportProcessor } from "@/components/ReportProcessor";
import { ExtractionHistory } from "@/components/ExtractionHistory";

export default function Home() {
  const [historyTrigger, setHistoryTrigger] = useState(0);

  const handleProcessSuccess = useCallback(() => {
    setHistoryTrigger((t) => t + 1);
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-lg mx-auto flex flex-col gap-8">
        <ReportProcessor onProcessSuccess={handleProcessSuccess} />
        <ExtractionHistory refetchTrigger={historyTrigger} />
      </div>
    </main>
  );
}
