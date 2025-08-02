/* eslint-env node */
import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { Banner, Head } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";

export const metadata = {
  metadataBase: new URL("https://docs.neurascale.io"),
  title: {
    template: "%s - NeuraScale Documentation",
  },
  description: "NeuraScale: Open Brain-Computer Interface Platform",
  applicationName: "NeuraScale",
  generator: "Next.js",
  appleWebApp: {
    title: "NeuraScale Docs",
  },
  other: {
    "msapplication-TileImage": "/ms-icon-144x144.png",
    "msapplication-TileColor": "#fff",
  },
  twitter: {
    site: "https://neurascale.io",
  },
};

export default async function RootLayout({ children }) {
  const navbar = (
    <Navbar
      logo={
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <span
            style={{
              fontSize: "20px",
              fontWeight: "800",
              letterSpacing: "0.05em",
              fontFamily:
                "Proxima Nova, -apple-system, BlinkMacSystemFont, sans-serif",
            }}
          >
            <span style={{ color: "#eeeeee" }}>NEURA</span>
            <span style={{ color: "#4185f4" }}>SCALE</span>
          </span>
          <div
            style={{
              width: "1px",
              height: "24px",
              backgroundColor: "rgba(255,255,255,0.2)",
            }}
          />
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <svg
              style={{ height: "24px", width: "auto" }}
              viewBox="0 0 536.229 536.229"
              fill="white"
              fillOpacity="0.8"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g>
                <g>
                  <rect y="130.031" width="58.206" height="276.168" />
                  <rect
                    x="95.356"
                    y="130.031"
                    width="58.206"
                    height="190.712"
                  />
                  <rect
                    x="190.712"
                    y="130.031"
                    width="58.206"
                    height="276.168"
                  />
                  <rect
                    x="381.425"
                    y="217.956"
                    width="58.212"
                    height="188.236"
                  />
                  <rect
                    x="381.425"
                    y="130.031"
                    width="154.805"
                    height="58.206"
                  />
                  <rect x="286.074" y="217.956" width="58.2" height="188.236" />
                  <rect x="286.074" y="130.031" width="58.2" height="58.206" />
                </g>
              </g>
            </svg>
            <span
              style={{
                fontSize: "14px",
                color: "rgba(255,255,255,0.7)",
                fontFamily:
                  "Neue Haas Grotesk Medium, -apple-system, BlinkMacSystemFont, sans-serif",
                fontWeight: 500,
              }}
            >
              Massachusetts Institute of Technology
            </span>
          </div>
        </div>
      }
    />
  );
  const pageMap = await getPageMap();
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head faviconGlyph="✦" />
      <body>
        <Layout
          navbar={navbar}
          footer={
            <Footer>
              MIT {new Date().getFullYear()} © NeuraScale. All rights reserved.
            </Footer>
          }
          editLink="Edit this page on GitHub"
          docsRepositoryBase="https://github.com/identity-wael/neurascale/blob/main/docs-nextra"
          sidebar={{ defaultMenuCollapseLevel: 1 }}
          pageMap={pageMap}
          darkMode={true}
          nextThemes={{
            defaultTheme: "dark",
            forcedTheme: "dark",
          }}
        >
          {children}
        </Layout>
      </body>
    </html>
  );
}
