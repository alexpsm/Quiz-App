import React from 'react';
import { motion } from 'framer-motion';
import { BottomNav } from './BottomNav';

export const Layout = ({ children, showNav = true }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-[#1a1a2e] to-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-neon-pink/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-neon-yellow/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
      
      {/* Content container - mobile constrained */}
      <div className="max-w-md mx-auto min-h-screen bg-background/30 backdrop-blur-sm relative shadow-2xl border-x border-white/5">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className={showNav ? 'pb-16' : ''}
        >
          {children}
        </motion.div>
        
        {showNav && <BottomNav />}
      </div>
    </div>
  );
};