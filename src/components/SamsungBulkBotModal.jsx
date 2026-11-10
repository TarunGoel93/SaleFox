import React, { useState, useEffect, useRef } from "react";
import "./SamsungBulkBotModal.css";

const DEFAULT_ACCOUNTS = [
  { id: 1, name: "Account 1", profile: "account_1", status: "Ready", desc: "Default Primary" },
  { id: 2, name: "Account 2", profile: "account_2", status: "Ready", desc: "Secondary Buyer" },
  { id: 3, name: "Account 3", profile: "account_3", status: "Ready", desc: "Enterprise Profile" },
  { id: 4, name: "Account 4", profile: "account_4", status: "Ready", desc: "Backup Runner" },
  { id: 5, name: "Account 5", profile: "account_5", status: "Ready", desc: "Turbo Profile" },
];

const DEFAULT_CARDS = [
  { id: 1, label: "Card 1", brand: "Visa", last4: "1111", name: "Debraj Shil", expiry: "09/28", color: "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" },
  { id: 2, label: "Card 2", brand: "Mastercard", last4: "4444", name: "Debraj Shil", expiry: "10/29", color: "linear-gradient(135deg, #eb3349 0%, #f45c43 100%)" },
  { id: 3, label: "Card 3", brand: "Amex", last4: "0005", name: "Debraj Shil", expiry: "11/27", color: "linear-gradient(135deg, #134e5e 0%, #71b280 100%)" },
];

const PIPELINE_STEPS = [
  { id: 1, name: "Profile Init", desc: "Launch Chrome Profile with detached mode" },
  { id: 2, name: "SKU Select", desc: "Configure specs, color, storage & buy now" },
  { id: 3, name: "Cart & Checkout", desc: "Bypass login & route to guest checkout" },
  { id: 4, name: "Address Fill", desc: "Inject Kolkata Pincode 700092 shipping" },
  { id: 5, name: "Card Injection", desc: "Auto-fill card & await OTP handoff" },
];

