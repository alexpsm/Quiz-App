import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Coins, Zap, Crown, Check, Loader2 } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

const CREDIT_PACKAGES = [
  { id: 'credits_100', amount: 100, price: '$0.99', icon: Coins, gradient: 'from-neon-blue to-neon-blue/70' },
  { id: 'credits_500', amount: 500, price: '$3.99', icon: Zap, popular: true, gradient: 'from-neon-pink to-neon-pink/70' },
  { id: 'credits_1000', amount: 1000, price: '$6.99', icon: Crown, gradient: 'from-neon-yellow to-neon-orange' },
];

export default function Store() {
  const { user, checkAuth } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [purchasing, setPurchasing] = useState('');
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [polling, setPolling] = useState(false);

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

  return (
    <Layout>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
            Store
          </h1>
          <PoweredByScore90 size="sm" className="justify-center" />
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

        {/* Banner Ad Placeholder */}
        <div className="bg-gray-900/50 border-2 border-gray-700 rounded-lg p-8 text-center backdrop-blur-sm">
          <p className="text-sm text-gray-500 uppercase tracking-wider">Ad Space</p>
          <p className="text-xs text-gray-600 mt-1">Banner advertisement</p>
        </div>
      </div>
    </Layout>
  );
}
