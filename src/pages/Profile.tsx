import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { ListingCard } from '../components/ListingCard';
import { Listing } from '../types';
import { User, Settings, Bookmark, Grid } from 'lucide-react';
import { motion } from 'motion/react';

// Mock User Data
const MOCK_USER = {
  user_id: 'u1',
  username: 'alex_hku',
  email: 'alex@connect.hku.hk',
  bio: 'Computer Science student at HKU. Looking for a quiet place near campus.',
  role: 'user',
  status: 'active',
  created_at: new Date(Date.now() - 31536000000).toISOString(),
};

// Mock Listings Data
const MOCK_MY_LISTINGS: Listing[] = [
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
  }
];

const MOCK_SAVED_LISTINGS: Listing[] = [
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
  }
];

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'my_listings' | 'saved_listings'>('my_listings');
  const [isEditing, setIsEditing] = useState(false);
  const [editBio, setEditBio] = useState(MOCK_USER.bio);

  const handleSaveProfile = () => {
    // API Call to update profile would go here
    setIsEditing(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Profile Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-8">
        <div className="h-32 bg-indigo-600"></div>
        <div className="px-6 py-6 sm:px-8 sm:flex sm:items-end sm:space-x-5 -mt-16">
          <div className="relative h-24 w-24 rounded-full ring-4 ring-white bg-white sm:h-32 sm:w-32 flex-shrink-0">
            <div className="h-full w-full rounded-full bg-gray-200 flex items-center justify-center">
              <User className="h-12 w-12 text-gray-500" />
            </div>
          </div>
          <div className="mt-6 sm:flex-1 sm:min-w-0 sm:flex sm:items-center sm:justify-end sm:space-x-6 sm:pb-1">
            <div className="sm:hidden md:block mt-6 min-w-0 flex-1">
              <h1 className="text-2xl font-bold text-gray-900 truncate">
                {user?.username || MOCK_USER.username}
              </h1>
              <p className="text-sm font-medium text-gray-500">
                {MOCK_USER.email} • Joined {new Date(MOCK_USER.created_at).getFullYear()}
              </p>
            </div>
            <div className="mt-6 flex flex-col justify-stretch space-y-3 sm:flex-row sm:space-y-0 sm:space-x-4">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="inline-flex justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Settings className="-ml-1 mr-2 h-5 w-5 text-gray-400" aria-hidden="true" />
                {isEditing ? 'Cancel Edit' : 'Edit Profile'}
              </button>
            </div>
          </div>
        </div>
        
        {/* Bio Section */}
        <div className="px-6 py-4 sm:px-8 border-t border-gray-200 bg-gray-50">
          {isEditing ? (
            <div className="space-y-4 max-w-2xl">
              <div>
                <label htmlFor="bio" className="block text-sm font-medium text-gray-700">Bio</label>
                <div className="mt-1">
                  <textarea
                    id="bio"
                    name="bio"
                    rows={3}
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2"
                    value={editBio}
                    onChange={(e) => setEditBio(e.target.value)}
                  />
                </div>
                <p className="mt-2 text-sm text-gray-500">Brief description for your profile. URLs are hyperlinked.</p>
              </div>
              <div className="flex justify-end">
                <button
                  onClick={handleSaveProfile}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Save Changes
                </button>
              </div>
            </div>
          ) : (
            <div className="max-w-2xl text-sm text-gray-700">
              {editBio || 'No bio provided.'}
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('my_listings')}
            className={`${
              activeTab === 'my_listings'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
          >
            <Grid className="h-4 w-4" />
            My Listings ({MOCK_MY_LISTINGS.length})
          </button>
          <button
            onClick={() => setActiveTab('saved_listings')}
            className={`${
              activeTab === 'saved_listings'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
          >
            <Bookmark className="h-4 w-4" />
            Saved Listings ({MOCK_SAVED_LISTINGS.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 'my_listings' && (
          <div>
            {MOCK_MY_LISTINGS.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {MOCK_MY_LISTINGS.map((listing) => (
                  <ListingCard key={listing.listing_id} listing={listing} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <Grid className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No listings</h3>
                <p className="mt-1 text-sm text-gray-500">You haven't created any listings yet.</p>
                <div className="mt-6">
                  <button
                    type="button"
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Create a Listing
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'saved_listings' && (
          <div>
            {MOCK_SAVED_LISTINGS.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {MOCK_SAVED_LISTINGS.map((listing) => (
                  <ListingCard key={listing.listing_id} listing={listing} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <Bookmark className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No saved listings</h3>
                <p className="mt-1 text-sm text-gray-500">You haven't saved any listings yet.</p>
              </div>
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Profile;
