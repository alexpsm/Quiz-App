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

export const PoweredByScore90 = ({ size = 'sm', className = '' }) => {
  const sizes = {
    'xs': { text: 'text-xs', logo: 'h-3' },
    'sm': { text: 'text-sm', logo: 'h-4' },
    'md': { text: 'text-base', logo: 'h-5' },
    'lg': { text: 'text-lg', logo: 'h-6' },
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className={`${sizes[size].text} text-gray-400 uppercase tracking-wider`}>Powered by</span>
      <Score90Logo variant="white" className={sizes[size].logo} />
    </div>
  );
};