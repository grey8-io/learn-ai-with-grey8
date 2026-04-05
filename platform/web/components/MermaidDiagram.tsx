"use client";

import { useEffect, useRef, useState } from "react";

interface MermaidDiagramProps {
  chart: string;
}

let mermaidInitialized = false;

/*
 * Semantic color palette — colors assigned by WHAT the node represents,
 * not by position. Consistent across all diagrams in the curriculum.
 *
 * Standard:
 *   Blue    — user-facing / entry points (browser, client, user, input, CLI)
 *   Teal    — processing / middleware (API, server, FastAPI, handler, validate)
 *   Purple  — AI / LLM (Ollama, model, LLM, generate, predict, embeddings)
 *   Amber   — data / storage (DB, cache, vector store, ChromaDB, files, docs)
 *   Emerald — output / success (response, result, answer, deploy, complete)
 *   Rose    — control / decision (error, alert, check, if, retry, reject)
 */
interface NodeColor {
  fill: string;
  border: string;
  text: string;
}

const COLORS = {
  blue:    { fill: "#1e40af", border: "#60a5fa", text: "#f8fafc" } as NodeColor,
  teal:    { fill: "#0f766e", border: "#2dd4bf", text: "#f8fafc" } as NodeColor,
  purple:  { fill: "#6d28d9", border: "#a78bfa", text: "#f8fafc" } as NodeColor,
  amber:   { fill: "#b45309", border: "#fbbf24", text: "#f8fafc" } as NodeColor,
  emerald: { fill: "#047857", border: "#34d399", text: "#f8fafc" } as NodeColor,
  rose:    { fill: "#be123c", border: "#fb7185", text: "#f8fafc" } as NodeColor,
};

// Fallback cycle for nodes that don't match any keyword
const FALLBACK_CYCLE = [COLORS.blue, COLORS.teal, COLORS.purple, COLORS.amber, COLORS.emerald, COLORS.rose];

// Keywords mapped to semantic categories (checked against lowercase node label)
const SEMANTIC_RULES: [RegExp, NodeColor][] = [
  // User-facing / entry (blue)
  [/\b(user|client|browser|input|cli|terminal|request|prompt|query|question|upload)\b/, COLORS.blue],
  // Processing / middleware (teal)
  [/\b(api|server|fastapi|flask|handler|middleware|validate|process|route|nginx|proxy|sanitize|normalize|parse|tutor|backend)\b/, COLORS.teal],
  // AI / LLM (purple)
  [/\b(ollama|llm|model|ai|generate|predict|embed|attention|token|train|inference|agent|think|gpt|llama|llava|mermaid|transformer|neural)\b/, COLORS.purple],
  // Data / storage (amber)
  [/\b(db|database|store|storage|cache|vector|chroma|file|doc|data|index|chunk|memory|queue|volume|save|persist|postgres|supabase)\b/, COLORS.amber],
  // Output / success (emerald)
  [/\b(response|result|answer|output|return|deploy|complete|success|display|render|show|done|finish)\b/, COLORS.emerald],
  // Control / decision (rose)
  [/\b(error|alert|check|fail|reject|retry|limit|rate|monitor|warn|exception|timeout|fallback|miss)\b/, COLORS.rose],
];

/** Determine color for a node based on its text content. */
function getNodeColor(label: string, index: number): NodeColor {
  const lower = label.toLowerCase();
  for (const [pattern, color] of SEMANTIC_RULES) {
    if (pattern.test(lower)) return color;
  }
  // Fallback: cycle through palette for unmatched nodes
  return FALLBACK_CYCLE[index % FALLBACK_CYCLE.length];
}

