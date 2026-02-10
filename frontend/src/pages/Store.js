import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Coins, Zap, Crown, Check, Loader2, Trophy, Clock, Lock, Ticket } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { GoogleSportsAd } from '../components/GoogleAd';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

const CREDIT_PACKAGES = [
  { id: 'credits_100', amount: 100, price: '$0.99', icon: Coins, gradient: 'from-neon-blue to-neon-blue/70' },
  { id: 'credits_500', amount: 500, price: '$3.99', icon: Zap, popular: true, gradient: 'from-neon-pink to-neon-pink/70' },
  { id: 'credits_1000', amount: 1000, price: '$6.99', icon: Crown, gradient: 'from-neon-yellow to-neon-orange' },
];

// Prize Draw images and data
const PRIZE_DRAWS = [
  {
    id: 'draw_ucl_final',
    title: 'UCL Final Tickets',
    subtitle: '2 x VIP Tickets to Munich',
    image: 'https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/yaiwjbh1_Screenshot%202026-02-10%20at%2018.41.34.png',
    cost: 500,
    minTier: 20,
    endsIn: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
    gradient: 'from-blue-600 to-indigo-800',
    borderColor: 'border-blue-500/50',
    entries: 2847,
  },
  {
    id: 'draw_signed_jersey',
    title: 'Signed Messi Jersey',
    subtitle: 'Official Inter Miami Kit',
    image: 'https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/c2ll96hh_Screenshot%202026-02-10%20at%2018.43.31.png',
    cost: 250,
    minTier: 15,
    endsIn: 3 * 24 * 60 * 60 * 1000, // 3 days
    gradient: 'from-pink-600 to-rose-800',
    borderColor: 'border-pink-500/50',
    entries: 5621,
  },
  {
    id: 'draw_ps5_fc25',
    title: 'PS5 + FC25 Bundle',
    subtitle: 'Console & Ultimate Edition',
    image: 'https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/taa1j8kh_Screenshot%202026-02-10%20at%2018.43.07.png',
    cost: 150,
    minTier: 10,
    endsIn: 5 * 24 * 60 * 60 * 1000, // 5 days
    gradient: 'from-purple-600 to-violet-800',
    borderColor: 'border-purple-500/50',
    entries: 8934,
  },
  {
    id: 'draw_stadium_tour',
    title: 'Stadium Tour Package',
    subtitle: 'Old Trafford VIP Experience',
    image: 'https://customer-assets.emergentagent.com/job_9083e011-eede-4abb-ab38-b39804918e3e/artifacts/o14h0195_Screenshot%202026-02-10%20at%2018.42.44.png',
    cost: 100,
    minTier: 5,
    endsIn: 10 * 24 * 60 * 60 * 1000, // 10 days
    gradient: 'from-red-600 to-red-900',
    borderColor: 'border-red-500/50',
    entries: 12453,
  },
];

