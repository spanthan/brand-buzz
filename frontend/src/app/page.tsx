"use client";

import React, { useState } from "react";
import GraphCanvas, { GraphLink, GraphNode } from "./components/GraphCanvas";
import CommentsPanel from "./components/CommentsPanel";
import TikTokEmbed from "./components/TikTokEmbed";
import LoadingOverlay from "./components/LoadingOverlay";
import { useComments } from "./hooks/useComments";

export default function BrandBuzz() {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tiktokUrl, setTiktokUrl] = useState("");
  const comments = useComments();

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/comments`);
      const data = await response.json();
      setGraphData(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="w-screen min-h-screen bg-cover bg-center"
      style={{ backgroundImage: 'url("/bg_img.jpg")' }}
    >
      {/* Optional dark overlay */}
      <div className="min-h-screen bg-black/40 text-white">
        {loading && <LoadingOverlay />}

        {/* Title */}
        <main className="px-8 py-6 space-y-6 text-white">
          <h1 className="text-3xl font-semibold">TikTok Comment Analyzer</h1>

          {/* URL Input + Analyze Button */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-4">
            <label htmlFor="tiktok-url" className="block text-sm mb-2">
              Enter TikTok URL
            </label>
            <div className="flex gap-2">
              <input
                id="tiktok-url"
                type="text"
                value={tiktokUrl}
                onChange={(e) => setTiktokUrl(e.target.value)}
                placeholder="e.g., https://www.tiktok.com/@username/video/1234567890"
                className="flex-grow p-2 rounded bg-white/20 text-white placeholder-zinc-300 border border-white/30"
              />
              <button
                onClick={fetchGraphData}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
              >
                Analyze
              </button>
            </div>
          </div>

          {/* Main Layout: Left (Graph), Right (Comments + TikTok) */}
          <div className="flex gap-6">
            {/* Left: Graph */}
            <div className="flex-1 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-4 min-h-[500px]">
              {graphData?.nodes?.length > 0 && (
                <GraphCanvas
                  graphData={graphData}
                  setSelectedKeyword={setSelectedKeyword}
                />
              )}
            </div>

            {/* Right: Comments and TikTok */}
            <div className="w-[400px] flex flex-col gap-4">
              {/* Comments Panel */}
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg overflow-hidden">
                <h2 className="text-lg font-semibold px-4 pt-4 text-white">Scraped Comments</h2>
                <CommentsPanel
                  comments={comments}
                  selectedKeyword={selectedKeyword}
                  onClearKeyword={() => setSelectedKeyword(null)}
                />
              </div>

              {/* TikTok Panel */}
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-4 min-h-[200px] flex items-center justify-center">
                <TikTokEmbed />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

