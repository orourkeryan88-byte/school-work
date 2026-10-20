import { ImageResponse } from "next/og";

// iPhone home-screen icon (generated at build time): the Southline wave mark.
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", background: "#0b1f3a" }}>
        <svg viewBox="0 0 32 32" width="100%" height="100%">
          <path d="M7 19.5c3-6 6-6 9 0s6 6 9 0" fill="none" stroke="#2dd4bf" strokeWidth="2.6" strokeLinecap="round" />
          <path d="M7 12.5h18" stroke="white" strokeWidth="2.6" strokeLinecap="round" />
        </svg>
      </div>
    ),
    size,
  );
}
