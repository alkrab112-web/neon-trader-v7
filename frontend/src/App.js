import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Context for global state
const AppContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.baseURL = API;

// JWT Token management
const getStoredToken = () => localStorage.getItem('neon_trader_token');
const setStoredToken = (token) => localStorage.setItem('neon_trader_token', token);
const removeStoredToken = () => localStorage.removeItem('neon_trader_token');

// Set up axios interceptor for JWT tokens
axios.interceptors.request.use(
  (config) => {
    const token = getStoredToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 responses globally
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Token expired or invalid, clear it and redirect to login
      removeStoredToken();
      window.location.reload(); // Force re-authentication
    }
    return Promise.reject(error);
  }
);

// Components
import Home from './components/Home';
import Platforms from './components/Platforms';
import Assistant from './components/Assistant';
import Settings from './components/Settings';
import TradingTools from './components/TradingTools';
import SmartNotifications from './components/SmartNotifications';
import Navigation from './components/Navigation';
import Toast from './components/Toast';
import Login from './components/Login';
import Header from './components/Header';
import SessionManager from './components/SessionManager';
import UnlockScreen from './components/UnlockScreen';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [isLocked, setIsLocked] = useState(false);
  const [currentUser, setCurrentUser] = useState(null); // New: Store current user info

  // Toast system
  const showToast = (message, type = 'info') => {
    setToast({ message, type, id: Date.now() });
  };

  const hideToast = () => {
    setToast(null);
  };

  // JWT Authentication functions
  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await axios.post('/auth/register', userData);
      
      const { access_token, user_id, email, username } = response.data;
      
      // Store JWT token
      setStoredToken(access_token);
      
      // Set user info
      const userInfo = { id: user_id, email, username };
      setCurrentUser(userInfo);
      setIsAuthenticated(true);
      setIsLocked(false);
      
      // Load initial data
      await Promise.all([
        fetchPortfolio(),
        fetchTrades(),
        fetchPlatforms()
      ]);
      
      return { success: true, message: 'تم إنشاء الحساب بنجاح' };
    } catch (error) {
      console.error('Registration error:', error);
      const message = error.response?.data?.detail || 'خطأ في إنشاء الحساب';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const login = async (loginData) => {
    try {
      setLoading(true);
      const response = await axios.post('/auth/login', loginData);
      
      const { access_token, user_id, email, username } = response.data;
      
      // Store JWT token
      setStoredToken(access_token);
      
      // Set user info
      const userInfo = { id: user_id, email, username };
      setCurrentUser(userInfo);
      setIsAuthenticated(true);
      setIsLocked(false);
      
      // Load initial data
      await Promise.all([
        fetchPortfolio(),
        fetchTrades(),
        fetchPlatforms()
      ]);
      
      return { success: true, message: 'تم تسجيل الدخول بنجاح' };
    } catch (error) {
      console.error('Login error:', error);
      const message = error.response?.data?.detail || 'خطأ في تسجيل الدخول';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Clear JWT token
      removeStoredToken();
      
      // Reset all state
      setIsAuthenticated(false);
      setIsLocked(false);
      setCurrentUser(null);
      setPortfolio(null);
      setTrades([]);
      setPlatforms([]);
      setCurrentPage('home');
      
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      return false;
    }
  };

  const lockApp = () => {
    // Lock app temporarily without clearing session
    setIsLocked(true);
    showToast('تم قفل التطبيق مؤقتاً', 'info');
  };

  const unlockApp = async (masterPassword = null) => {
    try {
      // For temporary lock, verify current user still valid  
      const currentUserResponse = await axios.get('/auth/me');
      if (currentUserResponse.data) {
        setIsLocked(false);
        showToast('تم فتح القفل', 'success');
        return true;
      } else {
        // Session invalid, redirect to login
        await logout();
        return false;
      }
    } catch (error) {
      console.error('Unlock error:', error);
      // If token expired, logout
      await logout();
      return false;
    }
  };

  // Check authentication on app start
  useEffect(() => {
    const checkAuth = () => {
      try {
        const sessionData = localStorage.getItem('neon_trader_session');
        if (sessionData) {
          const session = JSON.parse(sessionData);
          const now = Date.now();
          const sessionAge = now - session.loginTime;
          const maxSessionAge = 24 * 60 * 60 * 1000; // 24 hours
          
          if (sessionAge < maxSessionAge) {
            setIsAuthenticated(true);
          } else {
            // Session expired
            localStorage.removeItem('neon_trader_session');
            setIsAuthenticated(false);
          }
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        setIsAuthenticated(false);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated && !isCheckingAuth) {
      fetchPortfolio();
      fetchTrades();
      fetchPlatforms();
    }
  }, [isAuthenticated, isCheckingAuth]);

  // API calls (existing functions remain the same)
  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`/portfolio/${USER_ID}`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      showToast('خطأ في تحميل بيانات المحفظة', 'error');
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await axios.get(`/trades/${USER_ID}`);
      setTrades(response.data);
    } catch (error) {
      console.error('Error fetching trades:', error);
      showToast('خطأ في تحميل الصفقات', 'error');
    }
  };

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`/platforms/${USER_ID}`);
      setPlatforms(response.data);
    } catch (error) {
      console.error('Error fetching platforms:', error);
      showToast('خطأ في تحميل المنصات', 'error');
    }
  };

  const createTrade = async (tradeData) => {
    try {
      setLoading(true);
      const response = await axios.post(`/trades/${USER_ID}`, tradeData);
      showToast(response.data.message, 'success');
      await fetchTrades();
      await fetchPortfolio();
      return response.data;
    } catch (error) {
      console.error('Error creating trade:', error);
      showToast('خطأ في إنشاء الصفقة', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const closeTrade = async (tradeId) => {
    try {
      setLoading(true);
      const response = await axios.put(`/trades/${tradeId}/close`);
      showToast(response.data.message, 'success');
      await fetchTrades();
      await fetchPortfolio();
      return response.data;
    } catch (error) {
      console.error('Error closing trade:', error);
      showToast('خطأ في إغلاق الصفقة', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addPlatform = async (platformData) => {
    try {
      setLoading(true);
      const response = await axios.post(`/platforms/${USER_ID}`, platformData);
      showToast(response.data.message, 'success');
      await fetchPlatforms();
      return response.data;
    } catch (error) {
      console.error('Error adding platform:', error);
      showToast('خطأ في إضافة المنصة', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const testPlatform = async (platformId) => {
    try {
      setLoading(true);
      const response = await axios.put(`/platforms/${platformId}/test`);
      showToast(response.data.message, response.data.success ? 'success' : 'error');
      await fetchPlatforms();
      return response.data;
    } catch (error) {
      console.error('Error testing platform:', error);
      showToast('خطأ في اختبار المنصة', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const contextValue = {
    // Page state
    currentPage,
    setCurrentPage,
    
    // Data
    portfolio,
    trades,
    platforms,
    loading,
    
    // Authentication & Lock
    isAuthenticated,
    isLocked,
    login,
    logout,
    lockApp,
    
    // Functions
    showToast,
    createTrade,
    closeTrade,
    addPlatform,
    testPlatform,
    fetchPortfolio,
    fetchTrades,
    fetchPlatforms,
    userId: USER_ID
  };

  // Show loading screen during auth check
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center animate-pulse">
            <span className="text-white font-bold text-xl">N7</span>
          </div>
          <div className="spinner mb-4"></div>
          <p className="text-white">جاري تحميل التطبيق...</p>
        </div>
      </div>
    );
  }

  return (
    <AppContext.Provider value={contextValue}>
      <div className="app min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" dir="rtl">
        {/* Glass morphism background */}
        <div className="fixed inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-sm"></div>
        
        {!isAuthenticated ? (
          // Login Screen
          <Login />
        ) : isLocked ? (
          // Unlock Screen - App is locked temporarily
          <UnlockScreen onUnlock={unlockApp} />
        ) : (
          // Main App with Session Management
          <SessionManager>
            {/* Navigation */}
            <Navigation />
            
            {/* Header */}
            <Header />
            
            {/* Main content */}
            <div className="relative z-10 min-h-screen">          
              {/* Page content - with proper margins for desktop/mobile */}
              <main className="pt-20 pb-20 md:pb-4 md:pr-24 transition-all duration-300">
                {currentPage === 'home' && <Home />}
                {currentPage === 'platforms' && <Platforms />}
                {currentPage === 'assistant' && <Assistant />}
                {currentPage === 'tools' && <TradingTools />}
                {currentPage === 'notifications' && <SmartNotifications />}
                {currentPage === 'settings' && <Settings />}
              </main>
            </div>
          </SessionManager>
        )}

        {/* Toast notifications */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={hideToast}
          />
        )}
      </div>
    </AppContext.Provider>
  );
}

export { AppContext };
export default App;