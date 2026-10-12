import React from 'react';
import type { FeatureExplanation } from '../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { Cpu, Info } from 'lucide-react';

interface FeatureImportanceChartProps {
  explanations?: FeatureExplanation[];
  modelType?: string;
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({
  explanations = [],
  modelType = 'RandomForest',
}) => {
  if (!explanations || explanations.length === 0) {
    return (
      <div className="cyber-card rounded-xl p-5 border border-slate-800">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-3 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" /> Explainable AI (SHAP)
        </h3>
        <p className="text-sm text-slate-500">Feature importance data is unavailable for this scan.</p>
      </div>
    );
  }

  // Format data for chart
  const chartData = explanations.map((item) => ({
    name: item.display_name.length > 20 ? item.display_name.slice(0, 18) + '...' : item.display_name,
    fullName: item.display_name,
    shap_impact: item.shap_impact,
    value: item.feature_value,
    direction: item.direction,
    description: item.description,
    summary: item.summary_text,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isRisk = data.shap_impact > 0;
      return (
        <div className="bg-slate-900/95 border border-slate-700 p-3 rounded-lg shadow-xl text-xs max-w-xs backdrop-blur-md">
          <p className="font-bold text-white mb-1">{data.fullName}</p>
          <p className="text-slate-400 mb-2">{data.description}</p>
          <div className="flex items-center justify-between border-t border-slate-800 pt-2 mb-1">
            <span className="text-slate-400">Observed Value:</span>
            <span className="font-mono text-cyan-300 font-semibold">{data.value}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">SHAP Impact:</span>
            <span className={`font-mono font-bold ${isRisk ? 'text-rose-400' : 'text-emerald-400'}`}>
              {data.shap_impact > 0 ? `+${data.shap_impact}` : data.shap_impact}
            </span>
          </div>
          <p className="text-[11px] text-slate-300 mt-2 bg-slate-800/60 p-1.5 rounded">
            {data.summary}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="cyber-card rounded-xl p-5 border border-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
        <div>
          <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" /> Explainable AI — Feature Attributions
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            TreeSHAP attributions for {modelType} model (positive raises phishing probability)
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-500 inline-block" /> Increases Risk
          </span>
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block" /> Lowers Risk
          </span>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <XAxis
              type="number"
              domain={['dataMin - 0.05', 'dataMax + 0.05']}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickLine={{ stroke: '#334155' }}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              width={110}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={0} stroke="#475569" strokeDasharray="3 3" />
            <Bar dataKey="shap_impact" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.shap_impact > 0 ? '#ef4444' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800 flex items-start gap-2 text-xs text-slate-500">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <span>
          SHAP values explain mathematical feature contributions relative to base dataset expectation.
          They explain model behavior without implying causation or absolute intent.
        </span>
      </div>
    </div>
  );
};
