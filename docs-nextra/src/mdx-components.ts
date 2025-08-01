import { useMDXComponents as getDocsMDXComponents } from "nextra-theme-docs";
import Mermaid from "./components/Mermaid";

const docsComponents = getDocsMDXComponents();

export const useMDXComponents: typeof getDocsMDXComponents = (components) => ({
  ...docsComponents,
  ...components,
  Mermaid,
});
