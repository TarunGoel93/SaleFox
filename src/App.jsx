import { useState, useMemo, useEffect } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import ProductCard from "./components/ProductCard";
import Sidebar from "./components/Sidebar";
import WishlistPage from "./components/WishlistPage";
import ScraperDropdown from "./components/ScraperDropdown";
import BigSearchBar from "./components/BigSearchBar";
import SamsungBulkBotModal from "./components/SamsungBulkBotModal";
import { SCRAPERS_CONFIG } from "./services/scrapersConfig.js";
import {
  parseSmartQuery,
  filterProducts,
  getSearchHistory,
  saveSearchQuery,
  deleteHistoryItem,
  clearAllHistory,
  parsePriceNumber,
  parseRatingNumber,
  getInitialAllProducts,
  searchAcrossAll12Scrapers,
  checkAllScrapersHealth,
} from "./services/searchService.js";

// Base catalog featuring Flipkart smartphone inventory
// (Amazon products are sourced exclusively from the Amazon scraper files)
const ALL_CATALOG_PRODUCTS = [
  {
    id: "p1",
    name: "Apple iPhone 15 (Blue, 128 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15.jpg",
    price: "₹65,999",
    originalPrice: "₹79,900",
    discount: "17% off",
    rating: "4.6/5",
    delivery: "Free Delivery by Tomorrow",
    seller: "SuperComNet",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Apple",
    inStock: true,
    channel: "flipkart",
  },
  {
    id: "p3",
    name: "Samsung Galaxy S23 5G (Green, 128 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s23-5g.jpg",
    price: "₹46,999",
    originalPrice: "₹74,999",
    discount: "37% off",
    rating: "4.5/5",
    delivery: "Free Delivery in 2 Days",
    seller: "RetailNet",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Samsung",
    inStock: true,
    channel: "flipkart",
  },
  {
    id: "p6",
    name: "Google Pixel 8 (Hazel, 128 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/google-pixel-8.jpg",
    price: "₹61,999",
    originalPrice: "₹75,999",
    discount: "18% off",
    rating: "4.4/5",
    delivery: "Free Delivery by Tomorrow",
    seller: "Flashtech Retail",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Google",
    inStock: true,
    channel: "flipkart",
  },
  {
    id: "p8",
    name: "Motorola Edge 50 Pro (Luxe Lavender, 256 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/motorola-edge-50-pro.jpg",
    price: "₹29,999",
    originalPrice: "₹36,999",
    discount: "18% off",
    rating: "4.3/5",
    delivery: "Free Delivery in 2 Days",
    seller: "OmniTech Hub",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Motorola",
    inStock: true,
    channel: "flipkart",
  },
  {
    id: "p9",
    name: "Nothing Phone (2a) 5G (Black, 128 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/nothing-phone-2a.jpg",
    price: "₹23,999",
    originalPrice: "₹25,999",
    discount: "7% off",
    rating: "4.4/5",
    delivery: "Free Delivery",
    seller: "SuperComNet",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Nothing",
    inStock: true,
    channel: "flipkart",
  },
  {
    id: "p10",
    name: "Realme 12 Pro+ 5G (Submarine Blue, 256 GB)",
    image: "https://fdn2.gsmarena.com/vv/bigpic/realme-12-pro-plus.jpg",
    price: "₹28,999",
    originalPrice: "₹34,999",
    discount: "17% off",
    rating: "4.3/5",
    delivery: "Free Delivery",
    seller: "GadgetDeals India",
    badge: "Flipkart Assured",
    badgeType: "flipkart",
    brand: "Realme",
    inStock: true,
    channel: "flipkart",
  },
];

const INITIAL_FILTERS = {
  minPrice: "",
  maxPrice: "",
  minRating: "",
  inStockOnly: false,
  primeOnly: false,
  brand: "",
  sortBy: "relevance",
};

