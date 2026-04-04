import React, { useState } from 'react';
import { ListingCard } from '../components/ListingCard';
import { Listing } from '../types';
import { Search, Filter, SlidersHorizontal } from 'lucide-react';
import { motion } from 'motion/react';

// Mock data
const MOCK_LISTINGS: Listing[] = [
  {
    listing_id: '1',
    user_id: 'u1',
    owner_username: 'alex_hku',
    title: 'Cozy Room in Kennedy Town',
    description: 'Looking for a clean and tidy roommate. 5 mins walk to MTR.',
    image_url: 'https://picsum.photos/seed/room1/800/600',
    rent: 8500,
    location: 'Kennedy Town',
    listing_type: 'room',
    visibility_status: 'visible',
    save_count: 12,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    listing_id: '2',
    user_id: 'u2',
    owner_username: 'sarah_lee',
    title: 'Modern 2BR Flat near HKU',
    description: 'Spacious flat with great views. Fully furnished.',
    image_url: 'https://picsum.photos/seed/room2/800/600',
    rent: 18000,
    location: 'Sai Ying Pun',
    listing_type: 'apartment',
    visibility_status: 'visible',
    save_count: 45,
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    listing_id: '3',
    user_id: 'u3',
    owner_username: 'jason_w',
    title: 'Looking for Female Roommate',
    description: 'Shared room in Sassoon Road. Female students only.',
    image_url: 'https://picsum.photos/seed/room3/800/600',
    rent: 4500,
    location: 'Pok Fu Lam',
    listing_type: 'roommate_request',
    visibility_status: 'visible',
    save_count: 8,
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    listing_id: '4',
    user_id: 'u4',
    owner_username: 'hku_dorm',
    title: 'St. Johns College Dorm Offer',
    description: 'Subletting my dorm room for summer semester.',
    image_url: 'https://picsum.photos/seed/room4/800/600',
    rent: 3000,
    location: 'Pok Fu Lam',
    listing_type: 'dorm',
    visibility_status: 'visible',
    save_count: 22,
    created_at: new Date(Date.now() - 259200000).toISOString(),
    updated_at: new Date(Date.now() - 259200000).toISOString(),
  }
];

const Home: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('newest');

  const filteredListings = MOCK_LISTINGS.filter(listing => {
    const matchesSearch = listing.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         listing.location.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'all' || listing.listing_type === selectedType;
    return matchesSearch && matchesType;
  }).sort((a, b) => {
    if (sortBy === 'newest') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    if (sortBy === 'lowest_rent') return a.rent - b.rent;
    if (sortBy === 'highest_rent') return b.rent - a.rent;
    if (sortBy === 'most_saved') return b.save_count - a.save_count;
    return 0;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl"
        >
          Find your perfect <span className="text-indigo-600">Roomie</span> at HKU
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mt-5 max-w-xl mx-auto text-xl text-gray-500"
        >
          The trusted platform for HKU students to find housing, roommates, and dorm offers.
        </motion.p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-200 mb-8">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by location or title..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-400" />
              <select
                className="border border-gray-300 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                <option value="all">All Types</option>
                <option value="apartment">Apartment</option>
                <option value="room">Room</option>
                <option value="dorm">Dorm</option>
                <option value="roommate_request">Roommate Request</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <SlidersHorizontal className="h-5 w-5 text-gray-400" />
              <select
                className="border border-gray-300 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="newest">Newest First</option>
                <option value="lowest_rent">Lowest Rent</option>
                <option value="highest_rent">Highest Rent</option>
                <option value="most_saved">Most Saved</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Listings Grid */}
      {filteredListings.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredListings.map((listing, index) => (
            <motion.div
              key={listing.listing_id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
            >
              <ListingCard listing={listing} />
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900">No listings found</h3>
          <p className="text-gray-500">Try adjusting your search or filters.</p>
        </div>
      )}
    </div>
  );
};

export default Home;
