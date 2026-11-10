import React, { useState } from "react";
import "./BigSearchBar.css";
import { SCRAPERS_CONFIG } from "../services/scrapersConfig";

export default function BigSearchBar({
  searchQuery = "",
  onSearchChange,
  onSearchSubmit,
  scraperStatuses = {},
  isScrapingLive = false,
  selectedPlatform = "All 12 Stores",
  onSelectPlatform,
  storeCounts = {},
}) {
  const [localInput, setLocalInput] = useState(searchQuery);

  const handleSubmit = (e) => {
    e.preventDefault();
    const query = localInput.trim();
    if (onSearchChange) onSearchChange(query);
    if (onSearchSubmit) onSearchSubmit(query);
  };

  const handleChipClick = (query) => {
    setLocalInput(query);
    if (onSearchChange) onSearchChange(query);
    if (onSearchSubmit) onSearchSubmit(query);
  };

  const handlePlatformClick = (platformName) => {
    if (onSelectPlatform) {
      onSelectPlatform(platformName);
    }
  };

  const completedCount = Object.values(scraperStatuses).filter(
    (s) => s.status === "completed" || s.status === "ready"
  ).length;

  const totalScrapers = SCRAPERS_CONFIG.length;
  const progressPct = totalScrapers > 0 ? Math.round((completedCount / totalScrapers) * 100) : 0;

  const keyStores = [
    { name: "All 12 Stores", icon: "🌟", count: storeCounts.all },
    { name: "Croma", icon: "🟢", count: storeCounts.croma },
    { name: "Samsung", icon: "🔵", count: storeCounts.samsung },
    { name: "Apple", icon: "🍎", count: storeCounts.apple },
    { name: "Amazon", icon: "🟠", count: storeCounts.amazon },
    { name: "Flipkart", icon: "🛍️", count: storeCounts.flipkart },
    { name: "Vivo", icon: "🟣", count: storeCounts.vivo },
    { name: "Reliance Digital", icon: "🔴", count: storeCounts.reliance },
    { name: "JioMart", icon: "🔵", count: storeCounts.jiomart },
    { name: "Oppo", icon: "🟢", count: storeCounts.oppo },
  ];

  return (
    <div className="big-hero-search-container">
      <div className="big-hero-badge">
        <span className="live-dot-pulse" />
        <span>Live Multi-Store Price Comparison Engine (12 Scrapers)</span>
      </div>

      <h1 className="big-hero-title">
        Compare Live Prices Across <span className="highlight-text">12 Stores & Scrapers</span>
      </h1>
      <p className="big-hero-subtitle">
        Type any smartphone (e.g. <strong>"ai pulse 2"</strong>, <strong>"iPhone 15"</strong>, <strong>"Galaxy"</strong>). Live API calls fan out to all stores simultaneously!
      </p>

      {/* Main Search Form */}
      <form className="big-search-box-form" onSubmit={handleSubmit}>
        <div className="big-search-input-wrap">
          <svg
            className="big-search-icon"
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>

          <input
            type="text"
            className="big-search-input-field"
            placeholder="Search products across Croma, Samsung, Apple, Amazon & 8 more..."
            value={localInput}
            onChange={(e) => {
              setLocalInput(e.target.value);
              if (onSearchChange) onSearchChange(e.target.value);
            }}
          />

          {localInput && (
            <button
              type="button"
              className="big-search-clear-btn"
              onClick={() => {
                setLocalInput("");
                if (onSearchChange) onSearchChange("");
              }}
              title="Clear search"
            >
              ✕
            </button>
          )}

          <button
            type="submit"
            className={`big-search-submit-btn ${isScrapingLive ? "loading" : ""}`}
            disabled={isScrapingLive}
          >
            {isScrapingLive ? (
              <>
                <span className="spinner-icon" />
                <span>Scraping 12 Stores...</span>
              </>
            ) : (
              <>
                <span>Search All 12 Scrapers</span>
                <span className="arrow-icon">→</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Quick Search Suggestions */}
      <div className="quick-suggestions-row">
        <span className="suggestion-label">Trending Searches:</span>
        {["ai pulse 2", "iPhone 15", "Galaxy S24 Ultra", "iPhone 16 Pro", "Samsung S23 5G", "Croma iPhone 17"].map(
          (item) => (
            <button
              key={item}
              type="button"
              className="quick-chip-btn"
              onClick={() => handleChipClick(item)}
            >
              {item}
            </button>
          )
        )}
      </div>

      {/* Instant Store Switcher Row */}
      <div className="instant-store-tabs">
        <span className="store-tabs-label">Filter Store:</span>
        {keyStores.map((st) => {
          const isSelected =
            (selectedPlatform || "").toLowerCase() === st.name.toLowerCase() ||
            (st.name.includes("All") && (selectedPlatform || "").toLowerCase().includes("all"));
          return (
            <button
              key={st.name}
              type="button"
              className={`store-tab-pill ${isSelected ? "active" : ""}`}
              onClick={() => handlePlatformClick(st.name)}
            >
              <span>{st.icon}</span>
              <span>{st.name}</span>
              {st.count !== undefined && <span className="tab-count">({st.count})</span>}
            </button>
          );
        })}
      </div>

      {/* Live Parallel Scraper Monitor Board */}
      <div className="live-scrapers-monitor-board">
        <div className="monitor-header">
          <div className="monitor-title">
            <span className="signal-icon">⚡</span>
            <span>Parallel Scraper Live Engine ({completedCount}/{totalScrapers} Responded)</span>
          </div>
          {isScrapingLive && (
            <div className="monitor-progress-bar-wrap">
              <div
                className="monitor-progress-fill"
                style={{ width: `${Math.max(10, progressPct)}%` }}
              />
            </div>
          )}
        </div>

        <div className="scrapers-chips-grid">
          {SCRAPERS_CONFIG.map((scraper) => {
            const st = scraperStatuses[scraper.id] || {};
            const statusKey = st.status || "idle";
            const count = st.count || 0;
            const isSelected = (selectedPlatform || "").toLowerCase() === scraper.name.toLowerCase();

            let badgeClass = "badge-idle";
            let label = scraper.name;
            let icon = "⚪";

            if (statusKey === "searching" || statusKey === "scraping") {
              badgeClass = "badge-scraping";
              label = `${scraper.name} Scanning...`;
              icon = "🟡";
            } else if (statusKey === "completed") {
              badgeClass = count > 0 ? "badge-success" : "badge-empty";
              label = count > 0 ? `${scraper.name} (${count})` : `${scraper.name} (0)`;
              icon = count > 0 ? "🟢" : "⚪";
            } else if (statusKey === "offline" || statusKey === "error") {
              badgeClass = "badge-offline";
              label = `${scraper.name} (Offline)`;
              icon = "🔴";
            }

            return (
              <button
                key={scraper.id}
                type="button"
                className={`scraper-chip ${badgeClass} ${isSelected ? "selected-chip" : ""}`}
                onClick={() => handlePlatformClick(scraper.name)}
                title={`Click to filter only ${scraper.name} products`}
                style={{ "--brand-accent": scraper.color }}
              >
                <span className="scraper-chip-icon">{icon}</span>
                <span className="scraper-chip-name">{label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

