import "./globals.css";
import ErrorBoundary from "@/components/ErrorBoundary";

export const metadata = {
  title: "Vox - 内容生成 Agent",
  description: "多平台营销内容一键生成工具",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <ErrorBoundary>{children}</ErrorBoundary>
      </body>
    </html>
  );
}
