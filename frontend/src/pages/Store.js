import React from 'react';
import { motion } from 'framer-motion';
import { Coins, Zap, Crown } from 'lucide-react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function Store() {
  const { user } = useAuth();

  const creditPackages = [
    { amount: 100, price: '$0.99', icon: Coins },
    { amount: 500, price: '$3.99', icon: Zap, popular: true },
    { amount: 1000, price: '$6.99', icon: Crown },
  ];

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-white mb-2">
            Store
          </h1>
          <p className="text-sm text-gray-400">Get credits and remove ads</p>
        </div>

        {/* Current Balance */}
        <div className="bg-card border border-white/10 rounded-lg p-6 text-center">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-2">Your Balance</p>
          <p className="text-5xl font-black tracking-tighter text-primary">{user?.credits}</p>
          <p className="text-xs text-gray-500 mt-1">Credits</p>
        </div>

        {/* Credit Packages */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">
            Buy Credits
          </h3>
          
          <div className="space-y-3">
            {creditPackages.map((pkg, index) => {
              const Icon = pkg.icon;
              return (
                <motion.div
                  key={pkg.amount}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`bg-card border rounded-lg p-6 relative ${
                    pkg.popular ? 'border-primary shadow-[0_0_20px_-5px_rgba(251,191,36,0.5)]' : 'border-white/10'
                  }`}
                >
                  {pkg.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-black px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                      Popular
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-primary/20 border border-primary flex items-center justify-center">
                        <Icon className="text-primary" size={24} />
                      </div>
                      <div>
                        <p className="text-2xl font-black tracking-tighter text-white">
                          {pkg.amount}
                        </p>
                        <p className="text-xs text-gray-500 uppercase tracking-wider">Credits</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-black tracking-tighter text-primary">
                        {pkg.price}
                      </p>
                    </div>
                  </div>
                  
                  <button
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 rounded-sm font-bold uppercase tracking-wider transition-all active:scale-95"
                    data-testid={`buy-credits-${pkg.amount}`}
                  >
                    Buy Now
                  </button>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Ad-Free Subscription */}
        <div className="bg-gradient-to-r from-purple-900 to-indigo-900 border border-purple-500/50 rounded-lg p-6">
          <div className="text-center mb-4">
            <Crown className="text-yellow-400 mx-auto mb-2" size={48} />
            <h3 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-1">
              Premium
            </h3>
            <p className="text-sm text-gray-300">Remove all ads forever</p>
          </div>
          
          <div className="text-center mb-6">
            <p className="text-4xl font-black tracking-tighter text-yellow-400">$4.99</p>
            <p className="text-xs text-gray-400 mt-1">One-time purchase</p>
          </div>
          
          <button
            className="w-full bg-yellow-400 text-black hover:bg-yellow-300 h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all active:scale-95"
            data-testid="buy-premium"
          >
            Go Premium
          </button>
        </div>

        {/* Banner Ad Placeholder */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-8 text-center">
          <p className="text-sm text-gray-500 uppercase tracking-wider">Ad Space</p>
          <p className="text-xs text-gray-600 mt-1">Banner advertisement</p>
        </div>
      </div>
    </Layout>
  );
}