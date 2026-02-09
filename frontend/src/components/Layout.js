import React from 'react';
import { motion } from 'framer-motion';
import { BottomNav } from './BottomNav';

export const Layout = ({ children, showNav = true }) => {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background texture */}
      <div
        className="fixed inset-0 z-0 opacity-20 mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage: "url('https://grainy-gradients.vercel.app/noise.svg')",
        }}
      />
      
      {/* Content container - mobile constrained */}
      <div className="max-w-md mx-auto min-h-screen bg-background relative shadow-2xl border-x border-white/5">
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