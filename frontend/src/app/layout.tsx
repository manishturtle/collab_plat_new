import type { Metadata } from "next";
import ThemeRegistry from "@/components/ThemeRegistry"; // Adjust path if needed

export const metadata: Metadata = {
  title: "My App",
  description: "My awesome application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <ThemeRegistry>
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}