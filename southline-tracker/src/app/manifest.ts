import type { MetadataRoute } from "next";

// Makes the app installable on a phone ("Add to Home Screen"): opens
// full-screen with its own icon, like a native app.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Southline Agency",
    short_name: "Southline",
    description: "Every cold email and SMS sent, every reply, and what happened next.",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#0b1f3a",
    icons: [
      { src: "/icon", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/apple-icon", sizes: "180x180", type: "image/png" },
    ],
  };
}