// Countdown timer hook
function useCountdown(endTimeMs) {
  const [timeLeft, setTimeLeft] = useState(endTimeMs);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => Math.max(0, prev - 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);
  
  const days = Math.floor(timeLeft / (24 * 60 * 60 * 1000));
  const hours = Math.floor((timeLeft % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
  const minutes = Math.floor((timeLeft % (60 * 60 * 1000)) / (60 * 1000));
  const seconds = Math.floor((timeLeft % (60 * 1000)) / 1000);
  
  return { days, hours, minutes, seconds, timeLeft };
}

function PrizeDrawCard({ draw, userTier, userCredits, onEnter }) {
  const { days, hours, minutes, seconds } = useCountdown(draw.endsIn);
  const canEnter = userTier >= draw.minTier;
  const hasEnoughCredits = userCredits >= draw.cost;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-card border-2 ${draw.borderColor} rounded-lg overflow-hidden relative group`}
      data-testid={`prize-draw-${draw.id}`}
    >
      {/* Prize Image */}
      <div className="relative h-36 overflow-hidden">
        <img 
          src={draw.image} 
          alt={draw.title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className={`absolute inset-0 bg-gradient-to-t ${draw.gradient} opacity-60`} />
        
        {/* Countdown overlay */}
        <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm rounded px-2 py-1 flex items-center gap-1.5">
          <Clock size={12} className="text-neon-yellow" />
          <span className="text-[10px] font-mono font-bold text-white">
            {days > 0 ? `${days}d ` : ''}{String(hours).padStart(2, '0')}:{String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </span>
        </div>
        
        {/* Tier requirement badge */}
        <div className={`absolute top-2 left-2 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${
          canEnter ? 'bg-neon-yellow/90 text-black' : 'bg-gray-800/90 text-gray-400'
        }`}>
          {canEnter ? (
            <><Trophy size={10} /> Eligible</>
          ) : (
            <><Lock size={10} /> Tier {draw.minTier}+</>
          )}
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h4 className="font-bold text-white text-sm uppercase tracking-tight">{draw.title}</h4>
          <p className="text-xs text-gray-500">{draw.subtitle}</p>
        </div>
        
        {/* Stats row */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1 text-gray-400">
            <Ticket size={12} />
            <span>{draw.entries.toLocaleString()} entries</span>
          </div>
          <div className="flex items-center gap-1">
            <Coins size={12} className="text-neon-yellow" />
            <span className="font-bold text-neon-yellow">{draw.cost}</span>
          </div>
        </div>
        
        {/* Enter button */}
        <button
          onClick={() => onEnter(draw)}
          disabled={!canEnter || !hasEnoughCredits}
          className={`w-full py-2.5 rounded-sm font-bold uppercase text-xs tracking-wider transition-all active:scale-95 ${
            !canEnter 
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
              : !hasEnoughCredits
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : `bg-gradient-to-r ${draw.gradient} text-white hover:opacity-90 shadow-lg`
          }`}
          data-testid={`enter-draw-${draw.id}`}
        >
          {!canEnter ? (
            <span className="flex items-center justify-center gap-1">
              <Lock size={12} /> Tier {draw.minTier} Required
            </span>
          ) : !hasEnoughCredits ? (
            `Need ${draw.cost} Credits`
          ) : (
            <span className="flex items-center justify-center gap-1">
              <Ticket size={12} /> Enter Draw
            </span>
          )}
        </button>
      </div>
    </motion.div>
  );
}

export default function Store() {
  const { user, checkAuth } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [purchasing, setPurchasing] = useState('');
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [polling, setPolling] = useState(false);
  const [enteringDraw, setEnteringDraw] = useState(null);

  const userTier = user?.player_tier || 1;
  const userCredits = user?.credits || 0;

  const pollPaymentStatus = useCallback(async (sessionId, attempts = 0) => {
    const maxAttempts = 8;
    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      setPolling(false);
      return;
    }

    try {
      const response = await api.get(`/payments/status/${sessionId}`);
      const data = response.data;

      if (data.payment_status === 'paid') {
        setPaymentStatus('paid');
        setPolling(false);
        await checkAuth(); // Refresh user data to show updated credits
        // Clean URL
        setSearchParams({});
        return;
      } else if (data.status === 'expired') {
        setPaymentStatus('expired');
        setPolling(false);
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      console.error('Poll error:', error);
      setPaymentStatus('error');
      setPolling(false);
    }
  }, [checkAuth, setSearchParams]);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId && !polling && !paymentStatus) {
      setPolling(true);
      setPaymentStatus('processing');
      pollPaymentStatus(sessionId);
    }
  }, [searchParams, polling, paymentStatus, pollPaymentStatus]);

  const handlePurchase = async (packageId) => {
    setPurchasing(packageId);
    try {
      const response = await api.post('/payments/checkout', {
        package_id: packageId,
        origin_url: window.location.origin,
      });
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Purchase failed:', error);
      setPurchasing('');
    }
  };

  const handleEnterDraw = async (draw) => {
    if (userTier < draw.minTier || userCredits < draw.cost) return;
    
    setEnteringDraw(draw.id);
    try {
      const response = await api.post('/prize-draws/enter', {
        draw_id: draw.id,
        cost: draw.cost
      });
      await checkAuth(); // Refresh user credits
      alert(`🎉 Successfully entered ${draw.title}!\n\nCredits spent: ${draw.cost}\nRemaining: ${response.data.remaining_credits}\n\nGood luck!`);
    } catch (error) {
      console.error('Failed to enter draw:', error);
      if (error.response?.data?.detail) {
        alert(`Error: ${error.response.data.detail}`);
      } else {
        alert('Failed to enter draw. Please try again.');
      }
    } finally {
      setEnteringDraw(null);
    }
  };

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
            Store
          </h1>
          <PoweredByScore90 size="sm" variant="neon" className="justify-center" />
          <p className="text-sm text-gray-400 mt-2">Get credits and go premium</p>
        </div>

        {/* Payment Status Banner */}
        {paymentStatus && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`border-2 rounded-lg p-4 text-center ${
              paymentStatus === 'paid' ? 'bg-neon-yellow/10 border-neon-yellow' :
              paymentStatus === 'processing' ? 'bg-neon-blue/10 border-neon-blue' :
              'bg-destructive/10 border-destructive'
            }`}
            data-testid="payment-status-banner"
          >
            {paymentStatus === 'processing' && (
              <div className="flex items-center justify-center gap-2">
                <Loader2 className="animate-spin text-neon-blue" size={20} />
                <span className="text-neon-blue font-bold">Processing payment...</span>
              </div>
            )}
            {paymentStatus === 'paid' && (
              <div className="flex items-center justify-center gap-2">
                <Check className="text-neon-yellow" size={20} />
                <span className="text-neon-yellow font-bold">Payment successful! Credits added.</span>
              </div>
            )}
            {(paymentStatus === 'expired' || paymentStatus === 'error' || paymentStatus === 'timeout') && (
              <span className="text-destructive font-bold">Payment failed. Please try again.</span>
            )}
          </motion.div>
        )}

        {/* Current Balance */}
        <div className="bg-card border-2 border-neon-yellow/50 rounded-lg p-6 text-center shadow-neon-yellow">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-2">Your Balance</p>
          <p className="text-5xl font-black tracking-tighter text-neon-yellow" data-testid="credits-balance">{user?.credits}</p>
          <p className="text-xs text-gray-500 mt-1">Credits</p>
        </div>

        {/* Credit Packages */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">Buy Credits</h3>
          
          <div className="space-y-3">
            {CREDIT_PACKAGES.map((pkg, index) => {
              const Icon = pkg.icon;
              return (
                <motion.div
                  key={pkg.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`bg-card border-2 rounded-lg p-6 relative ${
                    pkg.popular ? 'border-neon-pink shadow-neon-pink' : 'border-white/10'
                  }`}
                >
                  {pkg.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-neon-pink to-neon-yellow text-black px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                      Popular
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${pkg.gradient} border-2 border-white/20 flex items-center justify-center shadow-lg`}>
                        <Icon className="text-white" size={24} />
                      </div>
                      <div>
                        <p className="text-2xl font-black tracking-tighter text-white">{pkg.amount}</p>
                        <p className="text-xs text-gray-500 uppercase tracking-wider">Credits</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-black tracking-tighter text-neon-yellow">{pkg.price}</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handlePurchase(pkg.id)}
                    disabled={purchasing === pkg.id}
                    className={`w-full bg-gradient-to-r ${pkg.gradient} text-white hover:opacity-90 h-10 px-6 rounded-sm font-bold uppercase tracking-wider transition-all active:scale-95 disabled:opacity-50`}
                    data-testid={`buy-credits-${pkg.amount}`}
                  >
                    {purchasing === pkg.id ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="animate-spin" size={16} />
                        Redirecting...
                      </span>
                    ) : 'Buy Now'}
                  </button>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Premium */}
        <div className="bg-gradient-to-r from-electric-purple to-neon-pink border-2 border-electric-purple/50 rounded-lg p-6 shadow-neon-pink">
          <div className="text-center mb-4">
            <Crown className="text-neon-yellow mx-auto mb-2" size={48} />
            <h3 className="text-2xl font-extrabold tracking-tighter uppercase text-white mb-1">Premium</h3>
            <p className="text-sm text-gray-200">Ad-free experience, updated monthly</p>
          </div>
          
          <div className="text-center mb-6">
            <p className="text-4xl font-black tracking-tighter text-neon-yellow">$0.99</p>
            <p className="text-xs text-gray-300 mt-1">per month</p>
          </div>
          
          <button
            onClick={() => handlePurchase('premium')}
            disabled={purchasing === 'premium'}
            className="w-full bg-neon-yellow text-black hover:bg-neon-orange h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all active:scale-95 shadow-neon-yellow disabled:opacity-50"
            data-testid="buy-premium"
          >
            {purchasing === 'premium' ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="animate-spin" size={16} />
                Redirecting...
              </span>
            ) : 'Go Premium'}
          </button>
        </div>

        {/* Prize Draws Section */}
        <div className="space-y-4" data-testid="prize-draws-section">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold uppercase tracking-tight text-white flex items-center gap-2">
                <Trophy className="text-neon-yellow" size={24} />
                Prize Draws
              </h3>
              <p className="text-xs text-gray-500 mt-1">Spend credits for a chance to win amazing prizes</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">Your Tier</p>
              <p className="text-lg font-black text-neon-blue">{userTier}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {PRIZE_DRAWS.map((draw, index) => (
              <motion.div
                key={draw.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <PrizeDrawCard 
                  draw={draw}
                  userTier={userTier}
                  userCredits={userCredits}
                  onEnter={handleEnterDraw}
                />
              </motion.div>
            ))}
          </div>
          
          {/* Info box */}
          <div className="bg-black/30 border border-white/10 rounded-lg p-4">
            <p className="text-xs text-gray-400 text-center">
              <span className="text-neon-yellow font-bold">How it works:</span> Each credit spent = 1 entry. 
              Higher tier requirements = better odds. Winners drawn at countdown end.
            </p>
          </div>
        </div>

        {/* Google AdSense Sports Ad */}
        <GoogleSportsAd className="mt-2" />
      </div>
    </Layout>
  );
}
