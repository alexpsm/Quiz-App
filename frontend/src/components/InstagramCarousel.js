import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Instagram, ExternalLink } from 'lucide-react';

// Real Score90 Instagram post IDs
const SCORE90_POSTS = [
  {
    id: 'DUljp9GjZY8',
    postUrl: 'https://www.instagram.com/p/DUljp9GjZY8/',
  },
  {
    id: 'DUlRtt1DeOI',
    postUrl: 'https://www.instagram.com/p/DUlRtt1DeOI/',
  },
  {
    id: 'DUlBOw4DXPh',
    postUrl: 'https://www.instagram.com/p/DUlBOw4DXPh/',
  },
  {
    id: 'DUjLSrrjUgb',
    postUrl: 'https://www.instagram.com/p/DUjLSrrjUgb/',
  },
  {
    id: 'DUge57XDYMm',
    postUrl: 'https://www.instagram.com/p/DUge57XDYMm/',
  },
];

// Load Instagram embed script once
const loadInstagramEmbed = () => {
  return new Promise((resolve) => {
    if (window.instgrm) {
      resolve(window.instgrm);
      return;
    }
    
    if (!document.getElementById('instagram-embed-script')) {
      const script = document.createElement('script');
      script.id = 'instagram-embed-script';
      script.src = '//www.instagram.com/embed.js';
      script.async = true;
      script.onload = () => {
        // Wait a bit for instgrm to initialize
        setTimeout(() => resolve(window.instgrm), 100);
      };
      document.body.appendChild(script);
    } else {
      // Script exists but not loaded yet, poll for it
      const checkInterval = setInterval(() => {
        if (window.instgrm) {
          clearInterval(checkInterval);
          resolve(window.instgrm);
        }
      }, 100);
    }
  });
};

