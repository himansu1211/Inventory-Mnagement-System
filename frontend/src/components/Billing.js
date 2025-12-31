import React, { useState, useEffect } from 'react';
import { Search, Plus, Receipt, Printer, Download, Loader2, Trash2, X } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const Billing = ({ showToast }) => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [billItems, setBillItems] = useState([]);
  const [billNumber, setBillNumber] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchProducts();
    generateBillNumber();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [searchQuery, products]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/products`);
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

  const generateBillNumber = () => {
    const date = new Date();
    const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    setBillNumber(`BILL-${dateStr}-${random}`);
  };

  const addToBill = (product) => {
    const existingItem = billItems.find(item => item.id === product.id);
    if (existingItem) {
      updateQuantity(product.id, existingItem.quantity + 1);
    } else {
      setBillItems([...billItems, { ...product, quantity: 1 }]);
    }
    setSearchQuery('');
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromBill(productId);
      return;
    }

    const product = products.find(p => p.id === productId);
    if (newQuantity > product.stock_quantity) {
      showToast(`Cannot add more than available stock (${product.stock_quantity})`, 'error');
      return;
    }

    setBillItems(billItems.map(item =>
      item.id === productId ? { ...item, quantity: newQuantity } : item
    ));
  };

  const removeFromBill = (productId) => {
    setBillItems(billItems.filter(item => item.id !== productId));
  };

  const getTotal = () => {
    return billItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const generateBill = async () => {
    if (billItems.length === 0) {
      showToast('Please add items to the bill', 'error');
      return;
    }

    try {
      setProcessing(true);
      const promises = billItems.map(item =>
        axios.post(`${API_BASE}/add-sale`, {
          product_id: item.id,
          quantity: item.quantity,
        })
      );

      await Promise.all(promises);

      showToast('Bill generated successfully', 'success');

      // Reset bill
      setBillItems([]);
      setCustomerName('');
      generateBillNumber();
    } catch (error) {
      console.error('Error generating bill:', error);
      showToast('Failed to generate bill', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const printBill = () => {
    const printWindow = window.open('', '_blank');
    const billDate = new Date().toLocaleDateString();

    const billHTML = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Bill - ${billNumber}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .bill-info { margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .total { font-weight: bold; font-size: 18px; text-align: right; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Smart-IMS Bill</h1>
          </div>
          <div class="bill-info">
            <p><strong>Bill Number:</strong> ${billNumber}</p>
            <p><strong>Date:</strong> ${billDate}</p>
            ${customerName ? `<p><strong>Customer:</strong> ${customerName}</p>` : ''}
          </div>
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              ${billItems.map(item => `
                <tr>
                  <td>${item.name}</td>
                  <td>${item.sku}</td>
                  <td>${item.quantity}</td>
                  <td>$${item.price.toFixed(2)}</td>
                  <td>$${(item.price * item.quantity).toFixed(2)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          <div class="total">
            <p>Total: $${getTotal().toFixed(2)}</p>
          </div>
        </body>
      </html>
    `;

    printWindow.document.write(billHTML);
    printWindow.document.close();
    printWindow.print();
  };

  const saveAsImage = () => {
    showToast('Save as image feature coming soon', 'info');
  };

  const saveAsPDF = () => {
    showToast('Save as PDF feature coming soon', 'info');
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
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-4 md:mb-0">Billing</h1>
          <div className="flex gap-2">
            <button
              onClick={printBill}
              disabled={billItems.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
            >
              <Printer size={20} />
              <span>Print Bill</span>
            </button>
            <button
              onClick={saveAsImage}
              disabled={billItems.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={20} />
              <span>Save as Image</span>
            </button>
            <button
              onClick={saveAsPDF}
              disabled={billItems.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={20} />
              <span>Save as PDF</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Product Search and Selection */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Add Products</h2>

            {/* Search */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Search by product name or SKU..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            {/* Product List */}
            <div className="max-h-96 overflow-y-auto">
              {filteredProducts.length === 0 ? (
                <p className="text-center text-slate-500 py-4">No products found</p>
              ) : (
                filteredProducts.map((product) => (
                  <div key={product.id} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg mb-2">
                    <div>
                      <p className="font-medium text-slate-900">{product.name}</p>
                      <p className="text-sm text-slate-600">SKU: {product.sku}</p>
                      <p className="text-sm font-medium text-slate-900">${product.price.toFixed(2)}</p>
                    </div>
                    <button
                      onClick={() => addToBill(product)}
                      disabled={product.stock_quantity === 0}
                      className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                    >
                      <Plus size={16} />
                      <span>Add</span>
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Bill Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Bill Summary</h2>

            {/* Bill Info */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">Bill Number</label>
              <input
                type="text"
                value={billNumber}
                readOnly
                className="w-full px-4 py-2 border border-slate-300 rounded-lg bg-slate-50"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">Customer Name (Optional)</label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                placeholder="Enter customer name"
              />
            </div>

            {/* Bill Items */}
            <div className="mb-4">
              <h3 className="text-lg font-medium text-slate-900 mb-2">Items</h3>
              {billItems.length === 0 ? (
                <p className="text-slate-500">No items added yet</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {billItems.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-slate-900">{item.name}</p>
                        <p className="text-sm text-slate-600">${item.price.toFixed(2)} each</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="px-2 py-1 bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
                        >
                          -
                        </button>
                        <span className="px-2 py-1 bg-white border border-slate-300 rounded">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="px-2 py-1 bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
                        >
                          +
                        </button>
                        <button
                          onClick={() => removeFromBill(item.id)}
                          className="p-1 text-red-600 hover:text-red-800"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Total */}
            <div className="border-t border-slate-200 pt-4 mb-4">
              <div className="flex justify-between items-center text-xl font-bold text-slate-900">
                <span>Total:</span>
                <span>${getTotal().toFixed(2)}</span>
              </div>
            </div>

            {/* Generate Bill Button */}
            <button
              onClick={generateBill}
              disabled={billItems.length === 0 || processing}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
            >
              {processing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Receipt size={20} />
                  <span>Generate Bill</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Billing;
