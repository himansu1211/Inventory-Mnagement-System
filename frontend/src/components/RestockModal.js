import React, { useState } from 'react';
import { X, Package, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const RestockModal = ({ product, onClose, onSuccess, showToast }) => {
  const [quantity, setQuantity] = useState(10);
  const [reason, setReason] = useState('Manual restock');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/restock`, {
        product_id: product.id,
        quantity: parseInt(quantity),
        reason: reason.trim() || 'Manual restock',
      });

      showToast(response.data.message || 'Product restocked successfully', 'success');
      onSuccess();
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Failed to restock product. Please try again.';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!product) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Package className="text-green-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-slate-900">Restock Product</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">Product</label>
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="font-medium text-slate-900">{product.name}</p>
              <p className="text-sm text-slate-600">SKU: {product.sku}</p>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Current Stock
            </label>
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="text-lg font-semibold text-slate-900">
                {product.stock_quantity} units
              </p>
            </div>
          </div>

          <div className="mb-4">
            <label htmlFor="quantity" className="block text-sm font-medium text-slate-700 mb-2">
              Quantity to Add
            </label>
            <input
              type="number"
              id="quantity"
              min="1"
              value={quantity}
              onChange={(e) => {
                const val = parseInt(e.target.value) || 0;
                if (val >= 1) {
                  setQuantity(val);
                  setError('');
                }
              }}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-600"
              required
            />
          </div>

          <div className="mb-4">
            <label htmlFor="reason" className="block text-sm font-medium text-slate-700 mb-2">
              Reason (Optional)
            </label>
            <input
              type="text"
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., Restock from supplier"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-600"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">New Stock Level</label>
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-xl font-bold text-green-600">
                {product.stock_quantity + parseInt(quantity || 0)} units
              </p>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </>
              ) : (
                'Restock'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RestockModal;

