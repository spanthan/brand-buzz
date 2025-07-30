"use client";
import TikTokEmbed from "./components/TikTokEmbed"; // adjust path if needed

import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { BaseType } from "d3";

interface GraphNode extends d3.SimulationNodeDatum {
  keyword: string;
  weight: number;
  sentiment?: string;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number;
}

export default function BrandBuzz() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] } | null>(null);
  const [loading, setLoading] = useState(false);
  // const [comments, setComments] = useState<string[]>([]);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<{ text: string; keywords: string[] }[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<string | null>(null);

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

  useEffect(() => {
    if (!graphData) return;

    const { nodes, links } = graphData;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const width = 600;
    const height = 500;

    svg.attr("viewBox", [0, 0, width, height]);
    const container = svg.append("g");

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 5])
      .on("zoom", (event) => {
        // Only apply zoom if it's not just a pan (e.g. touchpad scroll)
        if (event.sourceEvent?.type === "wheel" && event.sourceEvent.ctrlKey === false) {
          return; // Let the page scroll normally
        }
        container.attr("transform", event.transform.toString());
      });

    d3.select(svgRef.current as SVGSVGElement).call(zoom);

    const linkScale = d3
      .scaleLinear()
      .domain([1, d3.max(links, (d) => d.value * 2) || 2])
      .range([2, 9]);

    const nodeRadiusScale = d3
      .scaleSqrt()
      .domain([1, d3.max(nodes, (d) => d.weight * 3) || 3])
      .range([5, 20]);

    const sentimentColorMap: Record<string, string> = {
      positive: "#a8e6a1", // light green
      neutral: "#fdfd96",  // light yellow
      negative: "#cd5c5c"  // light red
    };

    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links).id(d => d.keyword).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = container.append("g")
      .attr("stroke", "#ffffffcc")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-linecap", "round")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", d => linkScale(d.value));

    const tooltip = d3.select("body").append("div")
      .style("position", "absolute")
      .style("padding", "6px 12px")
      .style("background", "#222")
      .style("color", "#fff")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    const sentimentMap: Record<string, string> = {
      positive: "🟢 Positive",
      neutral: "🟡 Neutral",
      negative: "🔴 Negative"
    };

    const nodeGroup = container.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5);
    const nodesSel = nodeGroup.selectAll<SVGCircleElement, GraphNode>("circle")
      .data(nodes)
      .join("circle")
      .attr("r", d => nodeRadiusScale(d.weight))
      .attr("fill", d => sentimentColorMap[d.sentiment || "neutral"]);

    nodesSel.call(
      d3.drag<SVGCircleElement, GraphNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    )
    .on("mouseover", (event, d) => {
      tooltip.style("opacity", 1)
        .style("left", `${event.pageX + 10}px`)
        .style("top", `${event.pageY + 10}px`)
        .html(`
          <strong>${d.keyword}</strong><br/>
          Sentiment: ${sentimentMap[d.sentiment || "neutral"]}<br/>
          Mentions: <strong>${d.weight}</strong>
        `);
    })
    .on("mousemove", (event) => {
      tooltip
        .style("left", `${event.pageX + 10}px`)
        .style("top", `${event.pageY + 10}px`);
    })
    .on("mouseout", () => {
      tooltip.style("opacity", 0);
    })
    .on("click", (event, d) => {
      setSelectedKeyword(d.keyword); // this will filter the comments list
    });

    const label = container.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.keyword)
      .attr("font-size", "8px")
      .attr("font-weight", "italics")
      .attr("font-family", "Helvetica")
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .attr("dy", "2.5em");

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as GraphNode).x!)
        .attr("y1", (d) => (d.source as GraphNode).y!)
        .attr("x2", (d) => (d.target as GraphNode).x!)
        .attr("y2", (d) => (d.target as GraphNode).y!);

      nodesSel
        .attr("cx", (d) => d.x!)
        .attr("cy", (d) => d.y!);

      label.attr("x", (d) => d.x!).attr("y", (d) => d.y!);
    });
  }, [graphData]);

  useEffect(() => {
      fetch(`${process.env.NEXT_PUBLIC_API_BASE}/graph`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setComments(data); // each comment has text + keywords
        } else {
          console.error("Invalid /comments response:", data);
        }
      })
      .catch(err => console.error("Error fetching comments:", err));
  }, []);

  return (
    <div
      className="w-screen min-h-screen bg-cover bg-center relative"
      style={{ backgroundImage: 'url("/bg_img.jpg")' }}
    >
      {loading && (
        <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none">
          <div className="bg-white text-black p-6 rounded-lg shadow-xl z-50 pointer-events-auto">
            <div className="border-4 border-pink-500 border-t-transparent rounded-full w-12 h-12 animate-spin"></div>
          </div>
        </div>
      )}
  
      <h1 className="text-2xl font-bold mb-2 text-white p-4">Brand Buzz</h1>
  
      <div className="p-4 flex gap-4">
        <button
          onClick={fetchGraphData}
          className="bg-white text-black px-4 py-2 rounded shadow"
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Graph"}
        </button>
      </div>
  
      <div className="flex p-4 gap-6 h-[calc(100%-140px)] relative">
        {/* Left panel – TikTok */}
        <div className="w-[340px]">
          <TikTokEmbed />
        </div>
  
        {/* Center panel – Graph + Comment dropdown */}
        <div className="flex-1 relative">
          <svg
            ref={svgRef}
            className="w-full h-full touch-pan-y"
            style={{ touchAction: "pan-y" }}
          />
  
          {/* Right top dropdown panel */}
          <div className="absolute top-4 right-4 w-[300px] bg-white bg-opacity-90 rounded-xl shadow-lg z-20">
            <button
              onClick={() => setShowComments(!showComments)}
              className="w-full px-4 py-2 text-left font-semibold bg-pink-100 hover:bg-pink-200 rounded-t-xl"
            >
              {showComments ? "Hide Selected Comments" : "Show Selected Comments"}
            </button>

            {showComments && (
              <div className="max-h-[400px] overflow-y-auto p-4 text-sm text-black space-y-2">
                {selectedKeyword && (
                  <div className="text-sm font-medium text-gray-600 mb-2">
                    Showing comments about: <span className="text-black">{selectedKeyword}</span>
                    <button
                      onClick={() => setSelectedKeyword(null)}
                      className="ml-2 text-pink-500 text-xs underline"
                    >
                      Clear
                    </button>
                  </div>
                )}
                
                {comments.length === 0 ? (
                  <p>No comments loaded.</p>
                ) : (
                  comments
                    .filter(comment => {
                      const match = !selectedKeyword || comment.keywords
                        .map(k => k.toLowerCase().trim())
                        .includes(selectedKeyword?.toLowerCase().trim());

                      console.log({
                        text: comment.text,
                        keywords: comment.keywords,
                        selectedKeyword,
                        match
                      });

                      return match;
                    })
                    .map((comment, i) => {
                      return (
                        <p key={i} className="border-b border-gray-200 pb-2">
                          {comment.text}
                        </p>
                      );
                    })
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

