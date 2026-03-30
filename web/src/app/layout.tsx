import type { Metadata } from "next";
import Script from "next/script";
import { Nunito, Quicksand } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { SessionProvider } from "@/components/providers/SessionProvider";

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const quicksand = Quicksand({
  variable: "--font-quicksand",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "TheStoryMama - Magical Bedtime Stories for Children",
    template: "%s | TheStoryMama",
  },
  description:
    "Beautiful bedtime stories made with love for your little one. Browse free illustrated stories or create personalized storybooks.",
  keywords: [
    "bedtime stories",
    "children stories",
    "toddler stories",
    "personalized storybook",
    "kids bedtime",
    "free bedtime stories",
    "illustrated stories for kids",
  ],
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    siteName: "TheStoryMama",
    type: "website",
    images: [{ url: "/og-logo.png", width: 512, height: 512 }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${nunito.variable} ${quicksand.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-[family-name:var(--font-nunito)]">
        <Script
          defer
          src="https://analytics.thestorymama.club/script.js"
          data-website-id="e92ce353-17aa-40f5-8d9a-06286d9e08f3"
          strategy="afterInteractive"
        />
        <SessionProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </SessionProvider>
      </body>
    </html>
  );
}
