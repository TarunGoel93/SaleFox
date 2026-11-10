/**
 * Scalefox Multi-Scraper Search & NLP Service
 * Supports 12 Scraper endpoints with Approach 1: Frontend Parallel Fan-Out (Promise.allSettled)
 * and Progressive Streaming (UI updates immediately as each scraper returns).
 */

import { SCRAPERS_CONFIG } from "./scrapersConfig.js";

// Cached JSON datasets from disk
import initialAmazonScraped from "../backend/scraped_data/amazon_products.json";
import initialAppleScraped from "../backend/brand_scrapers/apple/scraped_data/apple_products.json";
import initialVivoScraped from "../backend/brand_scrapers/vivo/scraped_data/vivo_products.json";
import initialCromaScraped from "../backend/brand_scrapers/croma/scraped_data/croma_products.json";
import initialSamsungScraped from "../backend/brand_scrapers/samsung/scraped_data/samsung_products.json";
import initialRelianceScraped from "../backend/brand_scrapers/reliance/scraped_data/reliance_products.json";
import initialJioMartScraped from "../backend/brand_scrapers/jiomart/scraped_data/jiomart_products.json";
import initialOppoScraped from "../backend/brand_scrapers/oppo/scraped_data/oppo_products.json";
import initialFlipkartScraped from "../backend/scraped_data/flipkart_products.json";

const HISTORY_STORAGE_KEY = "scalefox_search_history_v1";

// Helper to convert price strings like "₹79,900" or "79900" to float
export function parsePriceNumber(priceStr) {
  if (typeof priceStr === "number") return priceStr;
  if (!priceStr) return 0;
  const cleaned = String(priceStr).replace(/[^0-9.]/g, "");
  return parseFloat(cleaned) || 0;
}

// Helper to convert rating strings like "4.5/5" or "4.3" to float
export function parseRatingNumber(ratingStr) {
  if (typeof ratingStr === "number") return ratingStr;
  if (!ratingStr) return 0;
  const match = String(ratingStr).match(/([0-9]+(?:\.[0-9]+)?)/);
  return match ? parseFloat(match[1]) : 0;
}

/**
 * Smart Natural Language Query Parser
 */
