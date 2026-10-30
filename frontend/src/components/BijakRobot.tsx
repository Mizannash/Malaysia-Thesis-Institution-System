"use client";

export type BijakMood = "idle" | "talking" | "thinking";

interface BijakRobotProps {
  size?: number;
  mood?: BijakMood;
  animated?: boolean;
}

/** Prof. Bijak, the MTIS coach mascot. Pure SVG; animations live in globals.css (.bijak-*). */
export default function BijakRobot({ size = 52, mood = "idle", animated = true }: BijakRobotProps) {
  const classes = ["bijak", `bijak--${mood}`, animated ? "bijak--animated" : ""].join(" ");
  return (
    <svg className={classes} width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      {/* Antenna */}
      <line x1="32" y1="8" x2="32" y2="15" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" />
      <circle className="bijak-antenna" cx="32" cy="6.5" r="3.5" fill="var(--tertiary-accent)" />

      {/* Arms */}
      <line x1="22" y1="52" x2="14" y2="57" stroke="var(--primary)" strokeWidth="3.5" strokeLinecap="round" />
      <g className="bijak-arm">
        <line x1="42" y1="52" x2="50" y2="45" stroke="var(--primary)" strokeWidth="3.5" strokeLinecap="round" />
      </g>

      {/* Body */}
      <rect x="22" y="47" width="20" height="13" rx="6" fill="var(--primary)" />
      <circle cx="32" cy="53.5" r="2.2" fill="var(--tertiary-accent)" />

      {/* Head */}
      <rect x="9" y="14" width="46" height="35" rx="16" fill="var(--primary)" />
      <rect x="15" y="20" width="34" height="23" rx="11" fill="#e8f3fb" />

      {/* Eyes */}
      <g className="bijak-eyes">
        <circle cx="25" cy="30" r="4" fill="#0b1c30" />
        <circle cx="39" cy="30" r="4" fill="#0b1c30" />
        <g className="bijak-pupils">
          <circle cx="26.3" cy="28.6" r="1.4" fill="#ffffff" />
          <circle cx="40.3" cy="28.6" r="1.4" fill="#ffffff" />
        </g>
      </g>

      {/* Cheeks and smile */}
      <circle cx="20" cy="36" r="2" fill="#f9a8b8" opacity="0.8" />
      <circle cx="44" cy="36" r="2" fill="#f9a8b8" opacity="0.8" />
      <path d="M27 36.5 Q32 41 37 36.5" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
