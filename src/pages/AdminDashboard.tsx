import React from 'react';
import { Users, List, MessageSquare, Heart, TrendingUp, UserCheck } from 'lucide-react';
import { motion } from 'motion/react';

const AdminDashboard: React.FC = () => {
  const stats = [
    { name: 'Total Users', value: '1,284', icon: Users, color: 'bg-blue-500' },
    { name: 'Total Listings', value: '432', icon: List, color: 'bg-green-500' },
    { name: 'Total Comments', value: '2,845', icon: MessageSquare, color: 'bg-purple-500' },
    { name: 'Total Saves', value: '5,120', icon: Heart, color: 'bg-pink-500' },
  ];

  const recentActivity = [
    { id: 1, user: 'alex_hku', action: 'created a new listing', time: '2 mins ago' },
    { id: 2, user: 'sarah_lee', action: 'commented on a listing', time: '15 mins ago' },
    { id: 3, user: 'jason_w', action: 'registered a new account', time: '1 hour ago' },
    { id: 4, user: 'admin', action: 'suspended user "spammer123"', time: '3 hours ago' },
  ];

  const topListings = [
    { id: 1, title: 'Modern 2BR Flat near HKU', saves: 45, owner: 'sarah_lee' },
    { id: 2, title: 'St. Johns College Dorm Offer', saves: 22, owner: 'hku_dorm' },
    { id: 3, title: 'Cozy Room in Kennedy Town', saves: 12, owner: 'alex_hku' },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Platform Overview</h1>
        <p className="text-gray-500 text-sm">Real-time statistics and activity across RoomieHKU.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200"
          >
            <div className="flex items-center">
              <div className={cn("p-3 rounded-xl text-white mr-4", stat.color)}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900">Recent Activity</h2>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          <div className="divide-y divide-gray-100">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-indigo-600">@{activity.user}</span>
                  <span className="text-gray-600 ml-1">{activity.action}</span>
                </div>
                <span className="text-xs text-gray-400">{activity.time}</span>
              </div>
            ))}
          </div>
          <div className="px-6 py-4 bg-gray-50 text-center">
            <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700">View all activity</button>
          </div>
        </div>

        {/* Top Listings */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900">Most Saved Listings</h2>
            <Heart className="h-5 w-5 text-pink-500" />
          </div>
          <div className="divide-y divide-gray-100">
            {topListings.map((listing) => (
              <div key={listing.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{listing.title}</p>
                  <p className="text-xs text-gray-400">by @{listing.owner} </p>
                </div>
                <div className="flex items-center bg-pink-50 px-3 py-1 rounded-full">
                  <Heart className="h-3 w-3 text-pink-500 mr-1 fill-pink-500" />
                  <span className="text-xs font-bold text-pink-700">{listing.saves}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="px-6 py-4 bg-gray-50 text-center">
            <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700">View all listings</button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function for cn
function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}

export default AdminDashboard;
