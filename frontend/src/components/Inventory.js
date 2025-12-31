import React, { useState, useEffect } from 'react';
import { Search, Plus, ShoppingCart, Package, Loader2, AlertCircle, Edit } from 'lucide-react';
import RecordSaleModal from './RecordSaleModal';
import RestockModal from './RestockModal';
import AddProductModal from './AddProductModal';
import EditProductModal from './EditProductModal';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const Inventory = ({ showToast }) => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [saleModalOpen, setSaleModalOpen] = useState(false);
  const [restockModalOpen, setRestockModalOpen] = useState(false);
  const [addProductModalOpen, setAddProductModalOpen] = useState(false);
  const [editProductModalOpen, setEditProductModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, [lowStockOnly]);

  useEffect(() => {
    filterProducts();
  }, [searchQuery, products]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (lowStockOnly) params.append('low_stock_only', 'true');
      const response = await axios.get(`${API_BASE}/products?${params.toString()}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
      showToast('Failed to load products', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filterProducts = () => {
    if (!searchQuery.trim()) {
      setFilteredProducts(products);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = products.filter(
      (product) =>
        product.name.toLowerCase().includes(query) ||
        product.sku.toLowerCase().includes(query)
    );
    setFilteredProducts(filtered);
  };

  const getStockStatus = (product) => {
    if (product.stock_quantity === 0) {
      return { label: 'Out of Stock', color: 'bg-red-100 text-red-800' };
    } else if (product.stock_quantity <= product.min_stock_level) {
      return { label: 'Low Stock', color: 'bg-yellow-100 text-yellow-800' };
    }
    return { label: 'In Stock', color: 'bg-green-100 text-green-800' };
  };

  const handleSaleSuccess = () => {
    fetchProducts();
    setSaleModalOpen(false);
    setSelectedProduct(null);
  };

  const handleRestockSuccess = () => {
    fetchProducts();
    setRestockModalOpen(false);
    setSelectedProduct(null);
  };

  const openSaleModal = (product) => {
    setSelectedProduct(product);
    setSaleModalOpen(true);
  };

  const openRestockModal = (product) => {
    setSelectedProduct(product);
    setRestockModalOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
          <h1 className="text-3xl font-bold text-slate-900 mb-4 md:mb-0">Inventory Management</h1>
          <button
            onClick={() => setAddProductModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            <span>Add Product</span>
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Search by product name or SKU..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => setLowStockOnly(e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-600"
              />
              <span className="text-slate-700 font-medium">Low Stock Only</span>
            </label>
          </div>
        </div>

        {/* Products Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {filteredProducts.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center">
                      <AlertCircle className="mx-auto text-slate-400 mb-2" size={48} />
                      <p className="text-slate-600">No products found</p>
                    </td>
                  </tr>
                ) : (
                  filteredProducts.map((product) => {
                    const status = getStockStatus(product);
                    return (
                      <tr key={product.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-slate-900">{product.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-600">{product.sku}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-600">{product.category_name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-slate-900">
                            ${product.price.toFixed(2)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-600">
                            {product.stock_quantity} / {product.min_stock_level}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded-full ${status.color}`}
                          >
                            {status.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex gap-2">
                            <button
                              onClick={() => openSaleModal(product)}
                              disabled={product.stock_quantity === 0}
                              className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                              title="Record Sale"
                            >
                              <ShoppingCart size={16} />
                              <span className="hidden sm:inline">Sale</span>
                            </button>
                            <button
                              onClick={() => openRestockModal(product)}
                              className="flex items-center gap-1 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                              title="Restock"
                            >
                              <Package size={16} />
                              <span className="hidden sm:inline">Restock</span>
                            </button>
                            <button
                              onClick={() => {
                                setSelectedProduct(product);
                                setEditProductModalOpen(true);
                              }}
                              className="flex items-center gap-1 px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
                              title="Edit Product"
                            >
                              <Edit size={16} />
                              <span className="hidden sm:inline">Edit</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modals */}
      {saleModalOpen && (
        <RecordSaleModal
          product={selectedProduct}
          onClose={() => {
            setSaleModalOpen(false);
            setSelectedProduct(null);
          }}
          onSuccess={handleSaleSuccess}
          showToast={showToast}
        />
      )}

      {restockModalOpen && (
        <RestockModal
          product={selectedProduct}
          onClose={() => {
            setRestockModalOpen(false);
            setSelectedProduct(null);
          }}
          onSuccess={handleRestockSuccess}
          showToast={showToast}
        />
      )}

      {addProductModalOpen && (
        <AddProductModal
          onClose={() => setAddProductModalOpen(false)}
          onSuccess={() => {
            fetchProducts();
            setAddProductModalOpen(false);
          }}
          showToast={showToast}
        />
      )}

      {editProductModalOpen && (
        <EditProductModal
          product={selectedProduct}
          onClose={() => {
            setEditProductModalOpen(false);
            setSelectedProduct(null);
          }}
          onSuccess={() => {
            fetchProducts();
            setEditProductModalOpen(false);
            setSelectedProduct(null);
          }}
          showToast={showToast}
        />
      )}
    </div>
  );
};

export default Inventory;

