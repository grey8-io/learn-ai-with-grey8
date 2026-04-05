"use client";

import { isValidElement, Children } from "react";
import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

const MermaidDiagram = dynamic(() => import("./MermaidDiagram"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center rounded-xl bg-slate-900/80 border border-slate-700/50 p-8 my-4">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
    </div>
  ),
});

/** Extract plain text from React children (handles nested elements). */
function extractText(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (isValidElement(node)) return extractText(node.props.children);
  if (Array.isArray(node)) return node.map(extractText).join("");
  return "";
}

interface MarkdownRendererProps {
  content: string;
}

const components: Components = {
  h1: ({ children }) => (
    <h1 className="text-3xl font-bold text-slate-100 mb-6 mt-2">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xl font-semibold text-slate-100 mt-8 mb-4 pb-2 border-b border-slate-700/50">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-lg font-medium text-slate-200 mt-6 mb-3">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-slate-300 leading-7 mb-4">{children}</p>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      className="text-primary-400 hover:text-primary-300 underline underline-offset-2 transition-colors"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  ul: ({ children }) => (
    <ul className="list-disc list-inside space-y-1.5 text-slate-300 mb-4 ml-2">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-inside space-y-1.5 text-slate-300 mb-4 ml-2">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="text-slate-300">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-primary-500/50 bg-primary-600/5 px-4 py-3 my-4 text-slate-300 rounded-r-lg">
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }) => {
    const isInline = !className;
    if (isInline) {
      return (
        <code className="rounded bg-slate-700/70 px-1.5 py-0.5 text-sm text-primary-300 font-mono">
          {children}
        </code>
      );
    }
    const language = className?.replace("language-", "") || "";
    return (
      <code className={`text-sm font-mono ${className}`} {...props}>
        {children}
      </code>
    );
  },
  pre: ({ children }) => {
    // Detect mermaid code blocks and render as diagrams
    const child = Array.isArray(children) ? children[0] : children;
    if (isValidElement(child)) {
      const props = child.props as Record<string, unknown>;
      const cls = String(props.className || "");
      if (cls.includes("language-mermaid")) {
        const chart = extractText(props.children as React.ReactNode);
        return <MermaidDiagram chart={chart} />;
      }
    }
    return (
      <pre className="rounded-xl bg-slate-900/80 border border-slate-700/50 p-4 my-4 overflow-x-auto text-sm leading-6">
        {children}
      </pre>
    );
  },
  hr: () => <hr className="my-8 border-slate-700/50" />,
  strong: ({ children }) => (
    <strong className="font-semibold text-slate-100">{children}</strong>
  ),
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-slate-700/50">
      <table className="w-full text-sm text-slate-300">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-slate-800/50 text-slate-200">{children}</thead>
  ),
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left font-medium">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border-t border-slate-700/50 px-4 py-2.5">{children}</td>
  ),
  img: ({ src, alt }) => (
    <img
      src={src}
      alt={alt || ""}
      className="my-4 max-w-full rounded-lg border border-slate-700/50"
      loading="lazy"
    />
  ),
};

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
}
