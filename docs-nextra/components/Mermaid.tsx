import React, { useEffect, useRef } from "react";
import mermaid from "mermaid";

interface MermaidProps {
  children: string;
}

let mermaidId = 0;

const Mermaid: React.FC<MermaidProps> = ({ children }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [id] = React.useState(() => `mermaid-${mermaidId++}`);

  useEffect(() => {
    if (ref.current) {
      mermaid.initialize({
        startOnLoad: true,
        theme: "default",
        themeVariables: {
          primaryColor: "#4285f4",
          primaryTextColor: "#202124",
          primaryBorderColor: "#1a73e8",
          lineColor: "#5f6368",
          secondaryColor: "#34a853",
          tertiaryColor: "#fbbc04",
          background: "#ffffff",
          mainBkg: "#4285f4",
          secondBkg: "#34a853",
          tertiaryBkg: "#fbbc04",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        },
        flowchart: {
          htmlLabels: true,
          curve: "basis",
        },
        securityLevel: "loose",
      });

      try {
        mermaid.render(id, children, (svgCode) => {
          if (ref.current) {
            ref.current.innerHTML = svgCode;
          }
        });
      } catch (error) {
        console.error("Mermaid rendering error:", error);
        if (ref.current) {
          ref.current.innerHTML =
            '<p style="color: red;">Error rendering diagram</p>';
        }
      }
    }
  }, [children, id]);

  return (
    <div className="my-6 overflow-x-auto">
      <div ref={ref} className="mermaid flex justify-center" />
    </div>
  );
};

export default Mermaid;