export function parseSmartQuery(queryText = "") {
  const raw = String(queryText).trim();
  if (!raw) {
    return {
      rawQuery: "",
      keyword: "",
      minPrice: null,
      maxPrice: null,
      minRating: null,
      detectedBrand: null,
      detectedBudget: "",
    };
  }

  let minPrice = null;
  let maxPrice = null;
  let minRating = null;
  let detectedBudget = "";
  let workingQuery = raw;

  // 1. Between X and Y
  const betweenMatch = workingQuery.match(
    /(?:between|from)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|l|lakh)?\s*(?:to|and|-)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|l|lakh)?/i
  );
  if (betweenMatch) {
    const toNum = (valStr, unit) => {
      let v = parseFloat(valStr);
      const u = (unit || "").toLowerCase();
      if (u === "k" || u === "thousand" || (v <= 100 && v > 0)) v *= 1000;
      else if (u === "l" || u === "lakh") v *= 100000;
      return v;
    };
    minPrice = toNum(betweenMatch[1], betweenMatch[2]);
    maxPrice = toNum(betweenMatch[3], betweenMatch[4]);
    detectedBudget = `₹${minPrice.toLocaleString()} - ₹${maxPrice.toLocaleString()}`;
    workingQuery = workingQuery.replace(betweenMatch[0], " ");
  }

  // 2. Under / Below / Less than
  if (maxPrice === null) {
    const underMatch = workingQuery.match(
      /(?:under|below|less\s+than|up\s+to|within|max|<=|<)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|l|lakh)?/i
    );
    if (underMatch) {
      let val = parseFloat(underMatch[1]);
      const unit = (underMatch[2] || "").toLowerCase();
      if (unit === "k" || unit === "thousand" || (val <= 100 && val > 0)) {
        val *= 1000;
      } else if (unit === "l" || unit === "lakh") {
        val *= 100000;
      }
      maxPrice = val;
      detectedBudget = `Under ₹${maxPrice.toLocaleString()}`;
      workingQuery = workingQuery.replace(underMatch[0], " ");
    }
  }

  // 3. Above / Over / More than
  if (minPrice === null) {
    const aboveMatch = workingQuery.match(
      /(?:above|over|more\s+than|min|>=|>)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|l|lakh)?/i
    );
    if (aboveMatch) {
      let val = parseFloat(aboveMatch[1]);
      const unit = (aboveMatch[2] || "").toLowerCase();
      if (unit === "k" || unit === "thousand" || (val <= 100 && val > 0)) {
        val *= 1000;
      } else if (unit === "l" || unit === "lakh") {
        val *= 100000;
      }
      minPrice = val;
      detectedBudget = `Above ₹${minPrice.toLocaleString()}`;
      workingQuery = workingQuery.replace(aboveMatch[0], " ");
    }
  }

  // 4. Rating filter
  const ratingMatch = workingQuery.match(
    /(?:above|over|>=|>)?\s*(\d(?:\.\d)?)\s*(?:star|\*|rating)/i
  );
  if (ratingMatch) {
    minRating = parseFloat(ratingMatch[1]);
    workingQuery = workingQuery.replace(ratingMatch[0], " ");
  }

  // 5. Brand detection
  const brands = [
    "Apple",
    "iPhone",
    "Samsung",
    "Galaxy",
    "Croma",
    "OnePlus",
    "Google",
    "Pixel",
    "Xiaomi",
    "Redmi",
    "Realme",
    "Vivo",
    "Oppo",
    "Motorola",
    "Nothing",
    "Asus",
    "Sony",
    "Reliance",
  ];
  let detectedBrand = null;
  for (const b of brands) {
    const regex = new RegExp(`\\b${b}\\b`, "i");
    if (regex.test(raw)) {
      detectedBrand = b === "iPhone" ? "Apple" : b === "Galaxy" ? "Samsung" : b;
      break;
    }
  }

  const keyword = workingQuery.replace(/\s+/g, " ").trim();

  return {
    rawQuery: raw,
    keyword,
    minPrice,
    maxPrice,
    minRating,
    detectedBrand,
    detectedBudget,
  };
}

/**
 * Filter product catalog in-memory based on search text and active filters
 */
