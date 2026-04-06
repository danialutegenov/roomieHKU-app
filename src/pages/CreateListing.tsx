import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'motion/react';
import { ListingType } from '../types';
import { Building2, MapPin, DollarSign, Image as ImageIcon, FileText, Type } from 'lucide-react';

interface ListingForm {
  title: string;
  description: string;
  image_url: string;
  rent: string;
  location: string;
  listing_type: ListingType;
}

const initialForm: ListingForm = {
  title: '',
  description: '',
  image_url: '',
  rent: '',
  location: '',
  listing_type: 'room',
};

const CreateListing: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>(); // If there's an ID, it means edit mode
  const isEditMode = Boolean(id);

  const [form, setForm] = useState<ListingForm>(initialForm);
  const [errors, setErrors] = useState<Partial<ListingForm>>({});

  useEffect(() => {
    if (isEditMode) {
      // Mock fetch existing data
      setForm({
        title: 'Cozy Room in Kennedy Town',
        description: 'Looking for a clean and tidy roommate. 5 mins walk to MTR.',
        image_url: 'https://picsum.photos/seed/room1/800/600',
        rent: '8500',
        location: 'Kennedy Town',
        listing_type: 'room',
      });
    }
  }, [isEditMode, id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    // Clear error
    if (errors[name as keyof ListingForm]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors: Partial<ListingForm> = {};
    if (!form.title.trim()) newErrors.title = 'Title is required';
    if (!form.description.trim()) newErrors.description = 'Description is required';
    if (!form.rent || isNaN(Number(form.rent)) || Number(form.rent) < 0) newErrors.rent = 'Rent must be a valid positive number';
    if (!form.location.trim()) newErrors.location = 'Location is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    // Simulate API Call
    console.log('Submitting listing data:', form);
    
    // Redirect to home or listing detail
    navigate('/');
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden"
      >
        <div className="px-6 py-8 sm:p-10">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">
              {isEditMode ? 'Edit Listing' : 'Create a New Listing'}
            </h1>
            <p className="mt-2 text-sm text-gray-500">
              {isEditMode 
                ? 'Update the details of your listing below.' 
                : 'Fill out the details below to post your housing or roommate request.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title <span className="text-red-500">*</span>
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Type className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="title"
                  id="title"
                  className={`block w-full pl-10 sm:text-sm rounded-md p-2.5 border ${
                    errors.title ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                  placeholder="e.g. Cozy Room near HKU Main Campus"
                  value={form.title}
                  onChange={handleChange}
                />
              </div>
              {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
            </div>

            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
              {/* Type */}
              <div>
                <label htmlFor="listing_type" className="block text-sm font-medium text-gray-700">
                  Listing Type <span className="text-red-500">*</span>
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Building2 className="h-5 w-5 text-gray-400" />
                  </div>
                  <select
                    id="listing_type"
                    name="listing_type"
                    className="block w-full pl-10 sm:text-sm rounded-md p-2.5 border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                    value={form.listing_type}
                    onChange={handleChange}
                  >
                    <option value="apartment">Apartment</option>
                    <option value="room">Room</option>
                    <option value="dorm">Dorm</option>
                    <option value="roommate_request">Roommate Request</option>
                  </select>
                </div>
              </div>

              {/* Rent */}
              <div>
                <label htmlFor="rent" className="block text-sm font-medium text-gray-700">
                  Rent (HKD / month) <span className="text-red-500">*</span>
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <DollarSign className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    name="rent"
                    id="rent"
                    className={`block w-full pl-10 sm:text-sm rounded-md p-2.5 border ${
                      errors.rent ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                    }`}
                    placeholder="e.g. 5000"
                    value={form.rent}
                    onChange={handleChange}
                  />
                </div>
                {errors.rent && <p className="mt-1 text-sm text-red-600">{errors.rent}</p>}
              </div>
            </div>

            {/* Location */}
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                Location <span className="text-red-500">*</span>
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MapPin className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="location"
                  id="location"
                  className={`block w-full pl-10 sm:text-sm rounded-md p-2.5 border ${
                    errors.location ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                  placeholder="e.g. Kennedy Town, Sai Ying Pun"
                  value={form.location}
                  onChange={handleChange}
                />
              </div>
              {errors.location && <p className="mt-1 text-sm text-red-600">{errors.location}</p>}
            </div>

            {/* Image URL */}
            <div>
              <label htmlFor="image_url" className="block text-sm font-medium text-gray-700">
                Image URL (Optional)
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <ImageIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="image_url"
                  id="image_url"
                  className="block w-full pl-10 sm:text-sm rounded-md p-2.5 border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="https://example.com/image.jpg"
                  value={form.image_url}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description <span className="text-red-500">*</span>
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute top-3 left-3 flex items-start pointer-events-none">
                  <FileText className="h-5 w-5 text-gray-400" />
                </div>
                <textarea
                  name="description"
                  id="description"
                  rows={5}
                  className={`block w-full pl-10 sm:text-sm rounded-md p-2.5 border ${
                    errors.description ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                  placeholder="Provide more details about the listing..."
                  value={form.description}
                  onChange={handleChange}
                />
              </div>
              {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
            </div>

            <div className="pt-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                {isEditMode ? 'Update Listing' : 'Post Listing'}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default CreateListing;
