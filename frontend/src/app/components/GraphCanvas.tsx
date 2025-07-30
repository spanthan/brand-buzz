// components/GraphCanvas.tsx
"use client";
import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { BaseType } from "d3";

export interface GraphNode extends d3.SimulationNodeDatum {
  keyword: string;
  weight: number;
  sentiment?: string;
}

export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number;
}

interface GraphCanvasProps {
  graphData: { nodes: GraphNode[]; links: GraphLink[] } | null;
  setSelectedKeyword: (keyword: string | null) => void;
}

export default function GraphCanvas({ graphData, setSelectedKeyword }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!graphData) return;

    const { nodes, links } = graphData;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const width = 600;
    const height = 500;

    const margin = 100; // add padding
    svg.attr("viewBox", [-margin, -margin, width + margin * 2, height + margin * 2]);

    const container = svg.append("g");

    const zoom = d3.zoom<SVGSVGElement, unknown>()
    .filter((event) => {
      // Don't capture normal scroll (wheel without ctrlKey)
      if (event.type === "wheel" && event.ctrlKey === false) return false;
      return true;
    })
    .scaleExtent([0.1, 5])
    .on("zoom", (event) => {
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
      .attr("fill", "white")
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

  return (
    <div className="w-full h-full overflow-auto">
      <svg
        ref={svgRef}
        className="w-full"
        style={{ display: "block", marginTop: "0" }}
      />
    </div>
  );
}
