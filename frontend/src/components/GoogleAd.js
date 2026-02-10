import React, { useEffect, useRef } from 'react';

/**
 * Google AdSense Sports Ad Component
 * 
 * To use real ads, you need to:
 * 1. Sign up at https://www.google.com/adsense
 * 2. Get your publisher ID (ca-pub-XXXXXXXXXX)
 * 3. Create an ad unit and get the ad slot ID
 * 4. Add the AdSense script to your index.html
 * 5. Replace the placeholder values below
 */

// Configuration - Replace with your real AdSense details
const ADSENSE_CONFIG = {
  client: 'ca-pub-XXXXXXXXXXXXXXXXX', // Your AdSense publisher ID
  slot: 'XXXXXXXXXX', // Your ad slot ID
  // Sports-focused ad targeting
  format: 'auto',
  responsive: true,
};

export function GoogleSportsAd({ 
  style = 'display', // 'display', 'infeed', 'inarticle'
  className = '' 
}) {
  const adRef = useRef(null);
  const adLoaded = useRef(false);

  useEffect(() => {
    // Only try to load once
    if (adLoaded.current) return;
    
    // Check if AdSense script is loaded
    if (window.adsbygoogle && adRef.current) {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        adLoaded.current = true;
      } catch (e) {
        console.log('AdSense not available:', e);
      }
    }
  }, []);

  // For demo/development, show a styled placeholder
  // In production with real AdSense, this would show actual ads
  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Styled Sports Ad Placeholder */}
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-white/10 rounded-lg overflow-hidden">
        {/* Ad Header */}
        <div className="flex items-center justify-between px-3 py-1.5 bg-black/40 border-b border-white/5">
          <span className="text-[9px] text-gray-500 uppercase tracking-widest font-medium">Sponsored</span>
          <div className="flex items-center gap-1">
            <svg className="w-3 h-3 text-gray-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            <span className="text-[9px] text-gray-500">Google</span>
          </div>
        </div>

        {/* Ad Content - Sports themed placeholder */}
        <div className="p-4">
          <div className="flex gap-4">
            {/* Ad Image */}
            <div className="w-24 h-24 flex-shrink-0 bg-gradient-to-br from-green-600/20 to-emerald-800/20 rounded-lg flex items-center justify-center border border-green-500/20">
              <svg className="w-12 h-12 text-green-500/60" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1" fill="none"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
                <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" strokeWidth="1"/>
              </svg>
            </div>

            {/* Ad Text */}
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-white mb-1 line-clamp-2">
                Live Sports Streaming
              </h4>
              <p className="text-xs text-gray-400 mb-2 line-clamp-2">
                Watch every Premier League, La Liga & Champions League match live. Start your free trial today.
              </p>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-green-400 font-medium">★★★★★</span>
                <span className="text-[10px] text-gray-500">Ad • Sports</span>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <button className="w-full mt-3 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 rounded text-xs font-bold uppercase tracking-wider text-white transition-all">
            Watch Now
          </button>
        </div>

        {/* AdChoices info */}
        <div className="px-3 py-1.5 bg-black/20 border-t border-white/5 flex items-center justify-between">
          <span className="text-[8px] text-gray-600">Why this ad?</span>
          <div className="flex items-center gap-1 text-[8px] text-gray-600">
            <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm-1 6h2v2h-2V8zm0 4h2v6h-2v-6z"/>
            </svg>
            AdChoices
          </div>
        </div>
      </div>

      {/* Real AdSense ad unit (hidden in demo, would replace placeholder in production) */}
      <ins
        ref={adRef}
        className="adsbygoogle hidden"
        style={{ display: 'none' }}
        data-ad-client={ADSENSE_CONFIG.client}
        data-ad-slot={ADSENSE_CONFIG.slot}
        data-ad-format={ADSENSE_CONFIG.format}
        data-full-width-responsive={ADSENSE_CONFIG.responsive}
      />
    </div>
  );
}

// Horizontal banner variant
export function GoogleSportsBanner({ className = '' }) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border border-white/10 rounded-lg overflow-hidden">
        <div className="flex items-center gap-4 p-3">
          {/* Sports Icon */}
          <div className="w-12 h-12 flex-shrink-0 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 rounded-lg flex items-center justify-center border border-blue-500/20">
            <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c3.95-.49 7-3.85 7-7.93 0-.62-.08-1.21-.21-1.79L15 15v1c0 1.1-.9 2-2 2v1.93zM5.1 6.61C4.4 7.9 4 9.39 4 11c0 2.08.8 3.97 2.1 5.39.26-.81 1-1.39 1.9-1.39h1v-3c0-.55.45-1 1-1h6v-2h-2c-.55 0-1-.45-1-1V6h-2c-1.1 0-2-.9-2-2v-.41C6.57 4.53 5.62 5.48 5.1 6.61z"/>
            </svg>
          </div>

          {/* Ad Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[9px] text-gray-500 uppercase tracking-wider">Sponsored</span>
              <span className="text-[9px] text-gray-600">•</span>
              <span className="text-[9px] text-gray-500">Google Ads</span>
            </div>
            <p className="text-sm font-bold text-white truncate">
              Football Betting Odds & Live Scores
            </p>
            <p className="text-xs text-gray-400 truncate">
              Get the best odds on today's matches. 18+ BeGambleAware
            </p>
          </div>

          {/* CTA */}
          <button className="flex-shrink-0 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-xs font-bold uppercase tracking-wider text-white transition-all">
            Bet Now
          </button>
        </div>
      </div>
    </div>
  );
}

export default GoogleSportsAd;
