import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { AuthProvider } from "@/components/AuthProvider";
import { ProgressProvider } from "@/components/ProgressProvider";
import GamificationProvider from "@/components/GamificationProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Learn AI With Grey8",
  description:
    "A self-driving AI tutor and bootcamp. Master AI/ML through hands-on projects with personalized guidance.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans`}>
        <AuthProvider>
          <ProgressProvider>
            <GamificationProvider>
              <div className="flex min-h-screen">
                <Navigation />
                <main className="flex-1 overflow-auto">
                  <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                    {children}
                  </div>
                </main>
              </div>
            </GamificationProvider>
          </ProgressProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
