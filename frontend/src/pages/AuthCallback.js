import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { auth } from '../lib/api';
import { useAuth } from '../context/AuthContext';

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processSession = async () => {
      try {
        const hash = location.hash;
        const params = new URLSearchParams(hash.substring(1));
        const sessionId = params.get('session_id');

        if (!sessionId) {
          navigate('/login');
          return;
        }

        const response = await auth.processSession(sessionId);
        const { session_token, user } = response.data;

        // Store session token in cookie (done by backend)
        setUser(user);

        // Redirect to onboarding if no username, otherwise dashboard
        if (!user.username) {
          navigate('/onboarding', { state: { user } });
        } else {
          navigate('/dashboard', { state: { user } });
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        navigate('/login');
      }
    };

    processSession();
  }, [location, navigate, setUser]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-400">Processing authentication...</p>
      </div>
    </div>
  );
}