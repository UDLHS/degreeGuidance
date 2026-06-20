import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Degree Guidance — find your matches",
  description: "Sri Lankan A/L university degree guidance, based on your Z-score, district and stream.",
};

// Fonts/background scoped to this route group only (the (panel) admin layout
// is untouched). A plain <link> rather than next/font/google: this dev
// environment's build-time font-fetcher fails to reach fonts.googleapis.com
// even though curl/Node fetch to the same URL succeed (a WSL2-specific
// next/font quirk) -- a runtime <link>, same as a normal static page, sidesteps
// it entirely and is what the original design called for.
export default function StudentLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        // @ts-expect-error -- CSS custom properties
        "--font-hanken": "'Hanken Grotesk', system-ui, sans-serif",
        "--font-newsreader": "'Newsreader', serif",
        fontFamily: "var(--font-hanken)",
        background: "#f3f6fb",
        minHeight: "100vh",
      }}
    >
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      <link
        href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap"
        rel="stylesheet"
      />
      {children}
    </div>
  );
}
