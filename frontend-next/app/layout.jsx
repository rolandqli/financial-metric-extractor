import "./globals.css";

export const metadata = {
  title: "Earnings PDF Extractor",
  description: "Upload earnings PDFs and export key metrics to Excel",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