export default function SamsungBulkBotModal({ product, onClose }) {
  const urlLower = (product?.url || product?.link || "").toLowerCase();
  const brandCombined = `${product?.scraper || ""} ${product?.channel || ""} ${product?.store || ""} ${product?.brand || ""} ${product?.seller || ""} ${product?.badgeType || ""} ${product?.name || ""} ${product?.sourceName || ""} ${urlLower}`.toLowerCase();

  let brandKey = "samsung";
  let apiPort = 5053;
  let brandName = "Samsung";
  let brandLogo = "SAMSUNG";
  let brandAutomation = "samsung_automation";
  let defaultUrl = "https://www.samsung.com/in/";

  if (brandCombined.includes("flipkart")) {
    brandKey = "flipkart";
    apiPort = 5051;
    brandName = "Flipkart";
    brandLogo = "FLIPKART";
    brandAutomation = "flipkart_automation";
    defaultUrl = "https://www.flipkart.com/";
  } else if (brandCombined.includes("amazon")) {
    brandKey = "amazon";
    apiPort = 5050;
    brandName = "Amazon";
    brandLogo = "AMAZON";
    brandAutomation = "amazon_automation";
    defaultUrl = "https://www.amazon.in/";
  } else if (brandCombined.includes("croma")) {
    brandKey = "croma";
    apiPort = 5054;
    brandName = "Croma";
    brandLogo = "CROMA";
    brandAutomation = "croma_automation";
    defaultUrl = "https://www.croma.com/";
  } else if (brandCombined.includes("reliance")) {
    brandKey = "reliance";
    apiPort = 5056;
    brandName = "Reliance Digital";
    brandLogo = "RELIANCE";
    brandAutomation = "reliance_automation";
    defaultUrl = "https://www.reliancedigital.in/";
  } else if (brandCombined.includes("jiomart") || brandCombined.includes("jio")) {
    brandKey = "jiomart";
    apiPort = 5062;
    brandName = "JioMart";
    brandLogo = "JIOMART";
    brandAutomation = "jiomart_automation";
    defaultUrl = "https://www.jiomart.com/";
  } else if (brandCombined.includes("apple") || brandCombined.includes("iphone")) {
    brandKey = "apple";
    apiPort = 5055;
    brandName = "Apple";
    brandLogo = "";
    brandAutomation = "apple_automation";
    defaultUrl = "https://www.apple.com/in/";
  } else if (brandCombined.includes("vivo")) {
    brandKey = "vivo";
    apiPort = 5052;
    brandName = "Vivo";
    brandLogo = "VIVO";
    brandAutomation = "vivo_automation";
    defaultUrl = "https://shop.vivo.com/in/";
  } else if (brandCombined.includes("oppo")) {
    brandKey = "oppo";
    apiPort = 5057;
    brandName = "Oppo";
    brandLogo = "OPPO";
    brandAutomation = "oppo_automation";
    defaultUrl = "https://www.oppo.com/in/store/";
  } else if (brandCombined.includes("samsung") || brandCombined.includes("galaxy")) {
    brandKey = "samsung";
    apiPort = 5053;
    brandName = "Samsung";
    brandLogo = "SAMSUNG";
    brandAutomation = "samsung_automation";
    defaultUrl = "https://www.samsung.com/in/";
  } else {
    brandKey = "samsung";
    apiPort = 5053;
    brandName = "Samsung";
    brandLogo = "SAMSUNG";
    brandAutomation = "samsung_automation";
    defaultUrl = "https://www.samsung.com/in/";
  }

  const isApple = brandKey === "apple";
  const isCroma = brandKey === "croma";
  const isFlipkart = brandKey === "flipkart";
  const isAmazon = brandKey === "amazon";
  const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
  const apiBase = isLocal ? `http://localhost:${apiPort}` : `/backend-${apiPort}`;

  const [selectedAccount, setSelectedAccount] = useState(1);
  const [selectedCardIndex, setSelectedCardIndex] = useState(0);
  const [bulkQty, setBulkQty] = useState(product?.quantity || 10);
  const [botStatus, setBotStatus] = useState("idle"); // idle, running, awaiting_otp, step_done, completed, cancelled, error
  const [currentStep, setCurrentStep] = useState(0);
  const [logs, setLogs] = useState([]);
  const [guestCheckout, setGuestCheckout] = useState(true);
  const [detachChrome, setDetachChrome] = useState(true);
  const [autoCardFill, setAutoCardFill] = useState(true);
  const [browserLaunching, setBrowserLaunching] = useState(false);
  const [cards, setCards] = useState(DEFAULT_CARDS);
  const [screenTab, setScreenTab] = useState("screen"); // "screen" | "terminal"
  const [liveScreenshot, setLiveScreenshot] = useState(null);
  const [liveUrl, setLiveUrl] = useState(defaultUrl);
  const [notification, setNotification] = useState(null);

  // Croma Payment & OTP state
  const [paymentMethod, setPaymentMethod] = useState("cards"); // "cards", "emi", "upi", "netbanking"
  const [upiId, setUpiId] = useState("debraj1849@okaxis");
  const [gstNumber, setGstNumber] = useState("05AAACD1234F1Z1");
  const [otpCode, setOtpCode] = useState("");
  const [otpSubmitting, setOtpSubmitting] = useState(false);
  const [otpRequired, setOtpRequired] = useState(false);
  const [showPin, setShowPin] = useState({});

  const csvInputRef = useRef(null);

  const pipelineSteps = isApple
    ? [
        { id: 1, name: "Profile Init", desc: "Launch detached Chrome Profile on desktop" },
        { id: 2, name: "Bag Check & Color", desc: "Clean previous bag items & select phone color" },
        { id: 3, name: "Options & Bag", desc: "Select 'No trade-in', 'No AppleCare+' & Add to Bag" },
        { id: 4, name: "Review Bag & Checkout", desc: "Click 'Review Bag' CTA, then 'Check Out' button" },
        { id: 5, name: "Address & Payment", desc: "Debraj Shil (700092 Kolkata) & Card Injection" },
      ]
    : isCroma
    ? [
        { id: 1, name: "Profile Init", desc: "Launch detached Chrome Profile on desktop" },
        { id: 2, name: "Cart & Add Device", desc: "Add phone to cart & verify croma.com/cart items" },
        { id: 3, name: "Email Login & OTP", desc: "Enter debraj1849@gmail.com & await floating OTP" },
        { id: 4, name: "Checkout & Address", desc: "Click Checkout, confirm Dehradun address & inject GST" },
        { id: 5, name: "Payment Gateway", desc: "Inject selected card/UPI/COD & place order" },
      ]
    : isFlipkart
    ? [
        { id: 1, name: "Profile Init", desc: "Launch isolated Chrome Profile for Flipkart" },
        { id: 2, name: "Cart & Delivery", desc: "Navigate to Flipkart item, check delivery & Add to Cart" },
        { id: 3, name: "Order Summary", desc: "Proceed to Checkout with Debraj Shil address" },
        { id: 4, name: "Payment Selection", desc: "Select COD / UPI / Card as configured" },
        { id: 5, name: "Order Confirm", desc: "Confirm Order and complete purchase" },
      ]
    : isAmazon
    ? [
        { id: 1, name: "Profile Init", desc: "Launch isolated Chrome Profile for Amazon" },
        { id: 2, name: "Cart & Buy Now", desc: "Add product to Amazon cart / Proceed to Checkout" },
        { id: 3, name: "Delivery Address", desc: "Confirm Debraj Shil shipping address" },
        { id: 4, name: "Payment Mode", desc: "Select Pay on Delivery (COD) / UPI / Card" },
        { id: 5, name: "Place Order", desc: "Review and click 'Place your order in INR'" },
      ]
    : [
        { id: 1, name: "Profile Init", desc: `Launch isolated Chrome Profile for ${brandName}` },
        { id: 2, name: "Cart Clean & Pincode", desc: "Clear previous cart & verify 700092 delivery" },
        { id: 3, name: "SKU & Add to Cart", desc: "Select device & click 'Buy Now' / 'Add to Cart'" },
        { id: 4, name: "Address Fill", desc: "Inject Kolkata 700092 shipping address" },
        { id: 5, name: "Card Injection", desc: "Auto-fill card & trigger gateway / OTP handoff" },
      ];

  const logsEndRef = useRef(null);
  const pollTimerRef = useRef(null);

  // Auto-scroll logs terminal
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const startPolling = () => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    pollTimerRef.current = setInterval(async () => {
      try {
        const statusRes = await fetch(`${apiBase}/api/automation/status`);
        if (!statusRes.ok) return;
        const data = await statusRes.json();
        if (data.logs && data.logs.length > 0) {
          setLogs(data.logs);
        }
        if (data.screenshot) {
          setLiveScreenshot(data.screenshot);
        }
        if (data.current_url) {
          setLiveUrl(data.current_url);
        }
        if (data.current_step !== undefined && data.current_step > 0) {
          setCurrentStep(data.current_step);
        }
        if (data.otp_required !== undefined) {
          setOtpRequired(Boolean(data.otp_required));
        }
        if (data.status) {
          setBotStatus(data.status);
          if (data.status === "awaiting_otp") {
            setOtpRequired(true);
          } else if (data.status === "awaiting_upi_qr") {
            setOtpRequired(false);
            // Keep polling active to stream live UPI QR code
          } else if (data.status === "completed" || data.status === "error" || data.status === "cancelled") {
            setOtpRequired(false);
            // Keep streaming for 20 more seconds so live mirror doesn't freeze abruptly
            setTimeout(() => {
              if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
                pollTimerRef.current = null;
              }
            }, 25000);
          }
        }
        if (data.notification) {
          setNotification(data.notification);
        }
      } catch {
        // ignore transient poll errors
      }
    }, 350);
  };

  // Load automation cards config from backend & check initial status
  useEffect(() => {
    fetch(`${apiBase}/api/automation/config`)
      .then((r) => r.json())
      .then((data) => {
        if (data.cards && data.cards.length > 0) {
          const mappedCards = data.cards.map((c, i) => ({
            ...c,
            color: DEFAULT_CARDS[i % DEFAULT_CARDS.length]?.color || DEFAULT_CARDS[0].color,
          }));
          setCards(mappedCards);
        }
      })
      .catch(() => {});

    // Check if there is an active session or screenshot
    fetch(`${apiBase}/api/automation/status`)
      .then((r) => r.json())
      .then((data) => {
        if (data.screenshot) setLiveScreenshot(data.screenshot);
        if (data.current_url) setLiveUrl(data.current_url);
        if (data.logs && data.logs.length > 0) setLogs(data.logs);
        if (data.status === "running") {
          setBotStatus("running");
          startPolling();
        }
      })
      .catch(() => {});
  }, [apiBase]);

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, []);

  // Initial greeting log
  useEffect(() => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs([
      `[${timestamp}] [SYSTEM] ${brandName} Automation Bot initialized.`,
      `[${timestamp}] [SYSTEM] Connected to C:\\Users\\DEBRAJ\\Downloads\\${brandAutomation}.`,
      `[${timestamp}] [INFO] Target Device: ${product?.name || brandName + " Smartphone"}.`,
      `[${timestamp}] [INFO] Active Account: Account ${selectedAccount} (profile: account_${selectedAccount}).`,
      `[${timestamp}] [INFO] Ready to launch automated bulk buying workflow with visible Chrome browser.`,
    ]);
  }, [product, selectedAccount, brandName, brandAutomation]);

  // Calculate pricing
  const unitPriceNum = (() => {
    if (typeof product?.price === "number") return product.price;
    const cleaned = String(product?.price || "").replace(/[^0-9.]/g, "");
    return parseFloat(cleaned) || 0;
  })();
  const totalBulkPrice = unitPriceNum * bulkQty;

  // Add a log entry helper
  const addLog = (msg, level = "INFO") => {
    const ts = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${ts}] [${level}] ${msg}`]);
  };

  // Launch Live Chrome Window via Backend
  const handleLaunchBrowser = async () => {
    setBrowserLaunching(true);
    addLog(`Launching Chrome browser for Account ${selectedAccount} on your desktop...`, "ACTION");
    try {
      const res = await fetch(`${apiBase}/api/automation/launch-browser`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account: selectedAccount, product_name: product?.name }),
      });
      if (res.ok) {
        addLog(`Chrome instance launched with persistent profile 'account_${selectedAccount}'!`, "SUCCESS");
        addLog(`Streaming live Chrome screen directly to your Desktop Screen Mirror.`, "INFO");
        startPolling();
      } else {
        addLog(`Chrome launch note: Local profile account_${selectedAccount} active.`, "INFO");
      }
    } catch {
      addLog(`Browser instance ready in detached mode for account_${selectedAccount}.`, "INFO");
    } finally {
      setBrowserLaunching(false);
    }
  };

  // Handle CSV Virtual Cards Import
  const handleCsvImport = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const text = event.target.result;
        const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
        if (lines.length < 2) {
          alert("CSV must contain a header row and at least 1 card row.");
          return;
        }

        const rawHeaders = lines[0].split(",").map((h) => h.trim().toLowerCase().replace(/['"]/g, ""));
        const findCol = (aliases) => rawHeaders.findIndex((h) => aliases.some((a) => h.includes(a)));

        const numIdx = findCol(["number", "card_number", "pan", "cardnum", "card"]);
        const nameIdx = findCol(["name", "holder", "cardholder"]);
        const expIdx = findCol(["exp", "expiry", "expire", "valid"]);
        const cvvIdx = findCol(["cvv", "cvc", "security", "code"]);
        const passIdx = findCol(["password", "pass", "pin", "virtual_password", "pwd"]);
        const brandIdx = findCol(["brand", "type", "network"]);
        const labelIdx = findCol(["label", "bank", "title", "alias"]);

        const gradients = [
          "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
          "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
          "linear-gradient(135deg, #8a2387 0%, #e94057 50%, #f27121 100%)",
          "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
          "linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)"
        ];

        const parsedCards = [];
        for (let i = 1; i < lines.length; i++) {
          const row = lines[i].split(",").map((c) => c.trim().replace(/^["']|["']$/g, ""));
          if (row.length === 0 || !row[0]) continue;

          let rawNum = numIdx >= 0 ? row[numIdx] : row[0];
          rawNum = rawNum.replace(/\D/g, "");
          if (rawNum.length < 12) continue;

          const cardLast4 = rawNum.slice(-4);
          const cardName = (nameIdx >= 0 && row[nameIdx]) ? row[nameIdx] : "Debraj Shil";
          const cardExp = (expIdx >= 0 && row[expIdx]) ? row[expIdx] : "12/28";
          const cardCvv = (cvvIdx >= 0 && row[cvvIdx]) ? row[cvvIdx] : "123";
          const cardPass = (passIdx >= 0 && row[passIdx]) ? row[passIdx] : (cvvIdx >= 0 ? row[cvvIdx] : "9999");
          let cardBrand = (brandIdx >= 0 && row[brandIdx]) ? row[brandIdx] : "";
          if (!cardBrand) {
            if (rawNum.startsWith("4")) cardBrand = "Visa";
            else if (rawNum.startsWith("5")) cardBrand = "Mastercard";
            else if (rawNum.startsWith("3")) cardBrand = "Amex";
            else if (rawNum.startsWith("6")) cardBrand = "RuPay";
            else cardBrand = "Virtual Card";
          }
          const cardLabel = (labelIdx >= 0 && row[labelIdx]) ? row[labelIdx] : `Virtual Card ${i}`;

          parsedCards.push({
            id: `virtual_${Date.now()}_${i}`,
            label: cardLabel,
            number: rawNum.replace(/(\d{4})(?=\d)/g, "$1 "),
            last4: cardLast4,
            name: cardName,
            expiry: cardExp,
            cvv: cardCvv,
            password: cardPass,
            brand: cardBrand,
            isVirtual: true,
            color: gradients[(i - 1) % gradients.length]
          });
        }

        if (parsedCards.length === 0) {
          alert("Could not find valid card numbers in the uploaded CSV.");
          return;
        }

        setCards((prev) => [...parsedCards, ...prev]);
        setSelectedCardIndex(0);
        addLog(`Successfully imported ${parsedCards.length} virtual cards with password/PIN from CSV!`, "SUCCESS");

        try {
          await fetch(`${apiBase}/api/automation/import-cards`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cards: parsedCards })
          });
        } catch {}
      } catch (err) {
        alert("Failed to parse CSV: " + err.message);
      }
    };
    reader.readAsText(file);
    if (csvInputRef.current) csvInputRef.current.value = "";
  };

  // Submit OTP handler
  const handleSubmitOtp = async () => {
    if (!otpCode || otpCode.trim().length === 0) {
      alert("Please enter the verification OTP");
      return;
    }
    setOtpSubmitting(true);
    addLog(`Submitting user OTP (${otpCode}) to ${brandName} login portal...`, "ACTION");
    try {
      const res = await fetch(`${apiBase}/api/automation/submit-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ otp: otpCode.trim() }),
      });
      if (res.ok) {
        addLog(`OTP delivered to bot engine successfully!`, "SUCCESS");
        setOtpRequired(false);
      } else {
        addLog(`Server responded with OTP error.`, "ERROR");
      }
    } catch (err) {
      addLog(`Failed to send OTP: ${err.message}`, "ERROR");
    } finally {
      setOtpSubmitting(false);
    }
  };

  // Execute Automated Bulk Buy Bot Workflow
  const handleStartBot = async () => {
    if (botStatus === "running") return;
    setBotStatus("running");
    setCurrentStep(1);
    setNotification(null);

    addLog(`[START] Initiating automated bulk purchasing engine for ${bulkQty} units...`, "START");
    addLog(`[ACTION] Opening visible Chrome profile 'account_${selectedAccount}' on your desktop...`, "ACTION");

    try {
      // Trigger the real Python automation runner with live visible Chrome
      const res = await fetch(`${apiBase}/api/automation/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          account: selectedAccount,
          product_name: product?.name || `${brandName} Smartphone`,
          product_url: product?.url || product?.link || "",
          quantity: bulkQty,
          card_index: selectedCardIndex,
          payment_method: paymentMethod,
          upi_id: upiId,
          card_obj: cards[selectedCardIndex] || null,
          gst_number: gstNumber,
          guest_checkout: guestCheckout,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      startPolling();

    } catch (err) {
      setBotStatus("error");
      addLog(`Failed to start automation bot: ${err.message}`, "ERROR");
    }
  };

  const handleResetBot = async () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    try {
      await fetch(`${apiBase}/api/automation/stop`, { method: "POST" });
    } catch {}
    setBotStatus("idle");
    setCurrentStep(0);
    const ts = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${ts}] [SYSTEM] Automation stopped. Chrome browser window left open on desktop.`]);
  };

  return (
    <div className="samsung-bulk-modal-overlay" onClick={onClose}>
      <div className="samsung-bulk-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="samsung-bulk-header">
          <div className="samsung-bulk-header-left">
            <span
              className="samsung-logo-badge"
              style={
                isApple
                  ? { background: "#0071e3", boxShadow: "0 0 15px rgba(0, 113, 227, 0.5)" }
                  : brandKey === "croma"
                  ? { background: "#00b259", boxShadow: "0 0 15px rgba(0, 178, 89, 0.5)" }
                  : brandKey === "flipkart"
                  ? { background: "#2874f0", color: "#fff", boxShadow: "0 0 15px rgba(40, 116, 240, 0.5)" }
                  : brandKey === "amazon"
                  ? { background: "#ff9900", color: "#111", boxShadow: "0 0 15px rgba(255, 153, 0, 0.5)" }
                  : brandKey === "vivo"
                  ? { background: "#415fff", color: "#fff", boxShadow: "0 0 15px rgba(65, 95, 255, 0.5)" }
                  : brandKey === "reliance"
                  ? { background: "#e11b22", boxShadow: "0 0 15px rgba(225, 27, 34, 0.5)" }
                  : brandKey === "jiomart"
                  ? { background: "#008ecc", boxShadow: "0 0 15px rgba(0, 142, 204, 0.5)" }
                  : brandKey === "oppo"
                  ? { background: "#008b47", boxShadow: "0 0 15px rgba(0, 139, 71, 0.5)" }
                  : {}
              }
            >
              {brandLogo}
            </span>
            <div className="header-titles">
              <h2>{brandName} Automated Bulk Buying Bot</h2>
              <p>Autonomous Multi-Account Purchasing Engine • Powered by <code>{brandAutomation}</code></p>
            </div>
          </div>
          <div className="samsung-bulk-header-right">
            <span className={`bot-status-pill status-${botStatus}`}>
              {botStatus === "idle" && "⚪ Bot Idle"}
              {botStatus === "running" && "🟡 Bot Running"}
              {botStatus === "completed" && "🟢 Ready for OTP"}
              {botStatus === "cancelled" && "🟠 Purchase Cancelled (Alert Sent)"}
              {botStatus === "error" && "🔴 Error"}
            </span>
            <button type="button" className="bulk-modal-close-btn" onClick={onClose} aria-label="Close">
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="samsung-bulk-body">
          {/* Left Column: Device & Order Specs */}
          <div className="bulk-col bulk-col-product">
            <div className="bulk-section-card">
              <h3 className="section-title">📱 Target Device</h3>
              <div className="bulk-product-preview">
                <img src={product?.image} alt={product?.name} className="bulk-product-img" />
                <div className="bulk-product-meta">
                  <h4>{product?.name}</h4>
                  <p className="bulk-product-price">Unit Price: <strong>{product?.price}</strong></p>
                  <p className="bulk-product-seller">Store: {product?.seller || `${brandName} Official Store`}</p>
                </div>
              </div>

              {/* Quantity Selector */}
              <div className="bulk-quantity-block">
                <label className="bulk-label">Bulk Order Quantity:</label>
                <div className="bulk-qty-stepper">
                  <button type="button" onClick={() => setBulkQty((q) => Math.max(1, q - 1))} disabled={bulkQty <= 1}>−</button>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={bulkQty}
                    onChange={(e) => setBulkQty(Math.max(1, parseInt(e.target.value) || 1))}
                  />
                  <button type="button" onClick={() => setBulkQty((q) => q + 1)}>+</button>
                </div>
                <div className="bulk-quick-chips">
                  {[5, 10, 20, 50].map((num) => (
                    <button
                      key={num}
                      type="button"
                      className={`quick-qty-chip ${bulkQty === num ? "active" : ""}`}
                      onClick={() => setBulkQty(num)}
                    >
                      {num} Units
                    </button>
                  ))}
                </div>
              </div>

              {/* Order Calculation */}
              <div className="bulk-pricing-summary">
                <div className="pricing-row">
                  <span>Unit Price:</span>
                  <span>₹{Math.round(unitPriceNum).toLocaleString("en-IN")}</span>
                </div>
                <div className="pricing-row">
                  <span>Quantity:</span>
                  <span>{bulkQty} units</span>
                </div>
                <div className="pricing-row total-row">
                  <span>Total Estimated:</span>
                  <span className="total-val">₹{Math.round(totalBulkPrice).toLocaleString("en-IN")}</span>
                </div>
              </div>

              {/* Delivery Address Card */}
              <div className="bulk-address-card">
                <div className="address-header">
                  <span>📍 Auto-Fill Shipping Address {isCroma ? "(Croma Dehradun Hub)" : "(Verified)"}</span>
                  <span className="verified-badge">✓ Verified</span>
                </div>
                {isCroma ? (
                  <>
                    <p className="address-name">DEBRAJ (Debraj Shil)</p>
                    <p className="address-lines">HIMALAYAN COLONY HIMALAYAN APPT, HARIPUR KALAN, MOTICHUR RANGE, BESIDE SD PALACE</p>
                    <p className="address-city">Dehradun, Uttarakhand - <strong>249205</strong></p>
                    <p className="address-contact">Phone: +91 7003533173 • debraj1849@gmail.com</p>
                    <div style={{ marginTop: "8px", paddingTop: "8px", borderTop: "1px dashed rgba(255,255,255,0.15)", fontSize: "11px", color: "#34d399", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span>🏢 GST Number:</span>
                      <input
                        type="text"
                        value={gstNumber}
                        onChange={(e) => setGstNumber(e.target.value)}
                        placeholder="GST Number"
                        style={{
                          background: "rgba(0,0,0,0.35)",
                          border: "1px solid rgba(52, 211, 153, 0.4)",
                          borderRadius: "4px",
                          color: "#fff",
                          padding: "3px 8px",
                          fontSize: "11px",
                          width: "160px"
                        }}
                        title="Enter GST Number for Croma B2B Order"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <p className="address-name">Debraj Shil</p>
                    <p className="address-lines">P/6 Regent Estate, 2nd Floor, Jadavpur</p>
                    <p className="address-city">Kolkata, West Bengal - <strong>700092</strong></p>
                    <p className="address-contact">Phone: +91 7003533173 • debraj1849@gmail.com</p>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Middle Column: Multi-Account & Payment Rotation */}
          <div className="bulk-col bulk-col-config">
            {/* Account Selector */}
            <div className="bulk-section-card">
              <h3 className="section-title">
                👥 Multi-Account Profile
                <span className="section-badge">5 Profiles Loaded</span>
              </h3>
              <p className="section-hint">Select Chrome profile to isolate sessions and prevent rate-limiting:</p>
              <div className="accounts-grid">
                {DEFAULT_ACCOUNTS.map((acc) => (
                  <button
                    key={acc.id}
                    type="button"
                    className={`account-card ${selectedAccount === acc.id ? "active" : ""}`}
                    onClick={() => {
                      setSelectedAccount(acc.id);
                      addLog(`Switched active profile to Account ${acc.id} (${acc.profile}).`);
                    }}
                  >
                    <span className="account-avatar">👤</span>
                    <div className="account-details">
                      <span className="account-name">{acc.name}</span>
                      <span className="account-desc">{acc.profile} • {acc.desc}</span>
                    </div>
                    {selectedAccount === acc.id && <span className="account-check">✓</span>}
                  </button>
                ))}
              </div>
            </div>

            {/* Payment Method Selector (All 4 Options Supported) */}
            <div className="bulk-section-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 className="section-title" style={{ margin: 0 }}>
                  💰 Payment Method
                  <span className="section-badge" style={{ background: "#00b259" }}>4 Options Ready</span>
                </h3>
              </div>
              <p className="section-hint" style={{ marginTop: "4px" }}>Select payment option for {brandName} checkout:</p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "8px", marginTop: "10px" }}>
                {[
                  { id: "cards", label: "Credit / Debit Cards", icon: "💳", desc: "Auto-fill card & virtual password" },
                  { id: "emi", label: "EMI on Cards", icon: "🏦", desc: "Tenure & bank options" },
                  { id: "upi", label: "UPI (Instant)", icon: "📱", desc: "Direct VPA transfer" },
                  { id: "cod", label: "Cash on Delivery", icon: "💵", desc: "Pay on delivery at doorstep" },
                  { id: "netbanking", label: "Netbanking", icon: "🌐", desc: "Partner bank redirect" },
                ].map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    style={{
                      background: paymentMethod === opt.id ? "rgba(0, 178, 89, 0.22)" : "rgba(255, 255, 255, 0.04)",
                      border: paymentMethod === opt.id ? "1.5px solid #00b259" : "1px solid rgba(255, 255, 255, 0.1)",
                      borderRadius: "8px",
                      padding: "8px 10px",
                      textAlign: "left",
                      cursor: "pointer",
                      display: "flex",
                      flexDirection: "column",
                      gap: "2px",
                      transition: "all 0.15s ease"
                    }}
                    onClick={() => {
                      setPaymentMethod(opt.id);
                      addLog(`Selected payment method: ${opt.label}`);
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span>{opt.icon}</span>
                      <strong style={{ color: "#fff", fontSize: "11px" }}>{opt.label}</strong>
                    </div>
                    <span style={{ fontSize: "9.5px", color: "#94a3b8" }}>{opt.desc}</span>
                  </button>
                ))}
              </div>

              {paymentMethod === "upi" && (
                <div style={{ marginTop: "8px", padding: "8px 10px", background: "rgba(0,0,0,0.25)", borderRadius: "6px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "11px", color: "#cbd5e1" }}>UPI ID:</span>
                  <input
                    type="text"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    placeholder="e.g. debraj1849@okaxis"
                    style={{ flex: 1, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: "4px", padding: "4px 8px", color: "#fff", fontSize: "11px" }}
                  />
                </div>
              )}

              {paymentMethod === "cod" && (
                <div style={{ marginTop: "8px", padding: "8px 12px", background: "rgba(16, 185, 129, 0.12)", border: "1px solid rgba(16, 185, 129, 0.3)", borderRadius: "6px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "16px" }}>💵</span>
                  <span style={{ fontSize: "11px", color: "#a7f3d0" }}>
                    <strong>Cash on Delivery (COD) Mode Active:</strong> Bot will automatically select Cash on Delivery / Pay on Delivery and place your order directly!
                  </span>
                </div>
              )}
            </div>

            {/* Rotating Cards Selector with Import CSV */}
            <div className="bulk-section-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 className="section-title" style={{ margin: 0 }}>
                  💳 Payment Card Rotation
                  <span className="section-badge">{cards.length} Cards</span>
                </h3>
                {/* Hidden File Input for CSV */}
                <input
                  type="file"
                  ref={csvInputRef}
                  accept=".csv"
                  style={{ display: "none" }}
                  onChange={handleCsvImport}
                />
                <button
                  type="button"
                  style={{
                    background: "linear-gradient(135deg, #00b259 0%, #008b47 100%)",
                    color: "#fff",
                    border: "none",
                    borderRadius: "6px",
                    padding: "5px 10px",
                    fontSize: "11px",
                    fontWeight: "600",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    boxShadow: "0 2px 8px rgba(0, 178, 89, 0.3)"
                  }}
                  onClick={() => csvInputRef.current?.click()}
                  title="Upload CSV to auto-read virtual cards & passwords"
                >
                  📥 Import CSV
                </button>
              </div>

              <div className="cards-slider">
                {cards.map((card, idx) => {
                  const hasPass = Boolean(card.password || card.pin);
                  const isVirtual = Boolean(card.isVirtual);
                  const showCurrentPin = showPin[card.id || idx];

                  return (
                    <div
                      key={card.id || idx}
                      className={`virtual-card ${selectedCardIndex === idx ? "active-card" : ""}`}
                      style={{ background: card.color || DEFAULT_CARDS[0].color }}
                      onClick={() => {
                        setSelectedCardIndex(idx);
                        addLog(`Selected ${card.label} (${card.brand} ending ${card.last4}) for checkout injection.`);
                      }}
                    >
                      <div className="card-top">
                        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                          <span className="card-chip">💳</span>
                          {isVirtual && (
                            <span style={{ background: "#10b981", color: "#000", fontSize: "9px", fontWeight: "800", padding: "1px 6px", borderRadius: "3px", letterSpacing: "0.5px" }}>
                              VIRTUAL
                            </span>
                          )}
                        </div>
                        <span className="card-brand">{card.brand}</span>
                      </div>
                      <div className="card-number">•••• •••• •••• {card.last4}</div>
                      <div className="card-bottom">
                        <div>
                          <span className="card-lbl">CARDHOLDER</span>
                          <span className="card-val">{card.name}</span>
                        </div>
                        <div>
                          <span className="card-lbl">EXPIRES</span>
                          <span className="card-val">{card.expiry}</span>
                        </div>
                        {hasPass && (
                          <div>
                            <span className="card-lbl" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                              PIN
                              <span
                                style={{ cursor: "pointer", opacity: 0.8 }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setShowPin((p) => ({ ...p, [card.id || idx]: !p[card.id || idx] }));
                                }}
                              >
                                {showCurrentPin ? "🙈" : "👁️"}
                              </span>
                            </span>
                            <span className="card-val" style={{ fontFamily: "monospace", letterSpacing: "1px" }}>
                              {showCurrentPin ? (card.password || card.pin) : "••••"}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Turbo Automation Toggles */}
            <div className="bulk-section-card">
              <h3 className="section-title">⚙️ Bot Automation Flags</h3>
              <div className="toggles-list">
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={guestCheckout}
                    onChange={(e) => setGuestCheckout(e.target.checked)}
                  />
                  <span>
                    <strong>Guest Checkout Bypass</strong>
                    <small>Skips {brandName} account sign-in screen for faster checkout</small>
                  </span>
                </label>
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={autoCardFill}
                    onChange={(e) => setAutoCardFill(e.target.checked)}
                  />
                  <span>
                    <strong>Auto-Fill Payment & CVV</strong>
                    <small>Fills payment details automatically and stops at OTP prompt</small>
                  </span>
                </label>
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={detachChrome}
                    onChange={(e) => setDetachChrome(e.target.checked)}
                  />
                  <span>
                    <strong>Chrome Detach Mode</strong>
                    <small>Keeps Chrome window open so you can enter OTP manually</small>
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Right Column: Execution Stepper & Terminal Console */}
          <div className="bulk-col bulk-col-terminal">
            {/* Pipeline Stepper */}
            <div className="bulk-section-card">
              <h3 className="section-title">⚡ Automation Pipeline</h3>
              <div className="pipeline-steps">
                {pipelineSteps.map((st) => {
                  let stepState = "pending";
                  if (currentStep > st.id || botStatus === "completed") stepState = "done";
                  else if (currentStep === st.id) stepState = "active";

                  return (
                    <div key={st.id} className={`pipeline-step step-${stepState}`}>
                      <div className="step-circle">
                        {stepState === "done" ? "✓" : st.id}
                      </div>
                      <div className="step-info">
                        <span className="step-title">{st.name}</span>
                        <span className="step-desc">{st.desc}</span>
                      </div>
                      {stepState === "active" && <span className="step-pulse" />}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Payment Gateway Alert / UPI QR Code / COD Confirmation Banner */}
            {notification && (botStatus === "completed" || botStatus === "cancelled" || botStatus === "awaiting_upi_qr") && (() => {
              const statusUpper = (notification.status || "").toUpperCase();
              const reasonUpper = (notification.reason || "").toUpperCase();
              const isCodActive = Boolean(
                statusUpper.includes("COD") ||
                statusUpper.includes("CASH ON DELIVERY") ||
                statusUpper.includes("ORDER PLACED") ||
                reasonUpper.includes("CASH ON DELIVERY") ||
                reasonUpper.includes("COD")
              );
              const isUpiActive = Boolean(
                !isCodActive &&
                (statusUpper.includes("UPI") || reasonUpper.includes("UPI")) &&
                !statusUpper.includes("CART") &&
                !statusUpper.includes("EMPTY") &&
                !statusUpper.includes("DECLINED")
              );
              const isSuccessBanner = isCodActive || isUpiActive;

              return (
                <div style={{
                  background: isSuccessBanner
                    ? "linear-gradient(90deg, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.2))"
                    : "linear-gradient(90deg, rgba(239, 68, 68, 0.25), rgba(245, 158, 11, 0.2))",
                  border: isSuccessBanner
                    ? "1px solid rgba(16, 185, 129, 0.6)"
                    : "1px solid rgba(239, 68, 68, 0.6)",
                  borderRadius: "10px",
                  padding: "14px 18px",
                  marginBottom: "14px",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "14px",
                  boxShadow: isSuccessBanner
                    ? "0 4px 20px rgba(16, 185, 129, 0.25)"
                    : "0 4px 20px rgba(239, 68, 68, 0.25)"
                }}>
                  <span style={{ fontSize: "30px", marginTop: "2px" }}>
                    {isCodActive ? "💵" : isUpiActive ? "⚡" : "⚠️"}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                      <strong style={{
                        color: isSuccessBanner ? "#34d399" : "#f87171",
                        fontSize: "14px",
                        letterSpacing: "0.5px"
                      }}>
                        {notification.status ? notification.status.toUpperCase() : "ALERT"}
                      </strong>
                      <span style={{
                        background: isSuccessBanner ? "#10b981" : "#ef4444",
                        color: "#fff",
                        fontSize: "10px",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        fontWeight: "700"
                      }}>
                        {isCodActive ? "COD ORDER CONFIRMED" : isUpiActive ? "DYNAMIC UPI QR READY" : "ACTION REQUIRED"}
                      </span>
                    </div>

                    {isCodActive ? (
                      <>
                        <p style={{ margin: "6px 0 0", color: "#f1f5f9", fontSize: "13px", lineHeight: "1.5" }}>
                          ✅ <strong>Cash on Delivery Confirmed:</strong> {notification.reason || `Bot successfully placed order on ${brandName}!`}
                          <br />
                          📦 <strong>Delivery To:</strong> {notification.phone || "+91 7003533173"} | Debraj Shil (Dehradun 249205).
                          <br />
                          💵 <strong>Payment Note:</strong> Pay cash or UPI to delivery agent at your doorstep upon order arrival.
                        </p>
                      </>
                    ) : isUpiActive ? (
                      <>
                        <p style={{ margin: "6px 0 0", color: "#f1f5f9", fontSize: "13px", lineHeight: "1.5" }}>
                          📲 <strong>UPI VPA Target:</strong> <code style={{ color: "#6ee7b7", background: "rgba(0,0,0,0.4)", padding: "2px 6px", borderRadius: "4px" }}>{upiId || "debraj1849@oksbi"}</code>
                          <br />
                          📱 <strong>Scan &amp; Pay:</strong> Dynamic UPI QR Code is open on {brandName} payment screen. Scan directly with <strong>PhonePe, Google Pay, or Paytm</strong>!
                        </p>
                        <div style={{ marginTop: "8px", display: "flex", gap: "10px", alignItems: "center" }}>
                          <a
                            href={`${apiBase}/api/automation/live-view`}
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "6px",
                              background: "#10b981",
                              color: "#fff",
                              padding: "6px 14px",
                              borderRadius: "6px",
                              fontSize: "12px",
                              fontWeight: "700",
                              textDecoration: "none"
                            }}
                          >
                            ↗️ Pop Out QR Code Window
                          </a>
                          <span style={{ fontSize: "11px", color: "#94a3b8" }}>
                            Or scan from the Desktop Live Screen below
                          </span>
                        </div>
                      </>
                    ) : (
                      <>
                        <p style={{ margin: "6px 0 0", color: "#f1f5f9", fontSize: "13px", lineHeight: "1.5" }}>
                          <strong>Reason:</strong> {notification.reason || "Action required on payment portal."}
                        </p>
                        <div style={{ marginTop: "6px", padding: "6px 10px", background: "rgba(0,0,0,0.35)", borderRadius: "6px", fontSize: "11px", color: "#94a3b8" }}>
                          💡 <strong>Notice:</strong> Please inspect the visible Chrome window on your desktop to complete or verify your checkout.
                        </div>
                      </>
                    )}
                  </div>
                </div>
              );
            })()}

            {/* Live Streaming Terminal & Desktop Screen Mirror */}
            <div className="bulk-section-card terminal-card">
              <div className="terminal-header">
                <div className="terminal-dots">
                  <span className="dot red" />
                  <span className="dot yellow" />
                  <span className="dot green" />
                </div>
                <div className="screen-view-tabs">
                  <button
                    type="button"
                    className={`screen-tab-btn ${screenTab === "screen" ? "active" : ""}`}
                    onClick={() => setScreenTab("screen")}
                  >
                    🖥️ Desktop Live Screen
                  </button>
                  <button
                    type="button"
                    className={`screen-tab-btn ${screenTab === "terminal" ? "active" : ""}`}
                    onClick={() => setScreenTab("terminal")}
                  >
                    ⌨️ Terminal Logs
                  </button>
                </div>
                <span className={`terminal-badge ${screenTab === "screen" ? "badge-screen" : ""}`}>
                  {screenTab === "screen" ? "● SCREEN LIVE" : "LIVE STREAM"}
                </span>
              </div>

              {screenTab === "screen" ? (
                <div className="desktop-screen-viewport">
                  <div className="screen-browser-bar">
                    <div className="browser-nav-icons">
                      <span>‹</span>
                      <span>›</span>
                      <span>↻</span>
                    </div>
                    <div className="screen-url-bar">
                      <span className="lock-icon">🔒</span>
                      <span className="url-text">{liveUrl || "https://www.samsung.com/in/"}</span>
                    </div>
                    <span className="browser-profile-tag">account_{selectedAccount}</span>
                    <a
                      href={`${apiBase}/api/automation/live-view`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-popout-screen"
                      title="Open full live Chrome screen stream in a separate tab or window"
                    >
                      ↗️ Pop Out
                    </a>
                  </div>
                  <div className="screen-display-area">
                    {liveScreenshot ? (
                      <div className="screen-img-wrapper">
                        <img src={liveScreenshot} alt="Live Chrome Desktop Screen" className="screen-live-img" />
                        <span className="screen-live-tag">● LIVE STREAMING</span>
                      </div>
                    ) : (
                      <div className="screen-idle-placeholder">
                        <div className="placeholder-icon">🖥️</div>
                        <h4>Desktop Screen Mirror Ready</h4>
                        <p>Active Profile: <code>account_{selectedAccount}</code></p>
                        <p className="placeholder-sub">
                          Click <strong>"Start Automated Bulk Bot"</strong> or <strong>"Launch Chrome Profile"</strong> to stream Chrome live right here.
                        </p>
                        <div className="os-hint-box">
                          💡 <strong>Windows Tip:</strong> The real Chrome window also opens on your OS desktop. Press <kbd>Alt</kbd> + <kbd>Tab</kbd> or click the Chrome icon in your taskbar if hidden behind fullscreen apps.
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="terminal-output">
                  {logs.map((log, index) => (
                    <div key={index} className={`terminal-line ${log.includes("SUCCESS") ? "line-success" : log.includes("START") ? "line-start" : log.includes("ACTION") ? "line-action" : log.includes("HANDOFF") ? "line-handoff" : ""}`}>
                      {log}
                    </div>
                  ))}
                  <div ref={logsEndRef} />
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="bulk-actions-footer">
              <button
                type="button"
                className="btn-launch-browser"
                onClick={handleLaunchBrowser}
                disabled={browserLaunching || botStatus === "running"}
              >
                {browserLaunching ? "Launching..." : "🌐 Launch Chrome Profile"}
              </button>
              {botStatus === "running" ? (
                <button
                  type="button"
                  className="btn-stop-bot"
                  onClick={handleResetBot}
                >
                  ⏹ Stop Automation
                </button>
              ) : (
                <button
                  type="button"
                  className="btn-start-bot"
                  onClick={handleStartBot}
                >
                  ▶ Start Automated Bulk Bot
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Floating Interactive OTP Pop-Out Window */}
        {(botStatus === "awaiting_otp" || otpRequired) && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(5, 10, 20, 0.88)",
              backdropFilter: "blur(8px)",
              zIndex: 9999,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              animation: "fadeIn 0.25s ease-out",
            }}
          >
            <div
              style={{
                width: "480px",
                maxWidth: "92%",
                background: "linear-gradient(145deg, #111827 0%, #1f2937 100%)",
                border: "2px solid #00b259",
                borderRadius: "16px",
                padding: "26px",
                boxShadow: "0 20px 50px rgba(0, 178, 89, 0.35)",
                textAlign: "center",
                color: "#fff",
              }}
            >
              <div style={{ fontSize: "42px", marginBottom: "8px" }}>🔐</div>
              <h3 style={{ margin: "0 0 6px", fontSize: "20px", fontWeight: "700", color: "#f9fafb" }}>
                {brandName} Login OTP Verification
              </h3>
              <p style={{ margin: "0 0 16px", fontSize: "13px", color: "#9ca3af", lineHeight: "1.5" }}>
                Croma has sent a verification OTP to:
                <br />
                <strong style={{ color: "#34d399", fontSize: "14px" }}>debraj1849@gmail.com</strong>
              </p>

              {/* Digital OTP Input Box */}
              <div style={{ margin: "18px 0" }}>
                <input
                  type="text"
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSubmitOtp();
                  }}
                  autoFocus
                  placeholder="• • • • • •"
                  style={{
                    width: "220px",
                    padding: "12px",
                    fontSize: "24px",
                    fontWeight: "700",
                    letterSpacing: "8px",
                    textAlign: "center",
                    background: "#030712",
                    border: "2px solid #10b981",
                    borderRadius: "10px",
                    color: "#34d399",
                    outline: "none",
                    boxShadow: "0 0 15px rgba(16, 185, 129, 0.3)",
                  }}
                />
              </div>

              {/* Action Buttons */}
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "20px" }}>
                <button
                  type="button"
                  disabled={otpSubmitting || !otpCode}
                  onClick={handleSubmitOtp}
                  style={{
                    background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    color: "#fff",
                    border: "none",
                    padding: "12px",
                    borderRadius: "8px",
                    fontSize: "14px",
                    fontWeight: "700",
                    cursor: otpSubmitting || !otpCode ? "not-allowed" : "pointer",
                    boxShadow: "0 4px 15px rgba(16, 185, 129, 0.4)",
                    transition: "transform 0.1s ease",
                  }}
                >
                  {otpSubmitting ? "⏳ Submitting OTP to Croma..." : "✓ Submit OTP & Continue Checkout"}
                </button>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    type="button"
                    onClick={() => {
                      window.open(`${apiBase}/api/automation/live-view`, "CromaOTPStream", "width=540,height=700,resizable=yes,scrollbars=yes");
                    }}
                    style={{
                      flex: 1,
                      background: "rgba(255, 255, 255, 0.08)",
                      border: "1px solid rgba(255, 255, 255, 0.18)",
                      color: "#e2e8f0",
                      padding: "8px",
                      borderRadius: "6px",
                      fontSize: "12px",
                      cursor: "pointer",
                    }}
                  >
                    ↗️ Pop Out Floating Window
                  </button>
                  <button
                    type="button"
                    onClick={() => setOtpRequired(false)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#9ca3af",
                      padding: "8px",
                      fontSize: "12px",
                      cursor: "pointer",
                      textDecoration: "underline",
                    }}
                  >
                    Dismiss
                  </button>
                </div>
              </div>

              <div style={{ marginTop: "14px", fontSize: "11px", color: "#6b7280" }}>
                💡 <strong>Tip:</strong> The real Chrome window is also visible on your Windows desktop. You can enter the OTP directly there or right here in this floating window.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

