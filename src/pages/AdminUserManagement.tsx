import React, { useState } from 'react';
import { User } from '../types';
import { Search, Shield, ShieldAlert, UserX, UserCheck } from 'lucide-react';
import { motion } from 'motion/react';

const MOCK_USERS: User[] = [
  { user_id: '1', username: 'alex_hku', email: 'alex@hku.hk', role: 'user', status: 'active', created_at: '2024-01-15' },
  { user_id: '2', username: 'sarah_lee', email: 'sarah@hku.hk', role: 'user', status: 'active', created_at: '2024-02-01' },
  { user_id: '3', username: 'admin_main', email: 'admin@hku.hk', role: 'admin', status: 'active', created_at: '2023-12-01' },
  { user_id: '4', username: 'spammer123', email: 'spam@gmail.com', role: 'user', status: 'suspended', created_at: '2024-03-10' },
  { user_id: '5', username: 'jason_w', email: 'jason@hku.hk', role: 'user', status: 'active', created_at: '2024-03-15' },
];

const AdminUserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>(MOCK_USERS);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleStatus = (userId: string) => {
    setUsers(users.map(user => {
      if (user.user_id === userId) {
        return { ...user, status: user.status === 'active' ? 'suspended' : 'active' };
      }
      return user;
    }));
  };

  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) || 
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-500 text-sm">Manage user accounts, roles, and access status.</p>
        </div>
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search users..."
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Joined</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold">
                        {user.username[0].toUpperCase()}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-bold text-gray-900">@{user.username}</div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      {user.role === 'admin' ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          <Shield className="h-3 w-3 mr-1" />
                          Admin
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          User
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.status === 'active' ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {user.role !== 'admin' && (
                      <button
                        onClick={() => toggleStatus(user.user_id)}
                        className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          user.status === 'active' 
                            ? "text-red-600 hover:bg-red-50" 
                            : "text-green-600 hover:bg-green-50"
                        }`}
                      >
                        {user.status === 'active' ? (
                          <><UserX className="h-3.5 w-3.5 mr-1.5" /> Suspend</>
                        ) : (
                          <><UserCheck className="h-3.5 w-3.5 mr-1.5" /> Activate</>
                        )}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminUserManagement;
