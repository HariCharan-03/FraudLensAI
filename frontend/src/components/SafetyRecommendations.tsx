import { ShieldCheck } from 'lucide-react';

interface SafetyRecommendationsProps {
  recommendations?: string[];
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'INCONCLUSIVE';
}

export const SafetyRecommendations: React.FC<SafetyRecommendationsProps> = ({
  recommendations = [],
  riskLevel,
}) => {
  if (!recommendations || recommendations.length === 0) return null;

  const isHigh = riskLevel === 'HIGH';

  return (
    <div className={`cyber-card rounded-xl p-5 border ${isHigh ? 'border-rose-900/50 bg-rose-950/10' : 'border-slate-800'}`}>
      <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-3 flex items-center gap-2">
        <ShieldCheck className={`w-4 h-4 ${isHigh ? 'text-rose-400' : 'text-cyan-400'}`} />
        Recommended Incident & Safety Actions
      </h3>

      <div className="space-y-2.5">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-200">
            <span
              className={`flex items-center justify-center w-5 h-5 rounded-full shrink-0 font-bold text-[10px] mt-0.5 ${
                isHigh ? 'bg-rose-900/60 text-rose-300' : 'bg-cyan-900/60 text-cyan-300'
              }`}
            >
              {idx + 1}
            </span>
            <span className="leading-relaxed">{rec}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
