// components/CommentsPanel.tsx
"use client";
import React from "react";
import { Comment } from "../hooks/useComments";

interface CommentsPanelProps {
  comments: Comment[];
  selectedKeyword: string | null;
  show: boolean;
  onClearKeyword: () => void;
  onToggleShow: () => void;
}

export default function CommentsPanel({
  comments,
  selectedKeyword,
  show,
  onClearKeyword,
  onToggleShow
}: CommentsPanelProps) {

  const filtered = selectedKeyword
    ? comments.filter(comment =>
        comment.keywords.map(k => k.toLowerCase().trim()).includes(selectedKeyword.toLowerCase().trim())
      )
    : comments;

  return (
    <div className="absolute top-4 right-4 w-[300px] bg-white bg-opacity-90 rounded-xl shadow-lg z-20">
      <button
        onClick={onToggleShow}
        className="w-full px-4 py-2 text-left font-semibold bg-pink-100 hover:bg-pink-200 rounded-t-xl"
      >
        {show ? "Hide Selected Comments" : "Show Selected Comments"}
      </button>

      {show && (
        <div className="max-h-[400px] overflow-y-auto p-4 text-sm text-black space-y-2">
          {selectedKeyword && (
            <div className="text-sm font-medium text-gray-600 mb-2">
              Showing comments about: <span className="text-black">{selectedKeyword}</span>
              <button
                onClick={onClearKeyword}
                className="ml-2 text-pink-500 text-xs underline"
              >
                Clear
              </button>
            </div>
          )}

          {filtered.length === 0 ? (
            <p>No comments loaded.</p>
          ) : (
            filtered.map((comment, i) => (
              <p key={i} className="border-b border-gray-200 pb-2">
                {comment.text}
              </p>
            ))
          )}
        </div>
      )}
    </div>
  );
}
