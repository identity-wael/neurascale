import React from "react";
import { useRouter } from "next/router";

const config = {
  logo: <span style={{ fontWeight: "bold" }}>NeuraScale Documentation</span>,
  project: {
    link: "https://github.com/identity-wael/neurascale",
  },
  chat: {
    link: "https://github.com/identity-wael/neurascale/discussions",
  },
  docsRepositoryBase:
    "https://github.com/identity-wael/neurascale/tree/main/docs-nextra",
  footer: {
    text: "© 2025 NeuraScale. Built with ❤️ and 🧠",
  },
  navigation: {
    prev: true,
    next: true,
  },
  sidebar: {
    titleComponent({ title, type }) {
      if (type === "separator") {
        return <span className="cursor-default">{title}</span>;
      }
      return <>{title}</>;
    },
    defaultMenuCollapseLevel: 1,
    toggleButton: true,
  },
  toc: {
    backToTop: true,
  },
  darkMode: true,
  search: {
    placeholder: "Search documentation...",
  },
  editLink: {
    text: "Edit this page on GitHub →",
  },
  feedback: {
    content: "Question? Give us feedback →",
    labels: "feedback",
  },
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="NeuraScale Documentation" />
      <meta
        property="og:description"
        content="Comprehensive documentation for NeuraScale - Open-source neuromorphic computing platform"
      />
      <link rel="icon" href="/favicon.ico" />
    </>
  ),
  useNextSeoProps() {
    const { asPath } = useRouter();
    if (asPath !== "/") {
      return {
        titleTemplate: "%s – NeuraScale Docs",
      };
    }
  },
  banner: {
    key: "nextra-migration",
    text: (
      <a href="https://github.com/identity-wael/neurascale" target="_blank">
        🎉 Welcome to our new documentation site! Report any issues →
      </a>
    ),
  },
};

export default config;
