export type UserRole = 'user' | 'admin';
export type UserStatus = 'active' | 'suspended';
export type ListingType = 'apartment' | 'room' | 'dorm' | 'roommate_request';
export type VisibilityStatus = 'visible' | 'hidden' | 'closed';

export interface User {
  user_id: string;
  username: string;
  email: string;
  bio?: string;
  profile_picture_url?: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
}

export interface Listing {
  listing_id: string;
  user_id: string;
  owner_username: string;
  title: string;
  description: string;
  image_url?: string;
  rent: number;
  location: string;
  listing_type: ListingType;
  visibility_status: VisibilityStatus;
  save_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  comment_id: string;
  listing_id: string;
  user_id: string;
  username: string;
  content: string;
  created_at: string;
}

export interface AnalyticsData {
  total_users: number;
  total_listings: number;
  total_comments: number;
  most_saved_listings: Listing[];
  most_active_users: User[];
}
