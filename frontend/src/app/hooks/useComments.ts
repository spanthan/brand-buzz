// components/useComments.ts
"use client";
import { useEffect, useState } from "react";

export interface Comment {
  text: string;
  keywords: string[];
}

export function useComments() {
  const [comments, setComments] = useState<Comment[]>([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE}/comments`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setComments(data);
        } else {
          console.error("Invalid /comments response:", data);
        }
      })
      .catch(err => console.error("Error fetching comments:", err));
  }, []);

  return comments;
}
