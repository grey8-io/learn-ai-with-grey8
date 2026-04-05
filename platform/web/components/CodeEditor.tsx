"use client";

import { useRef } from "react";
import Editor, { OnMount } from "@monaco-editor/react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  language?: string;
  readOnly?: boolean;
}

export default function CodeEditor({
  value,
  onChange,
  language = "python",
  readOnly = false,
}: CodeEditorProps) {
  const editorRef = useRef<any>(null);

  const handleMount: OnMount = (editor) => {
    editorRef.current = editor;
    editor.focus();
  };

  return (
    <Editor
      height="100%"
      language={language}
      value={value}
      onChange={onChange}
      onMount={handleMount}
      theme="vs-dark"
      options={{
        readOnly,
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Menlo, monospace",
        fontLigatures: true,
        minimap: { enabled: false },
        lineNumbers: "on",
        renderLineHighlight: "line",
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        insertSpaces: true,
        wordWrap: "on",
        padding: { top: 12, bottom: 12 },
        scrollbar: {
          verticalScrollbarSize: 8,
          horizontalScrollbarSize: 8,
        },
        suggest: {
          showKeywords: true,
          showSnippets: true,
        },
      }}
      loading={
        <div className="flex h-full items-center justify-center bg-[#1e1e1e]">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
        </div>
      }
    />
  );
}
