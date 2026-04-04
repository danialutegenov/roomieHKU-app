import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, List, MessageSquare, ArrowLeft } from 'lucide-react';
import { cn } from '../lib/utils';

export const AdminSidebar: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    { name: 'Overview', path: '/admin', icon: LayoutDashboard },
    { name: 'User Management', path: '/admin/users', icon: Users },
    { name: 'Listing Management', path: '/admin/listings', icon: List },
    { name: 'Comments', path: '/admin/comments', icon: MessageSquare },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-[calc(100vh-64px)] sticky top-16 hidden md:block">
      <div className="p-6">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Admin Panel</h2>
        <nav className="space-y-1">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                location.pathname === item.path
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon className={cn("mr-3 h-5 w-5", location.pathname === item.path ? "text-indigo-500" : "text-gray-400")} />
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="mt-8 pt-8 border-t border-gray-200">
          <Link to="/" className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-gray-900 transition-colors">
            <ArrowLeft className="mr-3 h-5 w-5 text-gray-400" />
            Back to Site
          </Link>
        </div>
      </div>
    </div>
  );
};