export function filterProducts(products = [], query = "", filters = {}) {
  const nlp = parseSmartQuery(query);

  const effectiveMinPrice =
    filters.minPrice !== null && filters.minPrice !== ""
      ? parseFloat(filters.minPrice)
      : nlp.minPrice;

  const effectiveMaxPrice =
    filters.maxPrice !== null && filters.maxPrice !== ""
      ? parseFloat(filters.maxPrice)
      : nlp.maxPrice;

  const effectiveMinRating =
    filters.minRating !== null && filters.minRating !== ""
      ? parseFloat(filters.minRating)
      : nlp.minRating;

  const searchKeyword = (nlp.keyword || "").toLowerCase();
  const searchBrand = (filters.brand || nlp.detectedBrand || "").toLowerCase();

  return products.filter((product) => {
    const nameLower = (product.name || "").toLowerCase();
    const sellerLower = (product.seller || "").toLowerCase();
    const brandLower = (product.brand || "").toLowerCase();
    const priceVal = parsePriceNumber(product.price);
    const ratingVal = parseRatingNumber(product.rating);

    // 1. Keyword check
    if (
      searchKeyword &&
      searchKeyword !== "phone" &&
      searchKeyword !== "phones" &&
      searchKeyword !== "mobile" &&
      searchKeyword !== "mobiles" &&
      searchKeyword !== "all"
    ) {
      const isAiQuery = /\b(ai|pulse)\b/i.test(searchKeyword);
      if (isAiQuery) {
        // AI queries match AI flagships and smartphones
        const matchesAi =
          nameLower.includes("ai") ||
          nameLower.includes("galaxy") ||
          nameLower.includes("5g") ||
          nameLower.includes("ultra") ||
          nameLower.includes("pro") ||
          brandLower.includes("samsung") ||
          brandLower.includes("apple") ||
          brandLower.includes("croma");
        if (!matchesAi && !nameLower.includes(searchKeyword)) return false;
      } else {
        // Strict token matching: Ignore pure noise/category words like 'phone', 'phones', 'mobile', 'under'
        const noise = new Set(["phone", "phones", "mobile", "mobiles", "smartphone", "smartphones", "under", "below", "buy", "online", "price", "the", "in", "a", "an", "and", "with"]);
        // Normalize letter-number spacing: "m 17" -> "m17", "17 e" -> "17e", "m17 e" -> "m17e"
        const normKeyword = searchKeyword
          .replace(/\b([a-zA-Z])\s+(\d+)/g, "$1$2")
          .replace(/(\d+)\s+([a-zA-Z])\b/g, "$1$2");
        const words = normKeyword.split(" ").filter((w) => w && !noise.has(w));

        if (words.length > 0) {
          const normalizedTarget = `${nameLower} ${brandLower} ${sellerLower}`
            .toLowerCase()
            .replace(/\b([a-zA-Z])\s+(\d+)/g, "$1$2")
            .replace(/(\d+)\s+([a-zA-Z])\b/g, "$1$2");

          const isSamsungPhone = brandLower.includes("samsung") || nameLower.includes("samsung");

          const matchesAllTokens = words.every((w) => {
            // 'galaxy' exception for Samsung: all Samsung smartphones are Galaxy series, even if store writes 'Samsung M17e 5G'
            if (w === "galaxy" && isSamsungPhone) {
              return true;
            }
            // Strict token & model matching with word boundaries
            try {
              const tokenRegex = new RegExp(`\\b${w}\\b`, "i");
              return tokenRegex.test(normalizedTarget);
            } catch {
              return normalizedTarget.includes(w);
            }
          });
          if (!matchesAllTokens) return false;
        }
      }
    }

    // 2. Brand check
    if (searchBrand) {
      const matchesBrand =
        nameLower.includes(searchBrand) || brandLower.includes(searchBrand);
      if (!matchesBrand) return false;
    }

    // 3. Price checks
    if (effectiveMinPrice !== null && priceVal < effectiveMinPrice) {
      return false;
    }
    if (effectiveMaxPrice !== null && priceVal > effectiveMaxPrice) {
      return false;
    }

    // 4. Rating check
    if (effectiveMinRating !== null && ratingVal < effectiveMinRating) {
      return false;
    }

    // 5. In-stock check
    if (filters.inStockOnly && product.inStock === false) {
      return false;
    }

    // 6. Prime / Assured check
    if (filters.primeOnly) {
      const hasPrimeOrAssured =
        (product.badge && /prime|assured/i.test(product.badge)) ||
        (product.delivery && /prime|tomorrow/i.test(product.delivery));
      if (!hasPrimeOrAssured) return false;
    }

    return true;
  });
}

/**
 * Universal Scraped Item Transformer
 * Normalizes item schemas from any of the 12 scrapers (Amazon, Croma, Samsung, Apple, Vivo, etc.)
 */
