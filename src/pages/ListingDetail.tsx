import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { MapPin, Calendar, User, Heart, Trash2, Edit2, MessageSquare } from 'lucide-react';
import { motion } from 'motion/react';
import { Listing, Comment } from '../types';

// Mock Listing Data
const MOCK_LISTING: Listing = {
  listing_id: '1',
  user_id: 'u1',
  owner_username: 'alex_hku',
  title: 'Cozy Room in Kennedy Town',
  description: 'Looking for a clean and tidy roommate. 5 mins walk to MTR. The room comes fully furnished with a bed, desk, and wardrobe. Shared kitchen and bathroom. Rent includes high-speed WiFi but utilities are split evenly. Building has 24/7 security and a small gym. Available starting next month. Preferably a student or young professional.',
  image_url: 'https://picsum.photos/seed/room1/1200/800',
  rent: 8500,
  location: 'Kennedy Town',
  listing_type: 'room',
  visibility_status: 'visible',
  save_count: 12,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// Mock Comments
const MOCK_COMMENTS: Comment[] = [
  {
    comment_id: 'c1',
    listing_id: '1',
    user_id: 'u2',
    username: 'sarah_lee',
    content: 'Is the rent negotiable?',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    comment_id: 'c2',
    listing_id: '1',
    user_id: 'u3',
    username: 'jason_w',
    content: 'Are pets allowed in the apartment?',
    created_at: new Date(Date.now() - 43200000).toISOString(),
  }
];

const ListingDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, user, isAdmin } = useAuth();
  
  const [listing, setListing] = useState<Listing | null>(MOCK_LISTING);
  const [comments, setComments] = useState<Comment[]>(MOCK_COMMENTS);
  const [isSaved, setIsSaved] = useState(false);
  const [newComment, setNewComment] = useState('');

  // Handle Save
  const handleSaveToggle = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setIsSaved(!isSaved);
    if (listing) {
      setListing({
        ...listing,
        save_count: isSaved ? listing.save_count - 1 : listing.save_count + 1
      });
    }
  };

  // Handle Add Comment
  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !user) return;
    
    const comment: Comment = {
      comment_id: `c${Date.now()}`,
      listing_id: id || '1',
      user_id: user.user_id,
      username: user.username,
      content: newComment.trim(),
      created_at: new Date().toISOString(),
    };
    
    setComments([comment, ...comments]);
    setNewComment('');
  };

  // Handle Delete Comment
  const handleDeleteComment = (commentId: string) => {
    setComments(comments.filter(c => c.comment_id !== commentId));
  };

  // Handle Delete Listing
  const handleDeleteListing = () => {
    if (window.confirm('Are you sure you want to delete this listing?')) {
      // API call to delete listing would go here
      navigate('/');
    }
  };

  if (!listing) return <div className="text-center py-20">Listing not found.</div>;

  const isOwner = user?.user_id === listing.user_id;
  const canEditOrDelete = isOwner || isAdmin;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Listing Header */}
      <div className="mb-6 flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold text-gray-900"
          >
            {listing.title}
          </motion.h1>
          <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              {listing.location}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Posted {new Date(listing.created_at).toLocaleDateString()}
            </span>
            <span className="flex items-center gap-1">
              <User className="h-4 w-4" />
              By {listing.owner_username}
            </span>
            <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 capitalize">
              {listing.listing_type.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSaveToggle}
            className={`flex items-center gap-2 px-4 py-2 rounded-md border text-sm font-medium transition-colors ${
              isSaved 
                ? 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100' 
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Heart className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
            {isSaved ? 'Saved' : 'Save'} ({listing.save_count})
          </button>

          {canEditOrDelete && (
            <>
              <Link
                to={`/edit-listing/${listing.listing_id}`}
                className="flex items-center gap-2 px-4 py-2 rounded-md bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <Edit2 className="h-4 w-4" />
                Edit
              </Link>
              <button
                onClick={handleDeleteListing}
                className="flex items-center gap-2 px-4 py-2 rounded-md bg-white border border-red-300 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Image Gallery */}
          <div className="aspect-[16/9] w-full rounded-xl overflow-hidden bg-gray-100">
            <img 
              src={listing.image_url || 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267'} 
              alt={listing.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Description */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Description</h2>
            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
              {listing.description}
            </p>
          </div>

          {/* Comments Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-indigo-600" />
              Comments ({comments.length})
            </h2>

            {/* Comment Form */}
            {isAuthenticated ? (
              <form onSubmit={handleAddComment} className="mb-8">
                <div className="flex gap-4">
                  <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-indigo-600 font-medium text-sm">
                      {user?.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1">
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Add a comment..."
                      className="w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 min-h-[80px]"
                    />
                    <div className="mt-2 flex justify-end">
                      <button
                        type="submit"
                        disabled={!newComment.trim()}
                        className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                      >
                        Post Comment
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            ) : (
              <div className="bg-gray-50 rounded-lg p-4 text-center mb-8 border border-gray-200">
                <p className="text-gray-600 text-sm mb-2">Please login to add a comment.</p>
                <Link to="/login" className="text-indigo-600 hover:text-indigo-500 font-medium text-sm">
                  Login here
                </Link>
              </div>
            )}

            {/* Comments List */}
            <div className="space-y-6">
              {comments.map((comment) => (
                <div key={comment.comment_id} className="flex gap-4">
                  <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <span className="text-gray-600 font-medium text-sm">
                      {comment.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-gray-900 text-sm">{comment.username}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-700 text-sm">{comment.content}</p>
                    </div>
                    {/* Delete Comment Button */}
                    {(user?.user_id === comment.user_id || isAdmin) && (
                      <button 
                        onClick={() => handleDeleteComment(comment.comment_id)}
                        className="mt-1 text-xs text-red-500 hover:text-red-700 font-medium"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {comments.length === 0 && (
                <p className="text-center text-gray-500 text-sm py-4">No comments yet. Be the first to ask a question!</p>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Rent & Action Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
            <div className="text-3xl font-bold text-gray-900 mb-2">
              HK${listing.rent.toLocaleString()} <span className="text-lg text-gray-500 font-normal">/ month</span>
            </div>
            
            <div className="mt-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
                  <User className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Listed by</p>
                  <p className="font-medium text-gray-900">{listing.owner_username}</p>
                </div>
              </div>

              <hr className="border-gray-200" />

              <button className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Contact Owner
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListingDetail;
