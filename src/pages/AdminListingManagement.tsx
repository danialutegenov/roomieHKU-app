import React, { useState } from 'react';
import { Listing } from '../types';
import { Search, Eye, EyeOff, Trash2, ExternalLink, MapPin, DollarSign } from 'lucide-react';
import { motion } from 'motion/react';

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
    created_at: '2024-03-20',
    updated_at: '2024-03-20',
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
    created_at: '2024-03-25',
    updated_at: '2024-03-25',
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
    visibility_status: 'hidden',
    save_count: 8,
    created_at: '2024-03-28',
    updated_at: '2024-03-28',
  }
];

const AdminListingManagement: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>(MOCK_LISTINGS);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleVisibility = (listingId: string) => {
    setListings(listings.map(listing => {
      if (listing.listing_id === listingId) {
        return { ...listing, visibility_status: listing.visibility_status === 'visible' ? 'hidden' : 'visible' };
      }
      return listing;
    }));
  };

  const deleteListing = (listingId: string) => {
    if (window.confirm('Are you sure you want to delete this listing? This action cannot be undone.')) {
      setListings(listings.filter(l => l.listing_id !== listingId));
    }
  };

  const filteredListings = listings.filter(listing => 
    listing.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    listing.owner_username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Listing Management</h1>
          <p className="text-gray-500 text-sm">Moderate housing and roommate listings across the platform.</p>
        </div>
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search listings..."
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
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Listing</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Rent</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredListings.map((listing) => (
                <tr key={listing.listing_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="h-12 w-16 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0">
                        {listing.image_url ? (
                          <img src={listing.image_url} alt="" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-[10px] text-gray-400">No Img</div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-bold text-gray-900 line-clamp-1">{listing.title}</div>
                        <div className="flex items-center text-xs text-gray-500">
                          <MapPin className="h-3 w-3 mr-1" /> {listing.location}
                          <span className="mx-2">•</span>
                          by @{listing.owner_username}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                      {listing.listing_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center text-sm font-semibold text-gray-900">
                      <DollarSign className="h-3.5 w-3.5 text-indigo-500" />
                      {listing.rent}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={cn(
                      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                      listing.visibility_status === 'visible' ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                    )}>
                      {listing.visibility_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => toggleVisibility(listing.listing_id)}
                        className={cn(
                          "p-2 rounded-lg transition-colors",
                          listing.visibility_status === 'visible' ? "text-yellow-600 hover:bg-yellow-50" : "text-green-600 hover:bg-green-50"
                        )}
                        title={listing.visibility_status === 'visible' ? "Hide listing" : "Show listing"}
                      >
                        {listing.visibility_status === 'visible' ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={() => deleteListing(listing.listing_id)}
                        className="p-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                        title="Delete listing"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                      <button className="p-2 rounded-lg text-indigo-600 hover:bg-indigo-50 transition-colors" title="View details">
                        <ExternalLink className="h-4 w-4" />
                      </button>
                    </div>
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

// Helper function for cn
function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ');
}

export default AdminListingManagement;
