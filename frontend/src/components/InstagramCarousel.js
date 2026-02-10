import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Instagram, ExternalLink, Play } from 'lucide-react';

// Real Score90 Instagram posts
const SCORE90_POSTS = [
  {
    id: 'DUljp9GjZY8',
    postUrl: 'https://www.instagram.com/p/DUljp9GjZY8/',
    // Instagram CDN image - these are the actual post thumbnails
    thumbnail: 'https://instagram.com/p/DUljp9GjZY8/media/?size=l',
  },
  {
    id: 'DUlRtt1DeOI',
    postUrl: 'https://www.instagram.com/p/DUlRtt1DeOI/',
    thumbnail: 'https://instagram.com/p/DUlRtt1DeOI/media/?size=l',
  },
  {
    id: 'DUlBOw4DXPh',
    postUrl: 'https://www.instagram.com/p/DUlBOw4DXPh/',
    thumbnail: 'https://instagram.com/p/DUlBOw4DXPh/media/?size=l',
  },
  {
    id: 'DUjLSrrjUgb',
    postUrl: 'https://www.instagram.com/p/DUjLSrrjUgb/',
    thumbnail: 'https://instagram.com/p/DUjLSrrjUgb/media/?size=l',
  },
  {
    id: 'DUge57XDYMm',
    postUrl: 'https://www.instagram.com/p/DUge57XDYMm/',
    thumbnail: 'https://instagram.com/p/DUge57XDYMm/media/?size=l',
  },
];

export function InstagramCarousel({ autoPlay = true, interval = 4000 }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [imageErrors, setImageErrors] = useState({});
  const timerRef = useRef(null);

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

  const currentPost = SCORE90_POSTS[currentIndex];

  const handleImageError = (postId) => {
    setImageErrors(prev => ({ ...prev, [postId]: true }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-card border-2 border-pink-500/30 rounded-lg overflow-hidden max-w-sm mx-auto"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      data-testid="instagram-carousel"
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

      {/* Image Container */}
      <div className="relative aspect-square overflow-hidden bg-black">
        <AnimatePresence mode="wait">
          <motion.a
            key={currentPost.id}
            href={currentPost.postUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full h-full"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            {imageErrors[currentPost.id] ? (
              // Fallback: Show Instagram embed button
              <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-purple-900 to-pink-900">
                <Instagram size={48} className="text-white mb-3" />
                <p className="text-white font-bold text-sm">View on Instagram</p>
                <p className="text-gray-300 text-xs mt-1">@score90</p>
                <div className="mt-4 px-4 py-2 bg-white/20 rounded-full flex items-center gap-2">
                  <Play size={14} className="text-white" />
                  <span className="text-white text-xs font-medium">Open Post</span>
                </div>
              </div>
            ) : (
              <img 
                src={currentPost.thumbnail}
                alt={`Score90 Instagram post`}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                onError={() => handleImageError(currentPost.id)}
              />
            )}
          </motion.a>
        </AnimatePresence>

        {/* Navigation Arrows */}
        <button
          onClick={(e) => { e.preventDefault(); goPrev(); }}
          className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors z-10"
          data-testid="carousel-prev"
        >
          <ChevronLeft size={18} />
        </button>
        <button
          onClick={(e) => { e.preventDefault(); goNext(); }}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors z-10"
          data-testid="carousel-next"
        >
          <ChevronRight size={18} />
        </button>

        {/* Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
          <motion.div
            className="h-full bg-gradient-to-r from-yellow-400 via-pink-500 to-purple-600"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{ duration: interval / 1000, ease: 'linear' }}
            key={currentIndex}
          />
        </div>

        {/* Click to view overlay */}
        <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-sm rounded px-2 py-1 flex items-center gap-1">
          <ExternalLink size={10} className="text-white" />
          <span className="text-[9px] text-white font-medium">View Post</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
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

        {/* Post counter */}
        <div className="text-center">
          <span className="text-xs text-gray-500">
            {currentIndex + 1} / {SCORE90_POSTS.length}
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-white/10 bg-black/20">
        <p className="text-[10px] text-gray-500 text-center uppercase tracking-wider">
          While you wait • <a href="https://instagram.com/score90" target="_blank" rel="noopener noreferrer" className="text-pink-400 hover:text-pink-300">@score90</a>
        </p>
      </div>
    </motion.div>
  );
}

export default InstagramCarousel;
