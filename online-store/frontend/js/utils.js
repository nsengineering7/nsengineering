// ============================================================
// Kharat E-Commerce — Shared Utilities (utils.js)
// No ES modules — plain global functions
// ============================================================

var API_BASE = "http://localhost:8000";

// ── Auth ─────────────────────────────────────────────────────
function getToken() {
  return localStorage.getItem("kharat_token") || null;
}

function getUser() {
  try {
    var raw = localStorage.getItem("kharat_user");
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function setAuth(token, user) {
  localStorage.setItem("kharat_token", token);
  localStorage.setItem("kharat_user", JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem("kharat_token");
  localStorage.removeItem("kharat_user");
}

// ── Cart ──────────────────────────────────────────────────────
function getCart() {
  try {
    var raw = localStorage.getItem("kharat_cart");
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function setCart(cart) {
  localStorage.setItem("kharat_cart", JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(product) {
  var cart = getCart();
  var existing = cart.find(function (item) {
    return item.product_id === product.product_id;
  });
  if (existing) {
    existing.quantity += product.quantity || 1;
  } else {
    cart.push({
      product_id: product.product_id,
      name: product.name,
      price: product.price,
      quantity: product.quantity || 1,
      image_url: product.image_url || ""
    });
  }
  setCart(cart);
}

function removeFromCart(productId) {
  var cart = getCart().filter(function (item) {
    return item.product_id !== productId;
  });
  setCart(cart);
}

function updateCartBadge() {
  var cart = getCart();
  var total = cart.reduce(function (sum, item) {
    return sum + item.quantity;
  }, 0);
  var badges = document.querySelectorAll(".cart-badge");
  badges.forEach(function (badge) {
    badge.textContent = total;
    badge.style.display = total > 0 ? "flex" : "none";
  });
}

// ── API Fetch ─────────────────────────────────────────────────
function apiFetch(path, options) {
  options = options || {};
  var headers = options.headers || {};
  var token = getToken();
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }
  options.headers = headers;
  return fetch(API_BASE + path, options);
}

// ── Toast Notifications ───────────────────────────────────────
function showToast(message, type) {
  type = type || "info";
  var container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.cssText =
      "position:fixed;top:1.25rem;right:1.25rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;pointer-events:none;";
    document.body.appendChild(container);
  }

  var colors = {
    success: "border-green-400 text-green-400",
    error: "border-red-400 text-red-400",
    info: "border-amber-400 text-amber-400",
    warning: "border-yellow-400 text-yellow-400"
  };
  var icons = {
    success: "check-circle",
    error: "x-circle",
    info: "info",
    warning: "alert-triangle"
  };

  var toast = document.createElement("div");
  toast.className =
    "flex items-center gap-3 px-4 py-3 bg-slate-800 border-l-4 " +
    (colors[type] || colors.info) +
    " shadow-xl text-slate-100 text-sm font-medium min-w-64 max-w-sm pointer-events-auto";
  toast.style.cssText =
    "transform:translateX(120%);transition:transform 0.3s ease;border-radius:2px;";
  toast.innerHTML =
    '<i data-lucide="' +
    (icons[type] || "info") +
    '" class="w-4 h-4 flex-shrink-0 ' +
    (colors[type] || colors.info).split(" ")[1] +
    '"></i><span>' +
    message +
    "</span>";

  container.appendChild(toast);
  if (window.lucide) lucide.createIcons({ nodes: [toast] });

  // Slide in
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      toast.style.transform = "translateX(0)";
    });
  });

  // Auto-dismiss after 3s
  setTimeout(function () {
    toast.style.transform = "translateX(120%)";
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 350);
  }, 3000);
}

// ── Formatting ────────────────────────────────────────────────
function formatCurrency(amount) {
  if (amount === null || amount === undefined || isNaN(amount)) return "PKR 0";
  return (
    "PKR " +
    Number(amount)
      .toFixed(0)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",")
  );
}

function formatDate(isoString) {
  if (!isoString) return "—";
  try {
    var d = new Date(isoString);
    return d.toLocaleDateString("en-PK", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    return isoString;
  }
}

function getStatusColor(status) {
  var map = {
    pending: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
    confirmed: "bg-blue-500/20 text-blue-400 border border-blue-500/30",
    processing: "bg-purple-500/20 text-purple-400 border border-purple-500/30",
    shipped: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
    delivered: "bg-green-500/20 text-green-400 border border-green-500/30",
    cancelled: "bg-red-500/20 text-red-400 border border-red-500/30"
  };
  return map[(status || "").toLowerCase()] || "bg-slate-600/40 text-slate-300 border border-slate-600";
}

// ── Navbar Auth State ─────────────────────────────────────────
function initNavbar() {
  var token = getToken();
  var user = getUser();
  var guestLinks = document.getElementById("nav-guest");
  var userMenu = document.getElementById("nav-user");
  var userNameEl = document.getElementById("nav-username");
  var adminLink = document.getElementById("nav-admin");

  if (token && user) {
    if (guestLinks) guestLinks.style.display = "none";
    if (userMenu) userMenu.style.display = "flex";
    if (userNameEl) userNameEl.textContent = user.full_name || user.email || "User";
    if (adminLink) adminLink.style.display = user.is_admin ? "block" : "none";
  } else {
    if (guestLinks) guestLinks.style.display = "flex";
    if (userMenu) userMenu.style.display = "none";
    if (adminLink) adminLink.style.display = "none";
  }

  var logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      clearAuth();
      window.location.href = "index.html";
    });
  }

  // Mobile hamburger
  var hamburger = document.getElementById("hamburger-btn");
  var mobileMenu = document.getElementById("mobile-menu");
  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", function () {
      mobileMenu.classList.toggle("hidden");
    });
  }

  updateCartBadge();
}

