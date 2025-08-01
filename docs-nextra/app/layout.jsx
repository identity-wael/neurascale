import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { Banner, Head } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";

export const metadata = {
  title: {
    default: "NeuraScale Documentation",
    template: "%s | NeuraScale Docs",
  },
  description:
    "Official documentation for NeuraScale - AI-powered infrastructure platform",
};

export default async function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <Head faviconGlyph="🧠" />
      <body>
        <Layout
          navbar={
            <Navbar
              logo={
                <span style={{ fontWeight: "bold" }}>
                  NeuraScale Documentation
                </span>
              }
              projectLink="https://github.com/identity-wael/neurascale"
              chatLink="https://github.com/identity-wael/neurascale/discussions"
            />
          }
          pageMap={await getPageMap()}
          docsRepositoryBase="https://github.com/identity-wael/neurascale/tree/main/docs-nextra"
          sidebar={{
            defaultMenuCollapseLevel: 1,
            autoCollapse: true,
            toggleButton: true,
          }}
          toc={{
            title: "On This Page",
            backToTop: true,
          }}
          editLink={{ text: "Edit this page on GitHub →" }}
          feedback={{
            content: "Question? Give us feedback →",
            labels: "feedback",
          }}
          search={{ placeholder: "Search documentation..." }}
          footer={
            <Footer>
              <div style={{ textAlign: "center" }}>
                © 2025 NeuraScale. Built with ❤️ and 🧠
              </div>
            </Footer>
          }
          banner={
            <Banner dismissible key="nextra-migration">
              🎉 Welcome to our new documentation site! Report any issues →
            </Banner>
          }
        >
          {children}
        </Layout>
      </body>
    </html>
  );
}
