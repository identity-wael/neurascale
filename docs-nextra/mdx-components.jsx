import { useMDXComponents as getDocsMDXComponents } from "nextra-theme-docs";
import Mermaid from "./src/components/Mermaid";

const docsComponents = getDocsMDXComponents();

export function useMDXComponents(components) {
  return {
    ...docsComponents,
    ...components,
    Mermaid,
  };
}
