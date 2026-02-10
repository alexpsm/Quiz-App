import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Instagram, ExternalLink } from 'lucide-react';

// Score90 Instagram posts - these would ideally come from an API
// Using placeholder data structure that matches Instagram's embed format
const SCORE90_POSTS = [
  {
    id: '1',
    imageUrl: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&h=400&fit=crop',
    caption: '⚽ The atmosphere was ELECTRIC! What a match! 🔥 #Score90 #Football',
    likes: '12.5K',
    permalink: 'https://instagram.com/score90',
  },
  {
    id: '2',
    imageUrl: 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=400&h=400&fit=crop',
    caption: '🏆 Champions League nights hit different... Who\'s your pick for the final? 👇 #UCL #Score90',
    likes: '8.2K',
    permalink: 'https://instagram.com/score90',
  },
  {
    id: '3',
    imageUrl: 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=400&h=400&fit=crop',
    caption: '💪 Training day vibes! The grind never stops 🎯 #FootballLife #Score90',
    likes: '15.1K',
    permalink: 'https://instagram.com/score90',
  },
  {
    id: '4',
    imageUrl: 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=400&h=400&fit=crop',
    caption: '🎉 GOOOAAAL! That celebration says it all 😤🔥 #Score90 #GoalOfTheDay',
    likes: '22.3K',
    permalink: 'https://instagram.com/score90',
  },
  {
    id: '5',
    imageUrl: 'https://images.unsplash.com/photo-1459865264687-595d652de67e?w=400&h=400&fit=crop',
    caption: '📊 Stats don\'t lie! Who\'s been the best player this season? 🤔 #FootballStats #Score90',
    likes: '9.8K',
    permalink: 'https://instagram.com/score90',
  },
];

export function InstagramCarousel({ autoPlay = true, interval = 4000 }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
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
    // Reset timer on manual navigation
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % SCORE90_POSTS.length);
      }, interval);
    }
  };

  const goNext = () => goTo((currentIndex + 1) % SCORE90_POSTS.length);
  const goPrev = () => goTo((currentIndex - 1 + SCORE90_POSTS.length) % SCORE90_POSTS.length);

  const currentPost = SCORE90_POSTS[currentIndex];

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
            <p className="text-[10px] text-gray-500">Football Content</p>
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
          <motion.img
            key={currentPost.id}
            src={currentPost.imageUrl}
            alt={`Score90 post ${currentIndex + 1}`}
            className="w-full h-full object-cover"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          />
        </AnimatePresence>

        {/* Navigation Arrows */}
        <button
          onClick={goPrev}
          className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors"
          data-testid="carousel-prev"
        >
          <ChevronLeft size={18} />
        </button>
        <button
          onClick={goNext}
          className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors"
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
      </div>

      {/* Content */}
      <div className="p-4 space-y-2">
        {/* Likes */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-white">{currentPost.likes}</span>
          <span className="text-xs text-gray-500">likes</span>
        </div>

        {/* Caption */}
        <p className="text-sm text-gray-300 line-clamp-2">
          <span className="font-bold text-white">score90 </span>
          {currentPost.caption}
        </p>

        {/* Dots Indicator */}
        <div className="flex items-center justify-center gap-1.5 pt-2">
          {SCORE90_POSTS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => goTo(idx)}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                idx === currentIndex
                  ? 'bg-pink-500 w-3'
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
              data-testid={`carousel-dot-${idx}`}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-white/10 text-center">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider">
          While you wait • <span className="text-pink-400">@score90</span>
        </p>
      </div>
    </motion.div>
  );
}

export default InstagramCarousel;
