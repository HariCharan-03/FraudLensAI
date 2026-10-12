import React from 'react';

interface RiskGaugeProps {
  score: number; // 0 to 100
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'INCONCLUSIVE';
  size?: number;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, size = 180 }) => {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const safeScore = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  let strokeColor = '#10b981'; // emerald for low
  let glowColor = 'rgba(16, 185, 129, 0.4)';

  if (level === 'HIGH' || safeScore >= 75) {
    strokeColor = '#ef4444'; // rose/red
    glowColor = 'rgba(239, 68, 68, 0.5)';
  } else if (level === 'MEDIUM' || safeScore >= 45) {
    strokeColor = '#f59e0b'; // amber
    glowColor = 'rgba(245, 158, 11, 0.4)';
  } else if (level === 'INCONCLUSIVE') {
    strokeColor = '#64748b'; // slate
    glowColor = 'rgba(100, 116, 139, 0.3)';
  }

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Score Stroke */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 1s ease-in-out',
              filter: `drop-shadow(0 0 10px ${glowColor})`,
            }}
          />
        </svg>

        {/* Center Score Readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold tracking-tight text-white font-mono">
            {safeScore}
          </span>
          <span className="text-xs uppercase tracking-widest text-slate-400 font-semibold mt-0.5">
            / 100
          </span>
        </div>
      </div>

      <div className="mt-3">
        <span
          className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full border"
          style={{
            borderColor: strokeColor,
            color: strokeColor,
            backgroundColor: `${strokeColor}15`,
          }}
        >
          {level} RISK
        </span>
      </div>
    </div>
  );
};