export function InstagramCarousel({ autoPlay = true, interval = 5000 }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [embedsReady, setEmbedsReady] = useState(false);
  const timerRef = useRef(null);
  const containerRef = useRef(null);

  // Load Instagram embed script and process all embeds on mount
  useEffect(() => {
    let mounted = true;
    
    const initEmbeds = async () => {
      const instgrm = await loadInstagramEmbed();
      if (mounted && instgrm) {
        // Process all embeds
        instgrm.Embeds.process();
        setEmbedsReady(true);
      }
    };
    
    initEmbeds();
    
    return () => {
      mounted = false;
    };
  }, []);

  // Auto-advance carousel
  useEffect(() => {
    if (autoPlay && !isPaused) {
      timerRef.current = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % SCORE90_POSTS.length);
      }, interval);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [autoPlay, isPaused, interval]);

  const goTo = (index) => {
    setCurrentIndex(index);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      if (autoPlay && !isPaused) {
        timerRef.current = setInterval(() => {
          setCurrentIndex((prev) => (prev + 1) % SCORE90_POSTS.length);
        }, interval);
      }
    }
  };

  const goNext = () => goTo((currentIndex + 1) % SCORE90_POSTS.length);
  const goPrev = () => goTo((currentIndex - 1 + SCORE90_POSTS.length) % SCORE90_POSTS.length);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-card border-2 border-pink-500/30 rounded-lg overflow-hidden max-w-sm mx-auto"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      data-testid="instagram-carousel"
      ref={containerRef}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 via-pink-500 to-purple-600 flex items-center justify-center">
            <Instagram size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white">score90</p>
            <p className="text-[10px] text-gray-500">Latest Posts</p>
          </div>
        </div>
        <a
          href="https://instagram.com/score90"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-pink-400 hover:text-pink-300 flex items-center gap-1 transition-colors"
        >
          Follow <ExternalLink size={10} />
        </a>
      </div>

      {/* All Embeds Container - render all, show one */}
      <div className="relative overflow-hidden bg-white" style={{ minHeight: '320px' }}>
        {SCORE90_POSTS.map((post, idx) => (
          <div
            key={post.id}
            className="absolute inset-0 transition-opacity duration-300"
            style={{
              opacity: idx === currentIndex ? 1 : 0,
              pointerEvents: idx === currentIndex ? 'auto' : 'none',
              zIndex: idx === currentIndex ? 1 : 0,
            }}
          >
            <blockquote 
              className="instagram-media" 
              data-instgrm-captioned
              data-instgrm-permalink={post.postUrl}
              data-instgrm-version="14"
              style={{
                background: '#FFF',
                border: 0,
                borderRadius: '3px',
                boxShadow: 'none',
                margin: '0',
                padding: 0,
                width: '100%',
                minWidth: '100%',
                maxWidth: '100%',
              }}
            >
              <div style={{ padding: '16px' }}>
                <a 
                  href={post.postUrl}
                  style={{ 
                    background: '#FFFFFF', 
                    lineHeight: 0, 
                    padding: '0 0', 
                    textAlign: 'center', 
                    textDecoration: 'none', 
                    width: '100%' 
                  }}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <div style={{ 
                    display: 'flex', 
                    flexDirection: 'row', 
                    alignItems: 'center',
                    padding: '8px 0'
                  }}>
                    <div style={{
                      backgroundColor: '#F4F4F4',
                      borderRadius: '50%',
                      height: '40px',
                      marginRight: '14px',
                      width: '40px'
                    }}></div>
                    <div style={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      flexGrow: 1
                    }}>
                      <div style={{
                        backgroundColor: '#F4F4F4',
                        borderRadius: '4px',
                        height: '14px',
                        marginBottom: '6px',
                        width: '100px'
                      }}></div>
                      <div style={{
                        backgroundColor: '#F4F4F4',
                        borderRadius: '4px',
                        height: '14px',
                        width: '60px'
                      }}></div>
                    </div>
                  </div>
                  <div style={{ padding: '19% 0' }}></div>
                  <div style={{
                    display: 'block',
                    height: '50px',
                    margin: '0 auto 12px',
                    width: '50px'
                  }}>
                    <Instagram size={50} color="#262626" />
                  </div>
                  <div style={{ paddingTop: '8px' }}>
                    <div style={{
                      color: '#3897f0',
                      fontFamily: 'Arial,sans-serif',
                      fontSize: '14px',
                      fontWeight: 550,
                      textAlign: 'center'
                    }}>
                      View this post on Instagram
                    </div>
                  </div>
                </a>
              </div>
            </blockquote>
          </div>
        ))}

        {/* Navigation Arrows */}
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); goPrev(); }}
          className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors z-20"
          data-testid="carousel-prev"
        >
          <ChevronLeft size={18} />
        </button>
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); goNext(); }}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors z-20"
          data-testid="carousel-next"
        >
          <ChevronRight size={18} />
        </button>

        {/* Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30 z-20">
          <motion.div
            className="h-full bg-gradient-to-r from-yellow-400 via-pink-500 to-purple-600"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{ duration: interval / 1000, ease: 'linear' }}
            key={currentIndex}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 space-y-2 bg-card">
        {/* Dots Indicator */}
        <div className="flex items-center justify-center gap-1.5">
          {SCORE90_POSTS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => goTo(idx)}
              className={`h-1.5 rounded-full transition-all ${
                idx === currentIndex
                  ? 'bg-gradient-to-r from-pink-500 to-purple-500 w-4'
                  : 'bg-gray-600 hover:bg-gray-500 w-1.5'
              }`}
              data-testid={`carousel-dot-${idx}`}
            />
          ))}
        </div>

        <p className="text-[10px] text-gray-500 text-center uppercase tracking-wider">
          While you wait • <a href="https://instagram.com/score90" target="_blank" rel="noopener noreferrer" className="text-pink-400 hover:text-pink-300">@score90</a>
        </p>
      </div>
    </motion.div>
  );
}

export default InstagramCarousel;
