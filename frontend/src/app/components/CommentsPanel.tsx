"use client";
import React from "react";
import { Comment } from "../hooks/useComments";

interface CommentsPanelProps {
  comments: Comment[];
  selectedKeyword: string | null;
  onClearKeyword: () => void;
}

export default function CommentsPanel({
  comments,
  selectedKeyword,
  onClearKeyword
}: CommentsPanelProps) {
  const filtered = selectedKeyword
    ? comments.filter(comment =>
        comment.keywords.map(k => k.toLowerCase().trim()).includes(selectedKeyword.toLowerCase().trim())
      )
    : comments;

  return (
    <div className="w-full h-full flex flex-col">
      {/* Optional header */}
      {selectedKeyword && (
        <div className="text-sm font-medium text-zinc-200 px-4 pt-4">
          Showing comments about:{" "}
          <span className="text-white font-semibold">{selectedKeyword}</span>
          <button
            onClick={onClearKeyword}
            className="ml-2 text-pink-300 text-xs underline hover:text-pink-400"
          >
            Clear
          </button>
        </div>
      )}

      {/* Scrollable comment list */}
      <div className="flex-1 overflow-y-auto px-4 pb-4 pt-2 text-sm text-white space-y-2 max-h-[200px]">
        {filtered.length === 0 ? (
          <p className="text-zinc-300">No comments loaded.</p>
        ) : (
          filtered.map((comment, i) => (
            <p key={i} className="border-b border-white/10 pb-2">
              {comment.text}
            </p>
          ))
        )}
      </div>
    </div>
  );
}
