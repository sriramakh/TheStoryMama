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
  metadataBase: new URL("https://www.thestorymama.club"),
  title: {
    default:
      "Free Bedtime Stories for Kids + Personalized Stories | TheStoryMama",
    template: "%s | TheStoryMama",
  },
  description:
    "Browse 100+ free illustrated bedtime stories or create a personalized story starring your child. Beautiful art styles, PDF download, loved by parents.",
  alternates: { canonical: "https://www.thestorymama.club" },
  keywords: [
    "bedtime stories",
    "free bedtime stories for kids",
    "personalized bedtime story",
    "custom story with child's name",
    "AI bedtime story for kids",
    "illustrated stories for children",
    "toddler bedtime stories",
    "kids picture books online",
  ],
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    title:
      "Free Bedtime Stories for Kids + Personalized Stories | TheStoryMama",
    description:
      "Browse 100+ free illustrated bedtime stories or create a personalized story starring your child.",
    siteName: "TheStoryMama",
    type: "website",
    url: "https://www.thestorymama.club",
    images: [{ url: "/og-logo.png", width: 512, height: 512 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "TheStoryMama — Free & Personalized Bedtime Stories for Kids",
    description:
      "100+ free illustrated bedtime stories + personalized stories starring your child.",
    images: ["/og-logo.png"],
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
