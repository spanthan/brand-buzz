"use client";

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { BaseType } from "d3";

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  weight: number;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number;
}

const data: { nodes: GraphNode[]; links: GraphLink[] } = {
  nodes: [
    { id: "latte makeup", weight: 10 },
    { id: "broccoli Freckles", weight: 6 },
    { id: "micro beauty", weight: 8 },
    { id: "pregnant and nursing people", weight: 7 },
    { id: "pearl Skin", weight: 14 },
    { id: "Face yoga", weight: 9 },
    { id: "boyfriend blush", weight: 12 },
    { id: "dark skin", weight: 11 },
    { id: "sugar plum fairy", weight: 6 },
    { id: "olive skin", weight: 10 },
    { id: "sunset blush", weight: 8 },
    { id: "luminous complexion", weight: 7 },
  ],
  links: [
    { source: "latte makeup", target: "Face yoga", value: 3 },
    { source: "latte makeup", target: "sunset blush", value: 2 },
    { source: "latte makeup", target: "boyfriend blush", value: 2 },
    { source: "pearl Skin", target: "boyfriend blush", value: 4 },
    { source: "pearl Skin", target: "dark skin", value: 4 },
    { source: "dark skin", target: "olive skin", value: 3 },
    { source: "pregnant and nursing people", target: "micro beauty", value: 2 },
    { source: "pregnant and nursing people", target: "pearl Skin", value: 2 },
    { source: "sunset blush", target: "luminous complexion", value: 2 },
    { source: "sugar plum fairy", target: "Face yoga", value: 2 },
    { source: "luminous complexion", target: "sugar plum fairy", value: 1 },
    { source: "sunset blush", target: "boyfriend blush", value: 1 },
    { source: "latte makeup", target: "broccoli Freckles", value: 1 },
    { source: "latte makeup", target: "pregnant and nursing people", value: 1 },
    { source: "Face yoga", target: "boyfriend blush", value: 2 },
    { source: "micro beauty", target: "broccoli Freckles", value: 1 },
    { source: "micro beauty", target: "dark skin", value: 1 },
    { source: "olive skin", target: "pearl Skin", value: 2 },
  ],
};

export default function BrandBuzz() {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const width = 600;
    const height = 500;

    svg.attr("viewBox", [0, 0, width, height]);

    const customGradient = d3.scaleLinear<string>()
      .domain([0, 0.5, 1])
      .range(["#a18cd1", "#fbc2eb", "#84fab0"]); // purple → pink → blue

    const linkScale = d3
      .scaleLinear()
      .domain([1, d3.max(data.links, (d) => d.value) || 1])
      .range([0.5, 3]);

    const nodeRadiusScale = d3
      .scaleSqrt()
      .domain([1, d3.max(data.nodes, (d) => d.weight) || 1])
      .range([5, 20]);

    const simulation = d3
      .forceSimulation<GraphNode>(data.nodes)
      .force(
        "link",
        d3
          .forceLink<GraphNode, GraphLink>(data.links)
          .id((d) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#ffffffcc")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-linecap", "round")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke-width", (d) => linkScale(d.value));

    const nodeGroup = svg.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5);
    const nodes = nodeGroup
      .selectAll<SVGCircleElement, GraphNode>("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", (d) => nodeRadiusScale(d.weight))
      .attr("fill", (d) => {
        const xNorm = d.x !== undefined ? d.x / width : 0.5;
        const yNorm = d.y !== undefined ? d.y / height : 0.5;
        return customGradient((xNorm + yNorm) / 2);
      });

    nodes.call(
      d3
        .drag<SVGCircleElement, GraphNode>()
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
    );

    const label = svg
      .append("g")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text((d) => d.id)
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .attr("font-family", "sans-serif")
      .attr("fill", "white")
      .attr("text-anchor", "middle")
      .attr("dy", "2.5em");

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as GraphNode).x!)
        .attr("y1", (d) => (d.source as GraphNode).y!)
        .attr("x2", (d) => (d.target as GraphNode).x!)
        .attr("y2", (d) => (d.target as GraphNode).y!);

      nodes
        .attr("cx", (d) => d.x!)
        .attr("cy", (d) => d.y!)
        .attr("fill", (d) => {
          const xNorm = d.x! / width;
          const yNorm = d.y! / height;
          return customGradient((xNorm + yNorm) / 2);
        });

      label.attr("x", (d) => d.x!).attr("y", (d) => d.y!);
    });
  }, []);

  return (
    <div
      className="w-screen h-screen bg-cover bg-center"
      style={{ backgroundImage: 'url("/bg_img.jpg")' }}
    >
      <h1 className="text-2xl font-bold mb-2 text-white p-4">Brand Buzz</h1>
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}