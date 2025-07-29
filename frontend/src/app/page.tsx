"use client";

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { BaseType } from "d3";

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  weight: number;
  sentiment?: string;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number;
}

const data: { nodes: GraphNode[]; links: GraphLink[] } = {
  nodes: [
    {
      "id": "cerave not cruelty-free",
      "weight": 6,
      "sentiment": "negative"
    },
    {
      "id": "cerave tested on animals",
      "weight": 6,
      "sentiment": "neutral"
    },
    {
      "id": "water-based cleanser",
      "weight": 4,
      "sentiment": "neutral"
    },
    {
      "id": "cleanser not a soap",
      "weight": 6,
      "sentiment": "neutral"
    },
    {
      "id": "break out on oily skin",
      "weight": 2,
      "sentiment": "negative"
    },
    {
      "id": "not designed for makeup removal",
      "weight": 2,
      "sentiment": "positive"
    },
    {
      "id": "foam only with water",
      "weight": 11,
      "sentiment": "neutral"
    },
    {
      "id": "foams up when used correctly",
      "weight": 10,
      "sentiment": "neutral"
    },
    {
      "id": "not suitable for tinted products",
      "weight": 1,
      "sentiment": "neutral"
    },
    {
      "id": "not available in the us",
      "weight": 3,
      "sentiment": "neutral"
    },
    {
      "id": "needs to be used with water",
      "weight": 1,
      "sentiment": "negative"
    },
    {
      "id": "must use with damp skin",
      "weight": 1,
      "sentiment": "neutral"
    },
    {
      "id": "must emulsify in hands",
      "weight": 1,
      "sentiment": "neutral"
    }
  ],
  links: [
    {
      "source": "cerave not cruelty-free",
      "target": "cerave tested on animals",
      "value": 4
    },
    {
      "source": "cleanser not a soap",
      "target": "water-based cleanser",
      "value": 3
    },
    {
      "source": "foam only with water",
      "target": "foams up when used correctly",
      "value": 9
    },
    {
      "source": "foam only with water",
      "target": "must use with damp skin",
      "value": 1
    },
    {
      "source": "cleanser not a soap",
      "target": "foam only with water",
      "value": 1
    },
    {
      "source": "foam only with water",
      "target": "water-based cleanser",
      "value": 1
    },
    {
      "source": "cerave not cruelty-free",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "cerave not cruelty-free",
      "target": "not designed for makeup removal",
      "value": 0.5
    },
    {
      "source": "cerave not cruelty-free",
      "target": "cleanser not a soap",
      "value": 0.5
    },
    {
      "source": "cerave tested on animals",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "cerave tested on animals",
      "target": "water-based cleanser",
      "value": 0.5
    },
    {
      "source": "cerave tested on animals",
      "target": "needs to be used with water",
      "value": 0.5
    },
    {
      "source": "water-based cleanser",
      "target": "needs to be used with water",
      "value": 0.5
    },
    {
      "source": "cleanser not a soap",
      "target": "not designed for makeup removal",
      "value": 0.5
    },
    {
      "source": "break out on oily skin",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "break out on oily skin",
      "target": "not designed for makeup removal",
      "value": 0.5
    },
    {
      "source": "break out on oily skin",
      "target": "cleanser not a soap",
      "value": 0.5
    },
    {
      "source": "break out on oily skin",
      "target": "must emulsify in hands",
      "value": 0.5
    },
    {
      "source": "not designed for makeup removal",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "foams up when used correctly",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "foams up when used correctly",
      "target": "break out on oily skin",
      "value": 0.5
    },
    {
      "source": "foams up when used correctly",
      "target": "must emulsify in hands",
      "value": 0.5
    },
    {
      "source": "not suitable for tinted products",
      "target": "not designed for makeup removal",
      "value": 0.5
    },
    {
      "source": "not suitable for tinted products",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "not suitable for tinted products",
      "target": "needs to be used with water",
      "value": 0.5
    },
    {
      "source": "not suitable for tinted products",
      "target": "foam only with water",
      "value": 0.5
    },
    {
      "source": "not available in the us",
      "target": "cerave not cruelty-free",
      "value": 0.5
    },
    {
      "source": "not available in the us",
      "target": "needs to be used with water",
      "value": 0.5
    },
    {
      "source": "not available in the us",
      "target": "not designed for makeup removal",
      "value": 0.5
    },
    {
      "source": "not available in the us",
      "target": "not suitable for tinted products",
      "value": 0.5
    },
    {
      "source": "must emulsify in hands",
      "target": "must use with damp skin",
      "value": 0.5
    },
    {
      "source": "must emulsify in hands",
      "target": "cleanser not a soap",
      "value": 0.5
    }
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

    const container = svg.append("g");

    d3.select(svgRef.current as SVGSVGElement).call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 5])
        .on("zoom", (event) => {
          container.attr("transform", event.transform.toString());
        })
    );

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

    const link = container
      .append("g")
      .attr("stroke", "#ffffffcc")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-linecap", "round")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke-width", (d) => linkScale(d.value));

    const tooltip = d3.select("body")
      .append("div")
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
    )
    .on("mouseover", (event, d) => {
      tooltip
        .style("opacity", 1)
        .style("left", `${event.pageX + 10}px`)
        .style("top", `${event.pageY + 10}px`)
        .html(`
          <strong>${d.id}</strong><br/>
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
    });

    const label = container
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