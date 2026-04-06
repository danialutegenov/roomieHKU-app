import React, { useState } from 'react';
import { Comment } from '../types';
import { Search, Trash2, ExternalLink, MessageSquare } from 'lucide-react';
import { motion } from 'motion/react';
import { Link } from 'react-router-dom';

interface AdminComment extends Comment {
  listing_title: string;
}

const MOCK_COMMENTS: AdminComment[] = [
  {
    comment_id: 'c1',
    listing_id: '1',
    listing_title: 'Cozy Room in Kennedy Town',
    user_id: 'u2',
    username: 'sarah_lee',
    content: 'Is the rent negotiable? I am very interested but my budget is slightly lower.',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    comment_id: 'c2',
    listing_id: '1',
    listing_title: 'Cozy Room in Kennedy Town',
    user_id: 'u3',
    username: 'jason_w',
    content: 'Are pets allowed in the apartment?',
    created_at: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    comment_id: 'c3',
    listing_id: '2',
    listing_title: 'Modern 2BR Flat near HKU',
    user_id: 'u4',
    username: 'hku_dorm',
    content: 'Spam comment here, buy cheap stuff at http://spam.com',
    created_at: new Date(Date.now() - 10000000).toISOString(),
  }
];

const AdminCommentManagement: React.FC = () => {
  const [comments, setComments] = useState<AdminComment[]>(MOCK_COMMENTS);
  const [searchQuery, setSearchQuery] = useState('');

  const deleteComment = (commentId: string) => {
    if (window.confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
      setComments(comments.filter(c => c.comment_id !== commentId));
    }
  };

  const filteredComments = comments.filter(comment => 
    comment.content.toLowerCase().includes(searchQuery.toLowerCase()) || 
    comment.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    comment.listing_title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Comment Management</h1>
          <p className="text-gray-500 text-sm">Review and moderate user comments across all listings.</p>
        </div>
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search comments..."
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
              <tr className="border-b border-gray-200 bg-gray-50/50">
                <th className="py-4 px-6 font-semibold text-sm text-gray-600">Author</th>
                <th className="py-4 px-6 font-semibold text-sm text-gray-600">Comment Content</th>
                <th className="py-4 px-6 font-semibold text-sm text-gray-600">Listing Reference</th>
                <th className="py-4 px-6 font-semibold text-sm text-gray-600">Date</th>
                <th className="py-4 px-6 font-semibold text-sm text-gray-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredComments.map((comment) => (
                <motion.tr 
                  key={comment.comment_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="hover:bg-gray-50/50 transition-colors"
                >
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                        <span className="text-indigo-600 font-medium text-xs">
                          {comment.username.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">{comment.username}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-start gap-2 max-w-md">
                      <MessageSquare className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-gray-700 line-clamp-2">{comment.content}</p>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <Link 
                      to={`/listing/${comment.listing_id}`}
                      className="text-sm text-indigo-600 hover:text-indigo-900 flex items-center gap-1 font-medium group"
                    >
                      <span className="truncate max-w-[200px]">{comment.listing_title}</span>
                      <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  </td>
                  <td className="py-4 px-6">
                    <span className="text-sm text-gray-500 whitespace-nowrap">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => deleteComment(comment.comment_id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete Comment"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
              {filteredComments.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500 text-sm">
                    No comments found matching your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminCommentManagement;
