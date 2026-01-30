import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bedrock AI Agent",
  description: "AI Document Assistant powered by AWS Bedrock",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
