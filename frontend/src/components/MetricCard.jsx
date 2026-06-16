import React from 'react';

const MetricCard = ({ label, value, color = "text-text-primary" }) => (
  <div className="bg-bg-secondary p-5 rounded-lg border border-border-muted hover:border-gray-600 transition-all">
    <p className="text-text-secondary text-[10px] uppercase font-bold tracking-wider mb-1">{label}</p>
    <h3 className={`text-2xl font-mono font-bold ${color}`}>{value}</h3>
  </div>
);

export default MetricCard;