export function transformUniversalScrapedItem(item, scraper = {}, index = 0) {
  if (!item) return null;

  const brandName = item.brand || scraper.brand || scraper.name || "Brand";
  const channelName = scraper.channel || (scraper.id || "store").toLowerCase();
  const identifier =
    item.asin || item.sku || item.product_id || item.code || `${channelName}_${index}_${Date.now()}`;

  const priceNum = item.price_num || parsePriceNumber(item.price);
  let formattedPrice = "Out of Stock";
  if (priceNum > 0) {
    formattedPrice = `₹${priceNum.toLocaleString("en-IN")}`;
  } else if (item.price && item.price !== "₹0" && item.price !== "0" && item.price !== "₹0.00" && item.price !== "Out of Stock") {
    formattedPrice = item.price;
  } else {
    formattedPrice = "Out of Stock";
  }

  let mrpText = item.mrp || "";
  if (priceNum > 0 && !mrpText && item.mrp_num) {
    mrpText = `₹${item.mrp_num.toLocaleString("en-IN")}`;
  } else if (priceNum <= 0) {
    mrpText = "";
  }

  let discountText = item.discount || "";
  if (priceNum <= 0 || discountText === "0%" || discountText === "0% OFF" || discountText === "0% off") {
    discountText = "";
  } else if (discountText && !discountText.includes("off") && !discountText.includes("OFF")) {
    discountText = `${discountText.replace("-", "")} off`;
  }

  const ratingStr = item.rating
    ? String(item.rating).includes("/")
      ? item.rating
      : `${item.rating}/5`
    : "4.3/5";

  const defaultImg =
    channelName === "apple"
      ? "https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15.jpg"
      : channelName === "samsung"
      ? "https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-5g.jpg"
      : channelName === "oppo"
      ? "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/oppo-reno16-series-en/navigation/reno16/440-440-white.png"
      : "https://placehold.co/300x300?text=Product+Image";

  return {
    id: `${channelName}_${identifier}`,
    asin: item.asin || null,
    sku: item.sku || null,
    name: item.title || item.name || item.model || `${brandName} Device`,
    image: (() => {
      let rawImg = item.image_url || item.image || item.plpImage || defaultImg;
      if (typeof rawImg === "string") {
        if (rawImg.includes("reno16c/440-440-white.png")) {
          return "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/oppo-reno16-series-en/navigation/reno16-f/440-440-white.png";
        }
        if (rawImg.includes("oppo-find-x10-series/navigation/x10-pro-max")) {
          return "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/find-x10-series-en/navigation/find-x10-pro-max/440-440-white.png";
        }
        if (rawImg.includes("oppo-find-x10-series/navigation/x10/")) {
          return "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/find-x10-series-en/navigation/find-x10/440-440-blue.png";
        }
        if (rawImg.includes("oppo-f35-series-en/navigation/f35-pro")) {
          return "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/f35-pro-in/navigation/440-440-orange.png";
        }
        if (rawImg.includes("oppo-f35-series-en/navigation/f35/")) {
          return "https://www.oppo.com/content/dam/oppo_com/common/mkt/v2-2/oppo-a7-pro-serice-en/navigation/a7-pro/440-440-blue.png";
        }
        if (rawImg.includes("oppo-reno13-pro.jpg") || rawImg.includes("oppo-reno13.jpg")) {
          return "https://rukminim2.flixcart.com/image/416/416/xif0q/mobile/p/n/e/-resized-original-imahzx4mab5zr9y3.jpeg?q=70";
        }
        if (
          rawImg.includes("040909a72fc45b94") ||
          rawImg.includes("t3.png") ||
          rawImg.includes("t3pro") ||
          rawImg.includes("t3ultra")
        ) {
          return "https://fdn2.gsmarena.com/vv/bigpic/vivo-x-fold3-pro.jpg";
        }
      }
      return rawImg;
    })(),
    price: formattedPrice,
    priceNum: priceNum,
    originalPrice: mrpText,
    discount: discountText,
    rating: ratingStr,
    delivery:
      item.delivery ||
      (priceNum <= 0 || item.in_stock === false ? "Currently unavailable" : "Express Delivery Available"),
    seller: item.seller || `${scraper.name || brandName} Official Store`,
    badge: scraper.badge || (item.is_prime ? "Prime" : `${scraper.name} Verified`),
    badgeType: channelName,
    badgeColor: scraper.color || "#444444",
    brand: brandName,
    inStock: priceNum > 0 && item.in_stock !== false,
    channel: channelName,
    sourceName: scraper.name || brandName,
    url: (() => {
      let cleanUrl = item.url || "#";
      if (channelName.includes("jiomart") || cleanUrl.includes("jiomart.com")) {
        if (cleanUrl.includes("/p/") && !cleanUrl.includes("/p/digital/")) {
          const articleId = item.article_id || item.item_code || item.sku || item.uid;
          const slug = item.slug || cleanUrl.split("/p/")[1]?.split("/")[0] || "";
          if (slug && articleId && !slug.endsWith(articleId)) {
            cleanUrl = `https://www.jiomart.com/p/digital/${slug}/${articleId}`;
          } else if (slug) {
            cleanUrl = `https://www.jiomart.com/p/digital/${slug}`;
          }
        } else if (cleanUrl.includes("jiomart.com/search/") && !cleanUrl.includes("search?q=")) {
          const q = cleanUrl.split("/search/")[1] || "";
          cleanUrl = `https://www.jiomart.com/search?q=${q}`;
        }
      }
      if (channelName.includes("oppo") || cleanUrl.includes("oppo.com")) {
        if (cleanUrl.includes("shop.oppo.com")) {
          const slug = cleanUrl.replace("https://shop.oppo.com/in/product/", "").replace(".html", "").replace("oppo-", "");
          if (slug.includes("find-x")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-find-x/${slug.replace("-5g", "")}/`;
          } else if (slug.includes("find-n")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-find-n/${slug.replace("-5g", "")}/`;
          } else if (slug.includes("reno")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-reno/${slug.replace("-5g", "")}/`;
          } else if (slug.includes("f2") || slug.includes("f3")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-f/${slug}/`;
          } else if (slug.startsWith("a")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-a/${slug}/`;
          } else if (slug.startsWith("k")) {
            cleanUrl = `https://www.oppo.com/in/smartphones/series-k/${slug}/`;
          } else {
            cleanUrl = `https://www.oppo.com/in/smartphones/`;
          }
        }
      }
      return cleanUrl;
    })(),
    specs: item.specs || [],
    isLiveScraped: true,
  };
}