/** Inject per-node colors into the rendered SVG so each node is visually distinct. */
function colorizeNodes(svgHtml: string): string {
  // Parse as text/html to handle HTML tags inside foreignObject (like <br>)
  const parser = new DOMParser();
  const htmlDoc = parser.parseFromString(
    `<body>${svgHtml}</body>`,
    "text/html"
  );
  const doc = htmlDoc.body;
  const nodes = doc.querySelectorAll(".node");

  nodes.forEach((node, i) => {
    // Extract all text from the node to determine its semantic category
    const label = node.textContent || "";
    const color = getNodeColor(label, i);

    // Color the shape (rect, polygon, circle, path inside .label-container or directly)
    const shapes = node.querySelectorAll(
      "rect, polygon, circle, .label-container rect"
    );
    shapes.forEach((shape) => {
      (shape as SVGElement).style.fill = color.fill;
      (shape as SVGElement).style.stroke = color.border;
      (shape as SVGElement).style.strokeWidth = "2px";
    });

    // Color the text
    const texts = node.querySelectorAll("span, text, .nodeLabel, foreignObject span");
    texts.forEach((t) => {
      (t as HTMLElement).style.color = color.text;
      (t as SVGElement).style.fill = color.text;
    });
  });

  // Style subgraph clusters — subtle bordered containers
  const clusters = doc.querySelectorAll(".cluster rect");
  clusters.forEach((rect) => {
    (rect as SVGElement).style.fill = "#0f172a";
    (rect as SVGElement).style.stroke = "#475569";
    (rect as SVGElement).style.strokeWidth = "1.5px";
    (rect as SVGElement).style.rx = "8";
  });

  // Style cluster labels
  const clusterLabels = doc.querySelectorAll(".cluster text, .cluster span");
  clusterLabels.forEach((label) => {
    (label as HTMLElement).style.color = "#94a3b8";
    (label as SVGElement).style.fill = "#94a3b8";
    (label as HTMLElement).style.fontWeight = "600";
  });

  // Style edge lines — lighter, visible
  const edges = doc.querySelectorAll(".edge-pattern-solid, .flowchart-link");
  edges.forEach((edge) => {
    (edge as SVGElement).style.stroke = "#64748b";
    (edge as SVGElement).style.strokeWidth = "2px";
  });

  // Style edge arrowheads
  const markers = doc.querySelectorAll("marker path");
  markers.forEach((m) => {
    (m as SVGElement).style.fill = "#64748b";
    (m as SVGElement).style.stroke = "#64748b";
  });

  // Style edge labels
  const edgeLabels = doc.querySelectorAll(".edgeLabel span, .edgeLabel text, .edge-label span");
  edgeLabels.forEach((label) => {
    (label as HTMLElement).style.color = "#cbd5e1";
    (label as SVGElement).style.fill = "#cbd5e1";
    (label as HTMLElement).style.fontSize = "12px";
  });
  const edgeLabelBgs = doc.querySelectorAll(".edgeLabel rect, .edge-label rect");
  edgeLabelBgs.forEach((bg) => {
    (bg as SVGElement).style.fill = "#1e293b";
    (bg as SVGElement).style.stroke = "none";
    (bg as SVGElement).style.rx = "4";
  });

  // Extract the SVG element back as HTML string
  const svgEl = doc.querySelector("svg");
  return svgEl ? svgEl.outerHTML : svgHtml;
}

export default function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      try {
        const mermaid = (await import("mermaid")).default;

        if (!mermaidInitialized) {
          mermaid.initialize({
            startOnLoad: false,
            theme: "dark",
            themeVariables: {
              fontFamily: "ui-sans-serif, system-ui, sans-serif",
              fontSize: "14px",
              lineColor: "#64748b",
              textColor: "#e2e8f0",
            },
            flowchart: {
              htmlLabels: true,
              curve: "basis",
              padding: 16,
            },
            sequence: {
              diagramMarginX: 16,
              diagramMarginY: 16,
              actorMargin: 60,
              messageMargin: 40,
            },
          });
          mermaidInitialized = true;
        }

        const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
        const { svg: renderedSvg } = await mermaid.render(id, chart.trim());

        if (!cancelled) {
          setSvg(colorizeNodes(renderedSvg));
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to render diagram");
        }
      }
    }

    render();
    return () => {
      cancelled = true;
    };
  }, [chart]);

  if (error) {
    return (
      <pre className="rounded-xl bg-slate-900/80 border border-slate-700/50 p-4 my-4 overflow-x-auto text-sm leading-6">
        <code className="text-slate-400">{chart}</code>
      </pre>
    );
  }

  if (!svg) {
    return (
      <div className="flex items-center justify-center rounded-xl bg-slate-900/80 border border-slate-700/50 p-8 my-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="my-4 overflow-x-auto rounded-xl bg-slate-950/60 border border-slate-700/50 p-6 flex justify-center [&_svg]:max-w-full"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
