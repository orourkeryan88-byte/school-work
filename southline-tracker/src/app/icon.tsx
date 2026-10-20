import { ImageResponse } from "next/og";

// App icon (generated at build time): white "S" on black.
export const size = { width: 512, height: 512 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#0a0a0a", color: "white", fontSize: 320, fontWeight: 700 }}>
        S
      </div>
    ),
    size,
  );
}
