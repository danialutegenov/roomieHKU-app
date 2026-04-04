import React from 'react';
import { Link } from 'react-router-dom';
import { Listing } from '../types';
import { MapPin, DollarSign, Clock, Heart } from 'lucide-react';

interface ListingCardProps {
  listing: Listing;
}

export const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group">
      <Link to={`/listing/${listing.listing_id}`}>
        <div className="relative h-48 bg-gray-100">
          {listing.image_url ? (
            <img 
              src={listing.image_url} 
              alt={listing.title} 
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-xs font-semibold text-indigo-600 shadow-sm capitalize">
            {listing.listing_type.replace('_', ' ')}
          </div>
        </div>
        <div className="p-5">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-bold text-gray-900 line-clamp-1 group-hover:text-indigo-600 transition-colors">
              {listing.title}
            </h3>
          </div>
          
          <div className="space-y-2 mb-4">
            <div className="flex items-center text-sm text-gray-500">
              <MapPin className="h-4 w-4 mr-1 text-gray-400" />
              {listing.location}
            </div>
            <div className="flex items-center text-sm font-semibold text-gray-900">
              <DollarSign className="h-4 w-4 mr-1 text-indigo-500" />
              {listing.rent} / month
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex items-center text-xs text-gray-400">
              <Clock className="h-3 w-3 mr-1" />
              {new Date(listing.created_at).toLocaleDateString()}
            </div>
            <div className="flex items-center text-xs font-medium text-gray-500">
              <Heart className="h-3 w-3 mr-1 text-pink-500" />
              {listing.save_count} saves
            </div>
          </div>
          
          <div className="mt-3 text-xs text-gray-400 italic">
            Posted by @{listing.owner_username}
          </div>
        </div>
      </Link>
    </div>
  );
};
