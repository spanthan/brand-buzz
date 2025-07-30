"use client";
import React, { useState } from "react";
import TikTokEmbed from "./components/TikTokEmbed";
import GraphCanvas, { GraphNode, GraphLink } from "./components/GraphCanvas";
import { useComments } from "./hooks/useComments";
import CommentsPanel from "./components/CommentsPanel";
import Header from "./components/Header";
import LoadingOverlay from "./components/LoadingOverlay"

export default function BrandBuzz() {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] } | null>(null);
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const comments = useComments();

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/graph`);
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
      className="w-screen min-h-screen bg-cover bg-center relative"
      style={{ backgroundImage: 'url("/bg_img.jpg")' }}
    >
      {loading && <LoadingOverlay />}
  
      {/* Header */}
      <Header onGenerate={fetchGraphData} loading={loading} />
  
      {/* Main content */}
      <main className="flex p-4 gap-6 h-[calc(100%-140px)] relative">
        {/* Left: TikTok */}
        <section className="w-[340px]">
          <TikTokEmbed />
        </section>
  
        {/* Center: Graph + Comments */}
        <section className="flex-1 relative">
          <GraphCanvas graphData={graphData} setSelectedKeyword={setSelectedKeyword} />
          <CommentsPanel
            comments={comments}
            selectedKeyword={selectedKeyword}
            show={showComments}
            onClearKeyword={() => setSelectedKeyword(null)}
            onToggleShow={() => setShowComments(prev => !prev)}
          />
        </section>
      </main>
    </div>
  );
}