/**
 * Get initial products combined from all pre-scraped authentic disk files
 */
export function getInitialAllProducts() {
  const products = [];

  // Croma
  if (Array.isArray(initialCromaScraped)) {
    initialCromaScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "croma", name: "Croma", channel: "croma", badge: "Croma Official", color: "#00b5b5" }, i);
      if (p) products.push(p);
    });
  }

  // Samsung
  if (Array.isArray(initialSamsungScraped)) {
    initialSamsungScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "samsung", name: "Samsung", channel: "samsung", badge: "Samsung Official", color: "#1428a0" }, i);
      if (p) products.push(p);
    });
  }

  // Apple
  if (Array.isArray(initialAppleScraped)) {
    initialAppleScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "apple", name: "Apple", channel: "apple", badge: "Apple Store", color: "#555555" }, i);
      if (p) products.push(p);
    });
  }

  // Vivo
  if (Array.isArray(initialVivoScraped)) {
    initialVivoScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "vivo", name: "Vivo", channel: "vivo", badge: "Vivo Official", color: "#415fff" }, i);
      if (p) products.push(p);
    });
  }

  // Amazon
  if (Array.isArray(initialAmazonScraped)) {
    initialAmazonScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "amazon", name: "Amazon", channel: "amazon", badge: "Amazon Prime", color: "#FF9900" }, i);
      if (p) products.push(p);
    });
  }

  // Reliance Digital
  if (Array.isArray(initialRelianceScraped)) {
    initialRelianceScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "reliance", name: "Reliance Digital", channel: "reliance", badge: "Reliance Assured", color: "#e42529" }, i);
      if (p) products.push(p);
    });
  }

  // JioMart
  if (Array.isArray(initialJioMartScraped)) {
    initialJioMartScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "jiomart", name: "JioMart", channel: "jiomart", badge: "JioMart Verified", color: "#0078ad" }, i);
      if (p) products.push(p);
    });
  }

  // Oppo
  if (Array.isArray(initialOppoScraped)) {
    initialOppoScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "oppo", name: "Oppo", channel: "oppo", badge: "Oppo Official", color: "#008b47" }, i);
      if (p) products.push(p);
    });
  }

  // Flipkart
  if (Array.isArray(initialFlipkartScraped)) {
    initialFlipkartScraped.forEach((item, i) => {
      const p = transformUniversalScrapedItem(item, { id: "flipkart", name: "Flipkart", channel: "flipkart", badge: "Flipkart Assured", color: "#2874F0" }, i);
      if (p) products.push(p);
    });
  }

  return products;
}

