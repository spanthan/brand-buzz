// components/HeaderBar.tsx
"use client";
import React from "react";

interface HeaderBarProps {
  onGenerate: () => void;
  loading: boolean;
}

export default function HeaderBar({ onGenerate, loading }: HeaderBarProps) {
  return (
    <header className="p-4 text-white">
      <h1 className="text-2xl font-bold mb-2">Brand Buzz</h1>
      <div className="flex gap-4">
        <button
          onClick={onGenerate}
          className="bg-white text-black px-4 py-2 rounded shadow"
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Graph"}
        </button>
      </div>
    </header>
  );
}
