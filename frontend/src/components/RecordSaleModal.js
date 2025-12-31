import React, { useState } from 'react';
import { X, ShoppingCart, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const RecordSaleModal = ({ product, onClose, onSuccess, showToast }) => {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const maxQuantity = product?.stock_quantity || 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }

    if (quantity > maxQuantity) {
      setError(`Cannot sell more than available stock (${maxQuantity})`);
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/add-sale`, {
        product_id: product.id,
        quantity: parseInt(quantity),
      });

      showToast(response.data.message || 'Sale recorded successfully', 'success');
      onSuccess();
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Failed to record sale. Please try again.';
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
            <div className="p-2 bg-blue-100 rounded-lg">
              <ShoppingCart className="text-blue-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-slate-900">Record Sale</h2>
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
              Available Stock
            </label>
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="text-lg font-semibold text-slate-900">{maxQuantity} units</p>
            </div>
          </div>

          <div className="mb-4">
            <label htmlFor="quantity" className="block text-sm font-medium text-slate-700 mb-2">
              Quantity to Sell
            </label>
            <input
              type="number"
              id="quantity"
              min="1"
              max={maxQuantity}
              value={quantity}
              onChange={(e) => {
                const val = parseInt(e.target.value) || 0;
                if (val >= 1 && val <= maxQuantity) {
                  setQuantity(val);
                  setError('');
                }
              }}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              Maximum: {maxQuantity} units
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">Total Price</label>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-xl font-bold text-blue-600">
                ${(product.price * quantity).toFixed(2)}
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
              disabled={loading || maxQuantity === 0}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </>
              ) : (
                'Record Sale'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RecordSaleModal;

