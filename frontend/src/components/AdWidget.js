import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink } from 'lucide-react';

const FLASHSCORE_LOGO = "https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/kj1jrjqi_flashscore.png";
const POLYMARKET_LOGO = "https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/n5b3g40m_Company_Logo_Polymarket.png";

// Compact inline ad for between rounds/questions
export function InlineAd({ type = 'flashscore', className = '' }) {
  const ads = {
    flashscore: {
      logo: FLASHSCORE_LOGO,
      text: "Live Scores",
      url: "https://www.flashscore.com",
      bg: "from-[#1a1a2e] to-[#0d1117]",
      border: "border-red-500/20",
      hoverBorder: "hover:border-red-500/40"
    },
    polymarket: {
      logo: POLYMARKET_LOGO,
      text: "Predict & Win",
      url: "https://polymarket.com",
      bg: "from-[#1a1a2e] to-[#0d1117]",
      border: "border-blue-500/20",
      hoverBorder: "hover:border-blue-500/40"
    }
  };
  
  const ad = ads[type];
  
  return (
    <motion.a
      href={ad.url}
      target="_blank"
      rel="noopener noreferrer sponsored"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-center gap-2 bg-gradient-to-r ${ad.bg} border ${ad.border} ${ad.hoverBorder} rounded px-3 py-1.5 transition-all group ${className}`}
      data-testid={`ad-inline-${type}`}
    >
      <img src={ad.logo} alt={type} className="h-4 w-auto object-contain" />
      <span className="text-[10px] text-gray-500 group-hover:text-gray-400 uppercase tracking-wider">{ad.text}</span>
      <ExternalLink size={10} className="text-gray-600 group-hover:text-gray-400" />
    </motion.a>
  );
}

// Small banner for dashboard/profile - horizontal strip
export function AdBanner({ type = 'flashscore', size = 'sm', className = '' }) {
  const ads = {
    flashscore: {
      logo: FLASHSCORE_LOGO,
      tagline: "Check live football scores",
      cta: "View Scores",
      url: "https://www.flashscore.com",
      bgColor: "bg-gradient-to-r from-[#e30613]/10 to-transparent",
      borderColor: "border-red-500/20",
      ctaColor: "text-red-400 hover:text-red-300"
    },
    polymarket: {
      logo: POLYMARKET_LOGO,
      tagline: "Predict football outcomes",
      cta: "Start Trading",
      url: "https://polymarket.com",
      bgColor: "bg-gradient-to-r from-blue-500/10 to-transparent",
      borderColor: "border-blue-500/20",
      ctaColor: "text-blue-400 hover:text-blue-300"
    }
  };
  
  const ad = ads[type];
  const isSmall = size === 'sm';
  
  return (
    <motion.a
      href={ad.url}
      target="_blank"
      rel="noopener noreferrer sponsored"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className={`block ${ad.bgColor} border ${ad.borderColor} rounded-lg overflow-hidden transition-all hover:border-opacity-50 ${className}`}
      data-testid={`ad-banner-${type}`}
    >
      <div className={`flex items-center justify-between ${isSmall ? 'px-3 py-2' : 'px-4 py-3'}`}>
        <div className="flex items-center gap-3">
          <img 
            src={ad.logo} 
            alt={type} 
            className={`${isSmall ? 'h-5' : 'h-6'} w-auto object-contain`} 
          />
          <span className={`${isSmall ? 'text-xs' : 'text-sm'} text-gray-400 hidden sm:inline`}>
            {ad.tagline}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`${isSmall ? 'text-xs' : 'text-sm'} font-medium ${ad.ctaColor} transition-colors`}>
            {ad.cta}
          </span>
          <ExternalLink size={isSmall ? 12 : 14} className="text-gray-500" />
        </div>
      </div>
      <div className="h-px bg-gradient-to-r from-transparent via-gray-700/30 to-transparent" />
      <div className="px-3 py-1 text-center">
        <span className="text-[9px] text-gray-600 uppercase tracking-widest">Sponsored</span>
      </div>
    </motion.a>
  );
}

// Game over / results screen ad - more prominent but still tasteful
export function ResultsAd({ className = '' }) {
  // Randomly show one of the two ads
  const showFlashscore = React.useMemo(() => Math.random() > 0.5, []);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2 }}
      className={`${className}`}
    >
      {showFlashscore ? (
        <a
          href="https://www.flashscore.com"
          target="_blank"
          rel="noopener noreferrer sponsored"
          className="block bg-gradient-to-r from-[#e30613]/5 via-[#1a1a2e] to-[#e30613]/5 border border-red-500/20 hover:border-red-500/40 rounded-lg p-4 transition-all group"
          data-testid="ad-results-flashscore"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={FLASHSCORE_LOGO} alt="FlashScore" className="h-6 w-auto" />
              <div>
                <p className="text-sm text-gray-300 group-hover:text-white transition-colors">
                  Check today's football scores
                </p>
                <p className="text-[10px] text-gray-500">Live results from all leagues</p>
              </div>
            </div>
            <div className="flex items-center gap-1 text-red-400 group-hover:text-red-300">
              <span className="text-xs font-medium">View Now</span>
              <ExternalLink size={12} />
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-gray-800/50 text-center">
            <span className="text-[9px] text-gray-600 uppercase tracking-widest">Ad</span>
          </div>
        </a>
      ) : (
        <a
          href="https://polymarket.com"
          target="_blank"
          rel="noopener noreferrer sponsored"
          className="block bg-gradient-to-r from-blue-500/5 via-[#1a1a2e] to-blue-500/5 border border-blue-500/20 hover:border-blue-500/40 rounded-lg p-4 transition-all group"
          data-testid="ad-results-polymarket"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={POLYMARKET_LOGO} alt="Polymarket" className="h-6 w-auto" />
              <div>
                <p className="text-sm text-gray-300 group-hover:text-white transition-colors">
                  Predict match outcomes
                </p>
                <p className="text-[10px] text-gray-500">Trade on football events</p>
              </div>
            </div>
            <div className="flex items-center gap-1 text-blue-400 group-hover:text-blue-300">
              <span className="text-xs font-medium">Explore</span>
              <ExternalLink size={12} />
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-gray-800/50 text-center">
            <span className="text-[9px] text-gray-600 uppercase tracking-widest">Ad</span>
          </div>
        </a>
      )}
    </motion.div>
  );
}

// Minimal "powered by" style footer ad
export function FooterAd({ type = 'flashscore' }) {
  const config = {
    flashscore: {
      logo: FLASHSCORE_LOGO,
      url: "https://www.flashscore.com"
    },
    polymarket: {
      logo: POLYMARKET_LOGO,
      url: "https://polymarket.com"
    }
  };
  
  const ad = config[type];
  
  return (
    <a
      href={ad.url}
      target="_blank"
      rel="noopener noreferrer sponsored"
      className="inline-flex items-center gap-1.5 opacity-40 hover:opacity-70 transition-opacity"
      data-testid={`ad-footer-${type}`}
    >
      <span className="text-[9px] text-gray-500 uppercase tracking-wider">Scores by</span>
      <img src={ad.logo} alt={type} className="h-3 w-auto" />
    </a>
  );
}

export default { InlineAd, AdBanner, ResultsAd, FooterAd };
