import { generateStaticParamsFor, importPage } from "nextra/pages";
import { useMDXComponents } from "../../../mdx-components";

export const generateStaticParams = generateStaticParamsFor("mdxPath");

export async function generateMetadata(props) {
  const params = await props.params;
  const pathname = "/" + (params.mdxPath?.join("/") || "");
  return await importPage(pathname + ".mdx", params.mdxPath);
}

export default async function Page(props) {
  const params = await props.params;
  const pathname = "/" + (params.mdxPath?.join("/") || "");
  const result = await importPage(pathname + ".mdx", params.mdxPath);
  const { default: MDXContent, ...exported } = result;
  const components = useMDXComponents();

  return <MDXContent {...props} components={components} />;
}
