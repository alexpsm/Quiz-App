import React from 'react';

export const Score90Logo = ({ variant = 'color', className = '' }) => {
  const logos = {
    'color': 'https://customer-assets.emergentagent.com/job_8a65f18f-c58c-430e-be28-e5c1522836e7/artifacts/y7pam3jf_score-90-color-on-white.png',
    'white': 'https://customer-assets.emergentagent.com/job_8a65f18f-c58c-430e-be28-e5c1522836e7/artifacts/aecrm067_s90-white.png',
    'icon': 'https://customer-assets.emergentagent.com/job_8a65f18f-c58c-430e-be28-e5c1522836e7/artifacts/qj253bxk_icon-color.png',
  };

  return (
    <img
      src={logos[variant]}
      alt="Score90"
      className={className}
      loading="lazy"
    />
  );
};

export const PoweredByScore90 = ({ size = 'sm', className = '', variant = 'default' }) => {
  const sizes = {
    'xs': { text: 'text-[10px]', logo: 'h-3' },
    'sm': { text: 'text-xs', logo: 'h-4' },
    'md': { text: 'text-sm', logo: 'h-5' },
    'lg': { text: 'text-base', logo: 'h-6' },
  };

  // Styled variant with QuizBall aesthetic
  if (variant === 'styled') {
    return (
      <div className={`flex items-center justify-center gap-2 ${className}`}>
        <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-black/40 via-black/60 to-black/40 border border-white/10 rounded-full backdrop-blur-sm">
          <span className={`${sizes[size].text} font-bold uppercase tracking-[0.2em] bg-gradient-to-r from-gray-400 to-gray-300 bg-clip-text text-transparent`}>
            Powered by
          </span>
          <div className="w-px h-3 bg-gradient-to-b from-transparent via-neon-pink to-transparent" />
          <Score90Logo variant="white" className={`${sizes[size].logo} drop-shadow-[0_0_8px_rgba(236,72,153,0.5)]`} />
        </div>
      </div>
    );
  }

  // Neon glow variant
  if (variant === 'neon') {
    return (
      <div className={`flex items-center justify-center gap-3 ${className}`}>
        <div className="h-px flex-1 max-w-16 bg-gradient-to-r from-transparent to-neon-blue/50" />
        <div className="flex items-center gap-2">
          <span className={`${sizes[size].text} font-extrabold uppercase tracking-[0.15em] text-gray-500`}>
            Powered by
          </span>
          <Score90Logo variant="white" className={`${sizes[size].logo} drop-shadow-[0_0_10px_rgba(0,245,255,0.4)]`} />
        </div>
        <div className="h-px flex-1 max-w-16 bg-gradient-to-l from-transparent to-neon-pink/50" />
      </div>
    );
  }

  // Minimal variant with accent
  if (variant === 'minimal') {
    return (
      <div className={`flex items-center justify-center gap-2 opacity-60 hover:opacity-100 transition-opacity ${className}`}>
        <span className={`${sizes[size].text} font-medium uppercase tracking-widest text-gray-500`}>
          Powered by
        </span>
        <Score90Logo variant="white" className={sizes[size].logo} />
      </div>
    );
  }

  // Default - enhanced version
  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <span className={`${sizes[size].text} font-bold uppercase tracking-[0.15em] text-gray-400`}>
        Powered by
      </span>
      <Score90Logo variant="white" className={`${sizes[size].logo} drop-shadow-[0_0_6px_rgba(236,72,153,0.3)]`} />
    </div>
  );
};