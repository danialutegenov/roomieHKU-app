import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import { Navbar } from './components/Navbar';
import { AdminSidebar } from './components/AdminSidebar';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import AdminUserManagement from './pages/AdminUserManagement';
import AdminListingManagement from './pages/AdminListingManagement';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAdmin } = useAuth();
  return isAdmin ? <>{children}</> : <Navigate to="/" />;
};

const AdminLayout: React.FC = () => {
  return (
    <div className="flex bg-gray-50 min-h-[calc(100vh-64px)]">
      <AdminSidebar />
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};

const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <footer className="bg-gray-50 border-t border-gray-200 py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-500 text-sm">© 2024 RoomieHKU. Built for HKU Students.</p>
        </div>
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected User Routes */}
            <Route path="/create-listing" element={<PrivateRoute><div>Create Listing Page (Coming Soon)</div></PrivateRoute>} />
            <Route path="/profile" element={<PrivateRoute><div>Profile Page (Coming Soon)</div></PrivateRoute>} />
            <Route path="/saved-listings" element={<PrivateRoute><div>Saved Listings Page (Coming Soon)</div></PrivateRoute>} />
            <Route path="/listing/:id" element={<div>Listing Detail Page (Coming Soon)</div>} />

            {/* Admin Routes */}
            <Route path="/admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<AdminUserManagement />} />
              <Route path="listings" element={<AdminListingManagement />} />
              <Route path="comments" element={<div>Comment Management (Coming Soon)</div>} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}
