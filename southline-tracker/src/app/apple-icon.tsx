import { ImageResponse } from "next/og";

// iPhone home-screen icon (generated at build time): white "S" on black.
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#0a0a0a", color: "white", fontSize: 112, fontWeight: 700 }}>
        S
      </div>
    ),
    size,
  );
}
