import React from 'react';

function getTierColor(tier) {
  if (tier >= 80) return 'from-red-500 to-orange-500';
  if (tier >= 60) return 'from-purple-500 to-pink-500';
  if (tier >= 40) return 'from-neon-blue to-cyan-400';
  if (tier >= 20) return 'from-neon-yellow to-orange-400';
  if (tier >= 10) return 'from-green-400 to-emerald-500';
  return 'from-gray-400 to-gray-500';
}

function getTierBorderColor(tier) {
  if (tier >= 80) return 'border-red-500';
  if (tier >= 60) return 'border-purple-500';
  if (tier >= 40) return 'border-cyan-400';
  if (tier >= 20) return 'border-neon-yellow';
  if (tier >= 10) return 'border-green-400';
  return 'border-gray-500';
}

export function TieredAvatar({ src, alt, tier = 1, size = 'md', className = '' }) {
  const sizes = {
    sm: { img: 'w-8 h-8', badge: 'w-5 h-5 text-[9px] -bottom-1 -right-1' },
    md: { img: 'w-12 h-12', badge: 'w-6 h-6 text-[10px] -bottom-1 -right-1' },
    lg: { img: 'w-16 h-16', badge: 'w-7 h-7 text-xs -bottom-1 -right-1' },
    xl: { img: 'w-24 h-24', badge: 'w-8 h-8 text-sm -bottom-1 -right-1' },
  };
  const s = sizes[size] || sizes.md;
  const borderColor = getTierBorderColor(tier);
  const gradColor = getTierColor(tier);

  return (
    <div className={`relative inline-block ${className}`} data-testid="tiered-avatar">
      <img
        src={src}
        alt={alt || ''}
        className={`${s.img} rounded-full border-2 ${borderColor} object-cover`}
      />
      <div
        className={`absolute ${s.badge} bg-gradient-to-br ${gradColor} rounded-full flex items-center justify-center font-black text-white shadow-lg border border-black/30`}
        data-testid="tier-badge"
      >
        {tier}
      </div>
    </div>
  );
}
