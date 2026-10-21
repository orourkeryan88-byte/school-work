import { ImageResponse } from "next/og";
import { MARK } from "@/lib/brand-mark";

// iPhone home-screen icon (generated at build time): the Southline "SA" monogram.
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", background: "#ffffff" }}>
        <svg viewBox="-6 -6 112 112" width="100%" height="100%">
          <path d={MARK.s} fill={MARK.navy} />
          <path d={MARK.a} fill={MARK.navy} />
          <path d={MARK.swoosh} fill={MARK.gold} />
        </svg>
      </div>
    ),
    size,
  );
}
