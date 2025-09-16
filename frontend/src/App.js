import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Context for global state
const AppContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mock user ID for now
const USER_ID = "user_12345";

// Configure axios defaults
axios.defaults.baseURL = API;

// Components
import Home from './components/Home';
import Platforms from './components/Platforms';
import Assistant from './components/Assistant';
import Settings from './components/Settings';
import Navigation from './components/Navigation';
import Toast from './components/Toast';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);

  // Toast system
  const showToast = (message, type = 'info') => {
    setToast({ message, type, id: Date.now() });
  };

  const hideToast = () => {
    setToast(null);
  };

  // API calls
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

  // Load initial data
  useEffect(() => {
    fetchPortfolio();
    fetchTrades();
    fetchPlatforms();
  }, []);

  const contextValue = {
    currentPage,
    setCurrentPage,
    portfolio,
    trades,
    platforms,
    loading,
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

  return (
    <AppContext.Provider value={contextValue}>
      <div className="app min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" dir="rtl">
        {/* Glass morphism background */}
        <div className="fixed inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-sm"></div>
        
        {/* Main content */}
        <div className="relative z-10 min-h-screen">
          {/* Navigation */}
          <Navigation />
          
          {/* Page content */}
          <main className="pb-20">
            {currentPage === 'home' && <Home />}
            {currentPage === 'platforms' && <Platforms />}
            {currentPage === 'assistant' && <Assistant />}
            {currentPage === 'settings' && <Settings />}
          </main>
        </div>

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