/**
 * Check health of a specific scraper
 */
export async function checkScraperHealth(scraper) {
  try {
    const res = await fetch(`${scraper.baseUrl}${scraper.statusEndpoint || "/api/status"}`, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) return false;
    const data = await res.json();
    return Boolean(data && (data.status !== undefined || data.products !== undefined));
  } catch {
    return false;
  }
}

/**
 * Check all scrapers health in parallel
 */
export async function checkAllScrapersHealth() {
  const results = await Promise.allSettled(
    SCRAPERS_CONFIG.map(async (scraper) => {
      const isOnline = await checkScraperHealth(scraper);
      return { id: scraper.id, name: scraper.name, isOnline };
    })
  );

  const statusMap = {};
  results.forEach((res, idx) => {
    const scraper = SCRAPERS_CONFIG[idx];
    if (res.status === "fulfilled") {
      statusMap[scraper.id] = res.value.isOnline;
    } else {
      statusMap[scraper.id] = false;
    }
  });
  return statusMap;
}

/**
 * Search a single scraper with retry, polling, and data extraction
 */
export async function searchSingleScraper(scraper, query, filters = {}, onProgress = null) {
  const trimmed = String(query || "").trim();
  if (!trimmed) return [];

  const payload = {
    query: trimmed,
    pages: 3,
    pincode: import.meta.env.VITE_SCRAPER_PINCODE || "110058",
    in_stock_only: Boolean(filters.inStockOnly),
    min_price: filters.minPrice ? Number(filters.minPrice) : null,
    max_price: filters.maxPrice ? Number(filters.maxPrice) : null,
  };

  onProgress?.({
    status: "connecting",
    progress: 10,
    message: `Connecting to ${scraper.name} scraper...`,
  });

  try {
    // 1. Trigger the scraper
    const triggerRes = await fetch(`${scraper.baseUrl}${scraper.scrapeEndpoint || "/api/scrape"}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000),
    });

    if (!triggerRes.ok && triggerRes.status !== 409) {
      throw new Error(`Scraper start returned HTTP ${triggerRes.status}`);
    }

    const triggerData = await triggerRes.json().catch(() => ({}));

    // If endpoint returns synchronous results (e.g. serverless or instant cache)
    const directResults = triggerData.results || triggerData.products;
    if (Array.isArray(directResults) && directResults.length > 0) {
      onProgress?.({
        status: "completed",
        progress: 100,
        message: `${scraper.name}: ${directResults.length} items found`,
      });
      return directResults
        .map((item, idx) => transformUniversalScrapedItem(item, scraper, idx))
        .filter(Boolean);
    }

    // 2. Poll /api/status until completed or timeout
    const maxPollAttempts = 25; // 25 * 1000ms = 25s
    for (let attempt = 0; attempt < maxPollAttempts; attempt++) {
      await new Promise((r) => setTimeout(r, 1000));

      try {
        const statusRes = await fetch(`${scraper.baseUrl}${scraper.statusEndpoint || "/api/status"}`, {
          method: "GET",
          headers: { Accept: "application/json" },
          signal: AbortSignal.timeout(3000),
        });

        if (!statusRes.ok) continue;
        const job = await statusRes.json();

        const progress = Number(job.progress) || Math.min(15 + attempt * 4, 95);
        const message =
          job.message ||
          (Array.isArray(job.logs) ? job.logs.at(-1)?.msg || job.logs.at(-1) : null) ||
          `Scraping ${scraper.name}...`;

        onProgress?.({
          status: job.status || "scraping",
          progress,
          message,
        });

        const queryMatches =
          !job.query ||
          job.query.toLowerCase().trim() === trimmed.toLowerCase().trim() ||
          trimmed.toLowerCase().includes(job.query.toLowerCase()) ||
          job.query.toLowerCase().includes(trimmed.toLowerCase());

        if (job.status === "completed" || job.status === "ready") {
          if (!queryMatches && attempt < 5) {
            // Scraper is still returning prior query state, continue polling for current job
            continue;
          }
          const rawItems = Array.isArray(job.products)
            ? job.products
            : Array.isArray(job.results)
            ? job.results
            : [];
          return rawItems
            .map((item, idx) => transformUniversalScrapedItem(item, scraper, idx))
            .filter(Boolean);
        }

        if (job.status === "error") {
          throw new Error(job.error || `${scraper.name} scraper reported an error`);
        }
      } catch (pollErr) {
        // Continue polling until maxPollAttempts
      }
    }

    // Attempt to read latest status after timeout
    const finalRes = await fetch(`${scraper.baseUrl}${scraper.statusEndpoint || "/api/status"}`, {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(3000),
    });
    if (finalRes.ok) {
      const finalData = await finalRes.json();
      const raw = finalData.products || finalData.results || [];
      if (Array.isArray(raw) && raw.length > 0) {
        return raw.map((item, idx) => transformUniversalScrapedItem(item, scraper, idx)).filter(Boolean);
      }
    }

    return [];
  } catch (err) {
    onProgress?.({
      status: "offline",
      progress: 0,
      message: `${scraper.name} offline / unreachable`,
      error: err.message,
    });
    return [];
  }
}

/**
 * APPROACH 1: Frontend Parallel Fan-Out (Promise.allSettled) with Progressive Streaming
 *
 * Simultaneously sends HTTP requests to all 12 scrapers.
 * As soon as any scraper returns results, `onProductsBatch` is invoked immediately
 * so the frontend UI renders partial results instantly without waiting for all 12.
 */
export async function searchAcrossAll12Scrapers(
  query,
  filters = {},
  onScraperStatus = null,
  onProductsBatch = null
) {
  const trimmed = String(query || "").trim();
  if (!trimmed) return [];

  // Initialize all active scrapers to "searching" status
  SCRAPERS_CONFIG.forEach((scraper) => {
    onScraperStatus?.(scraper.id, {
      status: "searching",
      progress: 5,
      message: `Searching ${scraper.name}...`,
      count: 0,
      color: scraper.color,
      name: scraper.name,
    });
  });

  // Launch all scrapers concurrently
  const scraperPromises = SCRAPERS_CONFIG.map(async (scraper) => {
    try {
      const items = await searchSingleScraper(scraper, trimmed, filters, (prog) => {
        onScraperStatus?.(scraper.id, {
          ...prog,
          color: scraper.color,
          name: scraper.name,
        });
      });

      // Sanitize items: strictly ensure returned products match query so non-matching models never leak or inflate counts!
      const validItems = filterProducts(items, trimmed, filters);

      // Stream only verified matching products directly to the UI immediately!
      if (validItems && validItems.length > 0) {
        onProductsBatch?.(validItems, scraper.id);
        onScraperStatus?.(scraper.id, {
          status: "completed",
          progress: 100,
          message: `${scraper.name}: ${validItems.length} products found`,
          count: validItems.length,
          color: scraper.color,
          name: scraper.name,
        });
      } else {
        onProductsBatch?.([], scraper.id);
        onScraperStatus?.(scraper.id, {
          status: "completed",
          progress: 100,
          message: `${scraper.name}: No matching items`,
          count: 0,
          color: scraper.color,
          name: scraper.name,
        });
      }

      return validItems;
    } catch (err) {
      onScraperStatus?.(scraper.id, {
        status: "error",
        progress: 0,
        message: `${scraper.name} error: ${err.message}`,
        count: 0,
        color: scraper.color,
        name: scraper.name,
      });
      return [];
    }
  });

  // Wait for all scrapers to settle
  const settled = await Promise.allSettled(scraperPromises);
  const allAggregated = settled.flatMap((r) => (r.status === "fulfilled" ? r.value : []));

  return allAggregated;
}

// Search History Management
export function getSearchHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

export function saveSearchQuery(queryText, appliedFilters = {}) {
  const trimmed = String(queryText || "").trim();
  if (!trimmed) return getSearchHistory();

  try {
    const existing = getSearchHistory();
    const filtered = existing.filter(
      (item) => item.query.toLowerCase() !== trimmed.toLowerCase()
    );

    const now = new Date();
    const formattedDate = now.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
    const formattedTime = now.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });

    const newItem = {
      id: "sh_" + Date.now(),
      query: trimmed,
      date: `${formattedDate}, ${formattedTime}`,
      timestamp: Date.now(),
      filters: appliedFilters,
    };

    const updated = [newItem, ...filtered].slice(0, 15);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (err) {
    return getSearchHistory();
  }
}

export function deleteHistoryItem(id) {
  try {
    const existing = getSearchHistory();
    const updated = existing.filter((item) => item.id !== id);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch {
    return getSearchHistory();
  }
}

export function clearAllHistory() {
  try {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
    return [];
  } catch {
    return [];
  }
}

// Backward compatibility exports
export const checkBackendHealth = () => checkScraperHealth(SCRAPERS_CONFIG[3]); // Amazon
export const searchWithBackendScraper = (q, f, p) => searchSingleScraper(SCRAPERS_CONFIG[3], q, f, p);
export const searchWithBrandScraper = (brand, q, f, p) => {
  const scraper = SCRAPERS_CONFIG.find((s) => s.brand.toLowerCase() === brand.toLowerCase()) || SCRAPERS_CONFIG[0];
  return searchSingleScraper(scraper, q, f, p);
};
export const fetchScraperHistory = async () => [];
export const fetchBrandProducts = async (brand) => {
  const scraper = SCRAPERS_CONFIG.find((s) => s.brand.toLowerCase() === brand.toLowerCase());
  if (!scraper) return [];
  try {
    const res = await fetch(`${scraper.baseUrl}${scraper.statusEndpoint}`, { signal: AbortSignal.timeout(2000) });
    if (!res.ok) return [];
    const data = await res.json();
    const items = data.products || data.results || [];
    return items.map((it, idx) => transformUniversalScrapedItem(it, scraper, idx));
  } catch {
    return [];
  }
};
export const getInitialAmazonProducts = () =>
  Array.isArray(initialAmazonScraped)
    ? initialAmazonScraped.map((it, idx) => transformUniversalScrapedItem(it, { id: "amazon", name: "Amazon", channel: "amazon", badge: "Amazon Prime", color: "#FF9900" }, idx)).filter(Boolean)
    : [];
export const getInitialFlipkartProducts = () =>
  Array.isArray(initialFlipkartScraped)
    ? initialFlipkartScraped.map((it, idx) => transformUniversalScrapedItem(it, { id: "flipkart", name: "Flipkart", channel: "flipkart", badge: "Flipkart Assured", color: "#2874F0" }, idx)).filter(Boolean)
    : [];
export const getInitialBrandProducts = () => getInitialAllProducts();