function App() {
  const [activeTab, setActiveTab] = useState("All Products");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [executedQuery, setExecutedQuery] = useState("");
  const [searchHistory, setSearchHistory] = useState(() => getSearchHistory());
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [activeCategory, setActiveCategory] = useState("All products");

  // Multi-Scraper Platform Selection (Default to "All 12 Stores")
  const [selectedPlatform, setSelectedPlatform] = useState("All 12 Stores");

  // Global Unified Products Pool (pre-cached products + live scraped results)
  const [allProductsPool, setAllProductsPool] = useState(() => getInitialAllProducts());
  const [liveSearchResults, setLiveSearchResults] = useState([]);
  const [isScrapingLive, setIsScrapingLive] = useState(false);
  const [scraperStatuses, setScraperStatuses] = useState({});
  const [scraperError, setScraperError] = useState("");
  const [bulkBotProduct, setBulkBotProduct] = useState(null);

  // Check health of all 12 scrapers on mount
  useEffect(() => {
    checkAllScrapersHealth().then((healthMap) => {
      const initialStatus = {};
      SCRAPERS_CONFIG.forEach((s) => {
        initialStatus[s.id] = {
          name: s.name,
          color: s.color,
          status: healthMap[s.id] ? "completed" : "idle",
          count: 0,
          message: healthMap[s.id] ? `${s.name} Online` : `${s.name} Standby`,
        };
      });
      setScraperStatuses(initialStatus);
    });
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  // Approach 1: Frontend Parallel Fan-Out (Promise.allSettled) with Progressive Streaming
  const handleSearchSubmit = async (queryToRun) => {
    const q = (queryToRun !== undefined ? queryToRun : searchQuery).trim();
    if (!q) {
      setExecutedQuery("");
      return;
    }

    setExecutedQuery(q);
    setSearchQuery(q);
    setActiveTab("All Products");
    setScraperError("");
    setLiveSearchResults([]);

    // Save to localStorage history
    const updatedHistory = saveSearchQuery(q, filters);
    setSearchHistory(updatedHistory);

    setIsScrapingLive(true);

    try {
      await searchAcrossAll12Scrapers(
        q,
        filters,
        // Individual scraper status updates (connecting, scraping, completed, offline)
        (scraperId, statusData) => {
          setScraperStatuses((prev) => ({
            ...prev,
            [scraperId]: { ...prev[scraperId], ...statusData },
          }));
        },
        // Progressive streaming: As soon as scraper returns, batch is rendered immediately!
        (newBatch) => {
          setLiveSearchResults((prev) => {
            const map = new Map();
            prev.forEach((item) => map.set(item.id, item));
            newBatch.forEach((item) => map.set(item.id, item));
            return Array.from(map.values());
          });

          setAllProductsPool((prev) => {
            const map = new Map();
            prev.forEach((item) => map.set(item.id, item));
            newBatch.forEach((item) => map.set(item.id, item));
            return Array.from(map.values());
          });
        }
      );
    } catch (err) {
      console.warn("Global multi-scraper execution error:", err);
      setScraperError(err.message || "Failed to query live scrapers.");
    } finally {
      setIsScrapingLive(false);
    }
  };

  // Delete individual item from history
  const handleDeleteHistoryItem = (id) => {
    const updated = deleteHistoryItem(id);
    setSearchHistory(updated);
  };

  // Clear all search history
  const handleClearHistory = () => {
    const updated = clearAllHistory();
    setSearchHistory(updated);
  };

  // Reset all filters
  const handleResetFilters = () => {
    setFilters(INITIAL_FILTERS);
  };

  // Check if any non-default filters are active
  const hasActiveFilters = useMemo(() => {
    return (
      Boolean(filters.minPrice) ||
      Boolean(filters.maxPrice) ||
      Boolean(filters.minRating) ||
      filters.inStockOnly ||
      filters.primeOnly ||
      Boolean(filters.brand) ||
      filters.sortBy !== "relevance"
    );
  }, [filters]);

  // NLP Analysis for the executed query
  const parsedNLP = useMemo(() => {
    return parseSmartQuery(executedQuery);
  }, [executedQuery]);

  // Unified Product Catalog: Merges standard catalog + pre-cached scraped products + live scraped results
  const allUnifiedProducts = useMemo(() => {
    const map = new Map();
    // 1. Initial base catalog (Flipkart items)
    ALL_CATALOG_PRODUCTS.forEach((p) => map.set(p.asin || p.id, p));
    // 2. Scraped items from disk + live parallel search
    allProductsPool.forEach((p) => map.set(p.asin || p.id, p));
    return Array.from(map.values());
  }, [allProductsPool]);

// Strict store platform filter matcher: ensures each store only shows its own products
function matchesPlatform(product, selectedPlatform) {
  if (!product) return false;
  if (!selectedPlatform) return true;
  const target = selectedPlatform.toLowerCase().trim();
  if (target === "all" || target === "all 12 stores" || target.includes("all")) {
    return true;
  }

  const channel = (product.channel || "").toLowerCase();

  // Strict store-to-channel isolation
  if (target.includes("reliance")) {
    return channel === "reliance" || channel.includes("reliance");
  }
  if (target.includes("jiomart") || target.includes("jio")) {
    return channel === "jiomart" || channel.includes("jiomart");
  }
  if (target.includes("oppo")) {
    return channel === "oppo" || channel.includes("oppo");
  }
  if (target.includes("croma")) {
    return channel === "croma" || channel.includes("croma");
  }
  if (target.includes("samsung")) {
    return channel === "samsung" || channel.includes("samsung");
  }
  if (target.includes("apple")) {
    return channel === "apple" || channel.includes("apple");
  }
  if (target.includes("amazon")) {
    return channel === "amazon" || channel.includes("amazon");
  }
  if (target.includes("vivo")) {
    return channel === "vivo" || channel.includes("vivo");
  }
  if (target.includes("flipkart")) {
    return channel === "flipkart" || channel.includes("flipkart");
  }
  if (target.includes("vijay")) {
    return channel === "vijaysales" || channel.includes("vijay");
  }
  if (target.includes("poorvika")) {
    return channel === "poorvika" || channel.includes("poorvika");
  }
  if (target.includes("sangeetha")) {
    return channel === "sangeetha" || channel.includes("sangeetha");
  }
  if (target.includes("oneplus")) {
    return channel === "oneplus" || channel.includes("oneplus");
  }
  if (target.includes("xiaomi") || target.includes("mi")) {
    return channel === "xiaomi" || channel.includes("xiaomi") || channel.includes("mi");
  }

  return channel === target || channel.includes(target) || target.includes(channel);
}

  // Connect scraper dropdown selection with specific backend catalog data
  const platformProducts = useMemo(() => {
    return allUnifiedProducts.filter((product) => matchesPlatform(product, selectedPlatform));
  }, [allUnifiedProducts, selectedPlatform]);

  // Compute Search Results: Directly displays backend scraper results filtered by selected platform
  const filteredSearchResults = useMemo(() => {
    if (!executedQuery) return [];

    // When live scrapers have responded, strictly verify query and model accuracy!
    if (liveSearchResults && liveSearchResults.length > 0) {
      const platformFiltered = liveSearchResults.filter((p) => matchesPlatform(p, selectedPlatform));
      // Strict Model Isolation: Never allow unrelated models (like S26 or A56) to leak when searching S24 Ultra
      let results = filterProducts(platformFiltered, executedQuery, filters);

      if (filters.inStockOnly) {
        results = results.filter((p) => p.inStock);
      }
      if (filters.minPrice) {
        results = results.filter((p) => (p.priceNum || parsePriceNumber(p.price)) >= Number(filters.minPrice));
      }
      if (filters.maxPrice) {
        results = results.filter((p) => (p.priceNum || parsePriceNumber(p.price)) <= Number(filters.maxPrice));
      }

      return [...results].sort((a, b) => {
        const priceA = parsePriceNumber(a.price);
        const priceB = parsePriceNumber(b.price);
        const ratingA = parseRatingNumber(a.rating);
        const ratingB = parseRatingNumber(b.rating);

        if (filters.sortBy === "price_asc") return priceA - priceB;
        if (filters.sortBy === "price_desc") return priceB - priceA;
        if (filters.sortBy === "rating_desc") return ratingB - ratingA;
        return 0;
      });
    }

    // Fallback when scrapers have not responded yet: filter pre-scraped disk catalog
    const platformFiltered = allUnifiedProducts.filter((p) => matchesPlatform(p, selectedPlatform));
    const results = filterProducts(platformFiltered, executedQuery, filters);

    return [...results].sort((a, b) => {
      const priceA = parsePriceNumber(a.price);
      const priceB = parsePriceNumber(b.price);
      const ratingA = parseRatingNumber(a.rating);
      const ratingB = parseRatingNumber(b.rating);

      if (filters.sortBy === "price_asc") return priceA - priceB;
      if (filters.sortBy === "price_desc") return priceB - priceA;
      if (filters.sortBy === "rating_desc") return ratingB - ratingA;
      return 0;
    });
  }, [executedQuery, filters, liveSearchResults, allUnifiedProducts, selectedPlatform]);

  // Apply any active smart filters or executed query to the catalog
  const displayedProducts = useMemo(() => {
    if (executedQuery) {
      return filteredSearchResults;
    }

    let pool = platformProducts;
    if (hasActiveFilters) {
      pool = filterProducts(platformProducts, "", filters);
    }

    return [...pool].sort((a, b) => {
      const priceA = parsePriceNumber(a.price);
      const priceB = parsePriceNumber(b.price);
      const ratingA = parseRatingNumber(a.rating);
      const ratingB = parseRatingNumber(b.rating);

      if (filters.sortBy === "price_asc") return priceA - priceB;
      if (filters.sortBy === "price_desc") return priceB - priceA;
      if (filters.sortBy === "rating_desc") return ratingB - ratingA;
      return 0; // relevance
    });
  }, [platformProducts, filteredSearchResults, executedQuery, hasActiveFilters, filters]);

  // Lowest Price Comparison Banner across all returned products
  const bestDealProduct = useMemo(() => {
    if (!filteredSearchResults || filteredSearchResults.length === 0) return null;
    const valid = filteredSearchResults.filter(
      (p) => (p.priceNum && p.priceNum > 0) || parsePriceNumber(p.price) > 0
    );
    if (valid.length === 0) return null;
    return valid.reduce((lowest, curr) => {
      const lowestVal = lowest.priceNum || parsePriceNumber(lowest.price);
      const currVal = curr.priceNum || parsePriceNumber(curr.price);
      return currVal < lowestVal ? curr : lowest;
    }, valid[0]);
  }, [filteredSearchResults]);

  // Available brands for filter dropdown
  const availableBrands = useMemo(() => {
    const set = new Set();
    platformProducts.forEach((p) => {
      if (p.brand) set.add(p.brand);
    });
    return Array.from(set).sort();
  }, [platformProducts]);

  return (
    <div className="app">
      {/* Modern Left Sidebar */}
      <Sidebar
        activeItem={selectedPlatform}
        onSelectItem={(item) => {
          if (item === "Croma" || item === "Samsung" || item === "Apple" || item === "Amazon" || item === "Flipkart" || item === "Reliance" || item === "Reliance Digital" || item === "JioMart" || item === "Vivo" || item === "Oppo") {
            setSelectedPlatform(item);
            setActiveTab("All Products");
          } else {
            setActiveTab(item);
          }
          closeSidebar();
        }}
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
        counts={{
          all: allUnifiedProducts.length,
          croma: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("croma")).length,
          samsung: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("samsung")).length,
          apple: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("apple")).length,
          amazon: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("amazon")).length,
          flipkart: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("flipkart")).length,
          vivo: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("vivo")).length,
          reliance: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("reliance")).length,
          jiomart: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("jiomart")).length,
          oppo: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("oppo")).length,
        }}
      />

      {/* Main Content Area */}
      <div className="main-layout-wrapper">
        <Navbar
          onToggleSidebar={toggleSidebar}
          searchQuery={searchQuery}
          onSearchChange={(val) => {
            setSearchQuery(val);
            if (!val.trim()) setExecutedQuery("");
          }}
          onSearchSubmit={handleSearchSubmit}
          searchHistory={searchHistory}
          onDeleteHistoryItem={handleDeleteHistoryItem}
          onClearHistory={handleClearHistory}
          onToggleFilters={() => setIsFilterOpen((prev) => !prev)}
          isFilterOpen={isFilterOpen}
          hasActiveFilters={hasActiveFilters}
          activeCategory={activeCategory}
          onCategorySelect={(cat) => {
            setActiveCategory(cat);
            if (cat === "Mobiles" || cat === "All products") {
              setActiveTab("All Products");
            }
          }}
        />

        {/* Big Hero Search Bar with 12-Scraper Live Monitor */}
        <BigSearchBar
          searchQuery={searchQuery}
          onSearchChange={(val) => {
            setSearchQuery(val);
            if (!val.trim()) setExecutedQuery("");
          }}
          onSearchSubmit={handleSearchSubmit}
          scraperStatuses={scraperStatuses}
          isScrapingLive={isScrapingLive}
          selectedPlatform={selectedPlatform}
          onSelectPlatform={(storeName) => {
            setSelectedPlatform(storeName);
            setActiveTab("All Products");
          }}
          storeCounts={{
            all: allUnifiedProducts.length,
            croma: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("croma")).length,
            samsung: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("samsung")).length,
            apple: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("apple")).length,
            amazon: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("amazon")).length,
            flipkart: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("flipkart")).length,
            vivo: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("vivo")).length,
            reliance: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("reliance")).length,
            jiomart: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("jiomart")).length,
            oppo: allUnifiedProducts.filter((p) => (p.channel || "").toLowerCase().includes("oppo")).length,
          }}
        />

        {/* Global Smart Filter Toolbar (visible on demand or during search) */}
        {isFilterOpen && (
          <section className="smart-filter-toolbar" aria-label="Smart Filters">
            <div className="filter-toolbar-header">
              <span className="filter-toolbar-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
                </svg>
                Smart Filters
              </span>
              {hasActiveFilters && (
                <button
                  type="button"
                  className="filter-reset-link"
                  onClick={handleResetFilters}
                >
                  Reset all filters
                </button>
              )}
            </div>

            <div className="filter-controls-grid">
              {/* Price Range */}
              <div className="filter-control-group">
                <label className="filter-label">Price Range (₹)</label>
                <div className="price-inputs-row">
                  <input
                    type="number"
                    placeholder="Min"
                    className="filter-input-number"
                    value={filters.minPrice}
                    onChange={(e) =>
                      setFilters((prev) => ({ ...prev, minPrice: e.target.value }))
                    }
                  />
                  <span className="price-separator">to</span>
                  <input
                    type="number"
                    placeholder="Max"
                    className="filter-input-number"
                    value={filters.maxPrice}
                    onChange={(e) =>
                      setFilters((prev) => ({ ...prev, maxPrice: e.target.value }))
                    }
                  />
                </div>
              </div>

              {/* Customer Rating */}
              <div className="filter-control-group">
                <label className="filter-label">Min Rating</label>
                <select
                  className="filter-select"
                  value={filters.minRating}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, minRating: e.target.value }))
                  }
                >
                  <option value="">All Ratings</option>
                  <option value="4.0">4.0★ & above</option>
                  <option value="4.3">4.3★ & above</option>
                  <option value="4.5">4.5★ & above</option>
                </select>
              </div>

              {/* Brand */}
              <div className="filter-control-group">
                <label className="filter-label">Brand</label>
                <select
                  className="filter-select"
                  value={filters.brand}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, brand: e.target.value }))
                  }
                >
                  <option value="">All Brands</option>
                  {availableBrands.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div className="filter-control-group">
                <label className="filter-label">Sort By</label>
                <select
                  className="filter-select"
                  value={filters.sortBy}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, sortBy: e.target.value }))
                  }
                >
                  <option value="relevance">Relevance</option>
                  <option value="price_asc">Price: Low to High</option>
                  <option value="price_desc">Price: High to Low</option>
                  <option value="rating_desc">Highest Rated</option>
                </select>
              </div>

              {/* Checkboxes: In Stock & Prime */}
              <div className="filter-checkbox-group">
                <label className="filter-checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.inStockOnly}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        inStockOnly: e.target.checked,
                      }))
                    }
                  />
                  <span>In-Stock Only</span>
                </label>

                <label className="filter-checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.primeOnly}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        primeOnly: e.target.checked,
                      }))
                    }
                  />
                  <span>Prime / Assured</span>
                </label>
              </div>
            </div>
          </section>
        )}

        {/* Tab: Search Results View */}
        {activeTab === "Search Results" && (
          <main className="main-content">
            <div className="search-results-header-card">
              <div className="search-header-top">
                <h2>
                  Search Results for <span>"{executedQuery}"</span>
                </h2>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <ScraperDropdown
                    selectedPlatform={selectedPlatform}
                    onSelectPlatform={setSelectedPlatform}
                  />
                  <span className="results-count-badge">
                    {filteredSearchResults.length} {filteredSearchResults.length === 1 ? "product" : "products"} found
                  </span>
                </div>
              </div>

              {/* NLP Query Insights Bar */}
              {(parsedNLP.detectedBudget || parsedNLP.detectedBrand || hasActiveFilters) && (
                <div className="nlp-tags-row">
                  <span className="nlp-tags-lead">Applied constraints:</span>
                  {parsedNLP.detectedBudget && (
                    <span className="nlp-constraint-tag budget-tag">
                      🎯 Budget: {parsedNLP.detectedBudget}
                    </span>
                  )}
                  {(filters.brand || parsedNLP.detectedBrand) && (
                    <span className="nlp-constraint-tag brand-tag">
                      🏷️ Brand: {filters.brand || parsedNLP.detectedBrand}
                    </span>
                  )}
                  {filters.minRating && (
                    <span className="nlp-constraint-tag rating-tag">
                      ⭐ {filters.minRating}★ & above
                    </span>
                  )}
                  {filters.inStockOnly && (
                    <span className="nlp-constraint-tag">✓ In-Stock</span>
                  )}
                  {filters.primeOnly && (
                    <span className="nlp-constraint-tag">⚡ Prime / Assured</span>
                  )}
                </div>
              )}
            </div>

            {/* Best Deal Comparison Callout */}
            {bestDealProduct && (
              <div className="best-price-banner">
                <span className="best-price-icon">🏆</span>
                <span>
                  Lowest Price Found: <strong>{bestDealProduct.price}</strong> on <strong>{bestDealProduct.sourceName || bestDealProduct.brand}</strong> ({bestDealProduct.name})
                </span>
                {bestDealProduct.url && bestDealProduct.url !== "#" && (
                  <a
                    href={bestDealProduct.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="best-price-link"
                  >
                    View Best Deal →
                  </a>
                )}
              </div>
            )}

            {scraperError && (
              <div className="scraper-error-banner" role="alert">
                {scraperError}
              </div>
            )}

            {/* Live scraper progress */}
            {isScrapingLive && (
              <div className="scraper-progress-banner" role="status" aria-live="polite">
                <div className="scraper-progress-header">
                  <div className="scraper-progress-header-left">
                    <span className="scraper-pulse-dot" />
                    <span className="scraper-progress-msg">
                      <strong>Live {selectedPlatform} Scraper:</strong> {scraperProgress.message || `Scanning ${selectedPlatform} catalog...`}
                    </span>
                  </div>
                  <span className="scraper-progress-number">{scraperProgress.progress || 15}%</span>
                </div>
                <div className="scraper-progress-bar">
                  <div
                    className="scraper-progress-fill"
                    style={{ width: `${Math.max(12, scraperProgress.progress || 15)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Product Grid */}
            {filteredSearchResults.length > 0 ? (
              <div className="product-grid">
                {filteredSearchResults.map((product) => (
                  <ProductCard
                    key={product.id}
                    name={product.name}
                    image={product.image}
                    price={product.price}
                    originalPrice={product.originalPrice}
                    discount={product.discount}
                    rating={product.rating}
                    delivery={product.delivery}
                    seller={product.seller}
                    badge={product.badge}
                    badgeType={product.badgeType}
                    url={product.url}
                    channel={product.channel}
                    brand={product.brand}
                    sourceName={product.sourceName}
                    onOpenBulkAutomation={setBulkBotProduct}
                  />
                ))}
              </div>
            ) : (
              <div className="search-empty-state">
                <div className="empty-state-icon">🔍</div>
                <h3>No products found</h3>
                <p>
                  No gadgets matched your search for <strong>"{executedQuery}"</strong> with the currently selected filters.
                </p>
                <div className="empty-state-actions">
                  {hasActiveFilters && (
                    <button
                      type="button"
                      className="placeholder-action-btn"
                      onClick={handleResetFilters}
                    >
                      Clear Filters
                    </button>
                  )}
                  <button
                    type="button"
                    className="placeholder-action-btn"
                    style={{ backgroundColor: "#2874f0" }}
                    onClick={() => setActiveTab("All Products")}
                  >
                    View All Products
                  </button>
                </div>
              </div>
            )}
          </main>
        )}

        {/* Tab 1: All Products (Unified Catalog) */}
        {activeTab === "All Products" && (
          <main className="main-content">
            <div className="product-section-header">
              <div className="section-title-wrap">
                <h2 className="product-section-title">
                  {executedQuery ? `Search Results for "${executedQuery}"` : `${selectedPlatform} Products`}
                </h2>
                <span className="product-count-sub">
                  Showing {displayedProducts.length} {displayedProducts.length === 1 ? "product" : "products"} {executedQuery ? `matching "${executedQuery}"` : `from ${selectedPlatform}`}
                </span>
              </div>
              <ScraperDropdown
                selectedPlatform={selectedPlatform}
                onSelectPlatform={setSelectedPlatform}
              />
            </div>

            {/* Best Deal Callout */}
            {bestDealProduct && executedQuery && (
              <div className="best-price-banner">
                <span className="best-price-icon">🏆</span>
                <span>
                  Lowest Price Found: <strong>{bestDealProduct.price}</strong> on <strong>{bestDealProduct.sourceName || bestDealProduct.brand}</strong> ({bestDealProduct.name})
                </span>
                {bestDealProduct.url && bestDealProduct.url !== "#" && (
                  <a
                    href={bestDealProduct.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="best-price-link"
                  >
                    View Best Deal →
                  </a>
                )}
              </div>
            )}

            {displayedProducts.length > 0 ? (
              <div className="product-grid">
                {displayedProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    name={product.name}
                    image={product.image}
                    price={product.price}
                    originalPrice={product.originalPrice}
                    discount={product.discount}
                    rating={product.rating}
                    delivery={product.delivery}
                    seller={product.seller}
                    badge={product.badge}
                    badgeType={product.badgeType}
                    url={product.url}
                    channel={product.channel}
                    brand={product.brand}
                    sourceName={product.sourceName}
                    onOpenBulkAutomation={setBulkBotProduct}
                  />
                ))}
              </div>
            ) : (
              <div className="search-empty-state">
                <div className="empty-state-icon">📦</div>
                <h3>No {selectedPlatform} products found</h3>
                <p>
                  No products matched the current filters for {selectedPlatform}.
                </p>
                {hasActiveFilters && (
                  <button
                    type="button"
                    className="placeholder-action-btn"
                    onClick={handleResetFilters}
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            )}
          </main>
        )}

        {/* Tab: Flipkart Store & Deals */}
        {(activeTab === "Flipkart" || activeTab === "Flipkart Deals") && (
          <main className="main-content store-view flipkart-view">
            <div className="store-banner flipkart-banner">
              <div className="store-banner-info">
                <div className="store-badge-row">
                  <span className="store-tag flipkart-tag">FLIPKART STORE</span>
                  <span className="store-assured-badge">⚡ Flipkart Assured</span>
                </div>
                <h2>
                  {activeTab === "Flipkart Deals"
                    ? "Flipkart Super Deals & Offers"
                    : "Flipkart Smartphone Collection"}
                </h2>
                <p>
                  Explore authentic gadgets with official Flipkart warranty, bank discounts, and rapid delivery.
                </p>
              </div>
              <div className="store-banner-stats">
                <div className="store-banner-stat-box">
                  <span className="banner-stat-number">
                    {allUnifiedProducts.filter((p) => p.channel === "flipkart").length}
                  </span>
                  <span className="banner-stat-label">Live Listings</span>
                </div>
                <div className="store-banner-stat-box">
                  <span className="banner-stat-number">37%</span>
                  <span className="banner-stat-label">Max Discount</span>
                </div>
              </div>
            </div>

            <div className="store-filter-bar">
              <button
                type="button"
                className={`filter-chip ${activeTab === "Flipkart" ? "active-chip" : ""}`}
                onClick={() => setActiveTab("Flipkart")}
              >
                All Flipkart Products
              </button>
              <button
                type="button"
                className={`filter-chip ${activeTab === "Flipkart Deals" ? "active-chip" : ""}`}
                onClick={() => setActiveTab("Flipkart Deals")}
              >
                ⚡ Super Deals & Discounts
              </button>
            </div>

            <div className="product-grid">
              {allUnifiedProducts.filter((p) => p.channel === "flipkart").map((product) => (
                <ProductCard
                  key={product.id}
                  name={product.name}
                  image={product.image}
                  price={product.price}
                  originalPrice={product.originalPrice}
                  discount={product.discount}
                  rating={product.rating}
                  delivery={product.delivery}
                  seller={product.seller}
                  badge={product.badge}
                  badgeType={product.badgeType}
                  url={product.url}
                  channel={product.channel}
                  brand={product.brand}
                  sourceName={product.sourceName}
                  onOpenBulkAutomation={setBulkBotProduct}
                />
              ))}
            </div>
          </main>
        )}

        {/* Tab: Amazon Store & Deals */}
        {(activeTab === "Amazon" || activeTab === "Amazon Deals") && (
          <main className="main-content store-view amazon-view">
            <div className="store-banner amazon-banner">
              <div className="store-banner-info">
                <div className="store-badge-row">
                  <span className="store-tag amazon-tag">AMAZON STORE</span>
                  <span className="store-prime-badge">✓ prime delivery</span>
                </div>
                <h2>
                  {activeTab === "Amazon Deals"
                    ? "Amazon Lightning Deals"
                    : "Amazon Smartphone Collection"}
                </h2>
                <p>
                  Shop with Amazon Prime perks: Free One-Day delivery, hassle-free returns, and best seller rankings.
                </p>
              </div>
              <div className="store-banner-stats">
                <div className="store-banner-stat-box">
                  <span className="banner-stat-number">
                    {allUnifiedProducts.filter((p) => p.channel === "amazon").length}
                  </span>
                  <span className="banner-stat-label">Verified Items</span>
                </div>
                <div className="store-banner-stat-box">
                  <span className="banner-stat-number">1-Day</span>
                  <span className="banner-stat-label">Fast Shipping</span>
                </div>
              </div>
            </div>

            <div className="store-filter-bar">
              <button
                type="button"
                className={`filter-chip ${activeTab === "Amazon" ? "active-chip" : ""}`}
                onClick={() => setActiveTab("Amazon")}
              >
                All Amazon Products
              </button>
              <button
                type="button"
                className={`filter-chip ${activeTab === "Amazon Deals" ? "active-chip" : ""}`}
                onClick={() => setActiveTab("Amazon Deals")}
              >
                ⚡ Lightning Deals
              </button>
            </div>

            <div className="product-grid">
              {allUnifiedProducts.filter((p) => p.channel === "amazon").map((product) => (
                <ProductCard
                  key={product.id}
                  name={product.name}
                  image={product.image}
                  price={product.price}
                  originalPrice={product.originalPrice}
                  discount={product.discount}
                  rating={product.rating}
                  delivery={product.delivery}
                  seller={product.seller}
                  badge={product.badge}
                  badgeType={product.badgeType}
                  url={product.url}
                  channel={product.channel}
                  brand={product.brand}
                  sourceName={product.sourceName}
                  onOpenBulkAutomation={setBulkBotProduct}
                />
              ))}
            </div>
          </main>
        )}

        {/* Tab 2: Dashboard Placeholder */}
        {activeTab === "Dashboard" && (
          <main className="main-content placeholder-view">
            <div className="placeholder-header">
              <h2>Dashboard Overview</h2>
              <p>Welcome back to your Scalefox control panel.</p>
            </div>
            <div className="placeholder-stats-grid">
              <div className="placeholder-stat-card">
                <span className="stat-label">Total Catalog Products</span>
                <span className="stat-value">{allUnifiedProducts.length}</span>
                <span className="stat-sub">Across All Channels</span>
              </div>
              <div className="placeholder-stat-card">
                <span className="stat-label">Recent Searches Saved</span>
                <span className="stat-value">{searchHistory.length}</span>
                <span className="stat-sub">In search history</span>
              </div>
              <div className="placeholder-stat-card">
                <span className="stat-label">Connected Marketplaces</span>
                <span className="stat-value">2</span>
                <span className="stat-sub">
                  Flipkart & Amazon Active {isBackendOnline ? "(Scraper Online)" : ""}
                </span>
              </div>
            </div>
            <div className="placeholder-card">
              <div className="placeholder-icon-wrap">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2874f0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="7" height="9" rx="1" />
                  <rect x="14" y="3" width="7" height="5" rx="1" />
                  <rect x="14" y="12" width="7" height="9" rx="1" />
                  <rect x="3" y="16" width="7" height="5" rx="1" />
                </svg>
              </div>
              <h3>Shopping Console</h3>
              <p>Monitor products, compare prices between Flipkart and Amazon, and manage deals across your catalog.</p>
              <div style={{ display: "flex", gap: "10px", marginTop: "8px" }}>
                <button
                  type="button"
                  className="placeholder-action-btn"
                  onClick={() => setActiveTab("Flipkart")}
                >
                  View Flipkart
                </button>
                <button
                  type="button"
                  className="placeholder-action-btn"
                  style={{ backgroundColor: "#232f3e" }}
                  onClick={() => setActiveTab("Amazon")}
                >
                  View Amazon
                </button>
              </div>
            </div>
          </main>
        )}

        {/* Tab 3: Price Comparison Placeholder */}
        {activeTab === "Price Comparison" && (
          <main className="main-content placeholder-view">
            <div className="placeholder-header">
              <h2>Price Comparison</h2>
              <p>Compare real-time smartphone prices between Flipkart and Amazon.</p>
            </div>
            <div className="placeholder-card">
              <div className="placeholder-icon-wrap">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2874f0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="20" x2="18" y2="10" />
                  <line x1="12" y1="20" x2="12" y2="4" />
                  <line x1="6" y1="20" x2="6" y2="14" />
                </svg>
              </div>
              <h3>Flipkart vs. Amazon Comparison Tool</h3>
              <p>Side-by-side pricing analysis and deal history tracking between Flipkart and Amazon stores is active.</p>
              <button
                type="button"
                className="placeholder-action-btn"
                onClick={() => setActiveTab("All Products")}
              >
                Go to All Products
              </button>
            </div>
          </main>
        )}

        {/* Tab 4: Verified Marketplace Sellers Directory */}
        {activeTab === "Sellers" && (
          <main className="main-content sellers-directory-view">
            <div className="placeholder-header">
              <h2>Marketplace Sellers Directory</h2>
              <p>Explore verified sellers discovered by live Amazon, Flipkart, Reliance, Croma, Samsung, and JioMart scrapers.</p>
            </div>
            
            <div className="sellers-grid">
              {(() => {
                const sellerMap = {};
                allUnifiedProducts.forEach((p) => {
                  const s = p.seller || "Official Store";
                  if (!sellerMap[s]) {
                    sellerMap[s] = {
                      name: s,
                      channel: p.channel || "amazon",
                      sourceName: p.sourceName || p.brand,
                      count: 0,
                      minPrice: p.priceNum || 0,
                      maxPrice: p.priceNum || 0,
                      isFBA: s.includes("(FBA)") || s.toLowerCase().includes("fba"),
                      isFAssured: s.includes("(F-Assured)") || s.toLowerCase().includes("f-assured"),
                      sampleProducts: [],
                    };
                  }
                  sellerMap[s].count += 1;
                  if (p.priceNum > 0) {
                    if (sellerMap[s].minPrice === 0 || p.priceNum < sellerMap[s].minPrice) {
                      sellerMap[s].minPrice = p.priceNum;
                    }
                    if (p.priceNum > sellerMap[s].maxPrice) {
                      sellerMap[s].maxPrice = p.priceNum;
                    }
                  }
                  if (sellerMap[s].sampleProducts.length < 3) {
                    sellerMap[s].sampleProducts.push(p);
                  }
                });

                const sellersList = Object.values(sellerMap).sort((a, b) => b.count - a.count);

                return (
                  <div className="sellers-cards-container">
                    {sellersList.map((sellerItem) => (
                      <div key={sellerItem.name} className="seller-profile-card">
                        <div className="seller-card-top">
                          <div className="seller-avatar">
                            {sellerItem.name.slice(0, 2).toUpperCase()}
                          </div>
                          <div className="seller-meta-info">
                            <h3 className="seller-title" title={sellerItem.name}>
                              {sellerItem.name}
                            </h3>
                            <div className="seller-badges-row">
                              <span className={`channel-pill channel-${sellerItem.channel}`}>
                                {sellerItem.sourceName}
                              </span>
                              {sellerItem.isFBA && (
                                <span className="seller-fba-pill">Fulfilled by Amazon</span>
                              )}
                              {sellerItem.isFAssured && (
                                <span className="seller-fassured-pill">Flipkart Assured</span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="seller-stats-strip">
                          <div className="seller-stat-box">
                            <span className="stat-label">Listed Handsets</span>
                            <span className="stat-val">{sellerItem.count} items</span>
                          </div>
                          {sellerItem.minPrice > 0 && (
                            <div className="seller-stat-box">
                              <span className="stat-label">Price Range</span>
                              <span className="stat-val">
                                ₹{sellerItem.minPrice.toLocaleString("en-IN")}
                                {sellerItem.maxPrice > sellerItem.minPrice ? ` - ₹${sellerItem.maxPrice.toLocaleString("en-IN")}` : ""}
                              </span>
                            </div>
                          )}
                        </div>

                        <div className="seller-sample-thumbs">
                          {sellerItem.sampleProducts.map((sp) => (
                            <img
                              key={sp.id}
                              src={sp.image}
                              alt={sp.name}
                              className="seller-sample-thumb"
                              title={sp.name}
                              onError={(e) => { e.target.style.display = "none"; }}
                            />
                          ))}
                        </div>

                        <button
                          type="button"
                          className="seller-filter-btn"
                          onClick={() => {
                            setSearchQuery(sellerItem.name.replace(/\(FBA\)/gi, "").trim());
                            setActiveTab("All Products");
                          }}
                        >
                          View Seller Products →
                        </button>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
          </main>
        )}

        {activeTab === "Wishlist" && (
          <WishlistPage onExploreProducts={() => setActiveTab("All Products")} />
        )}

        {/* Tab 6: Settings Placeholder */}
        {activeTab === "Settings" && (
          <main className="main-content placeholder-view">
            <div className="placeholder-header">
              <h2>Settings & Preferences</h2>
              <p>Configure account and store syncing preferences.</p>
            </div>
            <div className="placeholder-card">
              <div className="placeholder-icon-wrap">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2874f0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                </svg>
              </div>
              <h3>Multi-Store Synchronization</h3>
              <p>Flipkart Catalog API: Connected. Amazon MWS/SP-API: Connected. Currency: INR (₹).</p>
              <button
                type="button"
                className="placeholder-action-btn"
                onClick={() => setActiveTab("All Products")}
              >
                Back to Shopping
              </button>
            </div>
          </main>
        )}
      </div>

      {/* Samsung Automated Bulk Buying Bot Modal */}
      {bulkBotProduct && (
        <SamsungBulkBotModal
          product={bulkBotProduct}
          onClose={() => setBulkBotProduct(null)}
        />
      )}
    </div>
  );
}

export default App;