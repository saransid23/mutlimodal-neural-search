/**
 * AURA Studio - Intelligent Visual Commerce Controller
 */

const API_BASE_URL = "http://127.0.0.1:8000";

// Global State
let selectedFile = null;
let currentSearchResults = [];
let filteredResults = [];

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "home") {
    initHomePage();
  } else if (page === "results") {
    initResultsPage();
  } else if (page === "product") {
    initProductPage();
  }
});

/* ==========================================================================
   Homepage Initialization & Event Handlers
   ========================================================================== */
function initHomePage() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const removeBtn = document.getElementById("removeImageBtn");
  const searchBtn = document.getElementById("searchBtn");
  const textInput = document.getElementById("textSearchInput");
  const lensToggleBtn = document.getElementById("lensToggleBtn");
  const lensStudioPopover = document.getElementById("lensStudioPopover");
  const promptChips = document.querySelectorAll(".prompt-chip");

  if (!dropzone || !fileInput) return;

  // Toggle Lens Popover
  if (lensToggleBtn && lensStudioPopover) {
    lensToggleBtn.addEventListener("click", () => {
      const isActive = lensStudioPopover.classList.toggle("active");
      lensToggleBtn.classList.toggle("active", isActive);
    });
  }

  // Click dropzone to open file dialog
  dropzone.addEventListener("click", () => fileInput.click());

  // File input change
  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  // Drag & Drop events
  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("drag-over");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    if (dt.files && dt.files[0]) {
      handleFileSelected(dt.files[0]);
    }
  });

  // Remove image
  if (removeBtn) {
    removeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      clearImageSelection();
    });
  }

  // Quick prompt chip click listeners
  promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const query = chip.dataset.query || chip.textContent.trim();
      if (textInput) {
        textInput.value = query;
        performSearch();
      }
    });
  });

  // Trigger search on Primary Search button click
  if (searchBtn) {
    searchBtn.addEventListener("click", () => performSearch());
  }

  // Trigger search on Enter key inside text input
  if (textInput) {
    textInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        performSearch();
      }
    });
  }
}

function handleFileSelected(file) {
  const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  if (!validTypes.includes(file.type)) {
    alert("Please select a valid image file (JPG, JPEG, PNG, or WEBP).");
    return;
  }

  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    alert("File size exceeds 5MB. Please upload a smaller image.");
    return;
  }

  selectedFile = file;

  // Render preview
  const reader = new FileReader();
  reader.onload = (e) => {
    const previewImg = document.getElementById("previewImage");
    const previewContainer = document.getElementById("previewContainer");
    const dropzoneContent = document.getElementById("dropzoneContent");
    const lensToggleBtn = document.getElementById("lensToggleBtn");
    const lensStudioPopover = document.getElementById("lensStudioPopover");

    if (previewImg && previewContainer) {
      previewImg.src = e.target.result;
      previewContainer.classList.add("active");
      if (dropzoneContent) dropzoneContent.style.display = "none";
    }
    if (lensStudioPopover) lensStudioPopover.classList.add("active");
    if (lensToggleBtn) lensToggleBtn.classList.add("active");
  };
  reader.readAsDataURL(file);
}

function clearImageSelection() {
  selectedFile = null;
  const fileInput = document.getElementById("fileInput");
  const previewContainer = document.getElementById("previewContainer");
  const dropzoneContent = document.getElementById("dropzoneContent");

  if (fileInput) fileInput.value = "";
  if (previewContainer) previewContainer.classList.remove("active");
  if (dropzoneContent) dropzoneContent.style.display = "block";
}

/* ==========================================================================
   Search Dispatcher
   ========================================================================== */
async function performSearch() {
  const textInput = document.getElementById("textSearchInput");
  const queryText = textInput ? textInput.value.trim() : "";

  if (!queryText && !selectedFile) {
    alert("Please enter a search query or upload an image to search.");
    return;
  }

  showLoading("Searching collection...");

  try {
    const formData = new FormData();
    let endpoint = "/search/multimodal";

    if (selectedFile && queryText) {
      // Multimodal Search
      formData.append("image", selectedFile);
      formData.append("query", queryText);
      formData.append("image_weight", 0.6);
      formData.append("text_weight", 0.4);
    } else if (selectedFile) {
      // Image Search
      endpoint = "/search/image";
      formData.append("image", selectedFile);
    } else {
      // Text Search
      endpoint = "/search/text";
    }

    let response;
    if (endpoint === "/search/text") {
      response = await fetch(`${API_BASE_URL}/search/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText, top_k: 15 })
      });
    } else {
      response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        body: formData
      });
    }

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || "Search request failed.");
    }

    const data = await response.json();

    // Cache results in sessionStorage and redirect to results.html
    sessionStorage.setItem("searchResults", JSON.stringify(data));
    sessionStorage.setItem("searchQuery", queryText);
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        sessionStorage.setItem("searchImageBase64", reader.result);
        window.location.href = "results.html";
      };
      reader.readAsDataURL(selectedFile);
    } else {
      sessionStorage.removeItem("searchImageBase64");
      window.location.href = "results.html";
    }

  } catch (error) {
    hideLoading();
    alert(`Search Error: ${error.message}`);
  }
}

/* ==========================================================================
   Results Page Renderer & Filters
   ========================================================================== */
function initResultsPage() {
  const cachedDataStr = sessionStorage.getItem("searchResults");
  const searchQuery = sessionStorage.getItem("searchQuery") || "";
  const searchImageBase64 = sessionStorage.getItem("searchImageBase64");

  const queryBadge = document.getElementById("queryBadge");
  const uploadedThumb = document.getElementById("uploadedThumb");
  const resultCount = document.getElementById("resultCount");

  if (queryBadge) {
    queryBadge.textContent = searchQuery ? `"${searchQuery}"` : (searchImageBase64 ? "Visual Lens Search" : "All Products");
  }

  if (uploadedThumb) {
    if (searchImageBase64) {
      uploadedThumb.src = searchImageBase64;
      uploadedThumb.style.display = "block";
    } else {
      uploadedThumb.style.display = "none";
    }
  }

  // Check URL category filter
  const urlParams = new URLSearchParams(window.location.search);
  const categoryParam = urlParams.get("category");

  if (categoryParam) {
    fetchProductsByCategory(categoryParam);
    return;
  }

  if (cachedDataStr) {
    const data = JSON.parse(cachedDataStr);
    currentSearchResults = data.results || [];
    if (resultCount) resultCount.textContent = `${currentSearchResults.length} Products Found`;
    applyFiltersAndRender();
  } else {
    fetchAllProducts();
  }

  setupFilterListeners();
}

async function fetchAllProducts() {
  showLoading("Fetching products...");
  try {
    const res = await fetch(`${API_BASE_URL}/products`);
    const products = await res.json();
    currentSearchResults = products.map(p => ({ ...p, similarity: 100.0 }));
    const resultCount = document.getElementById("resultCount");
    if (resultCount) resultCount.textContent = `${currentSearchResults.length} Products Found`;
    applyFiltersAndRender();
  } catch (e) {
    alert("Failed to load products from server.");
  } finally {
    hideLoading();
  }
}

async function fetchProductsByCategory(cat) {
  showLoading(`Loading ${cat}...`);
  try {
    const res = await fetch(`${API_BASE_URL}/products`);
    const products = await res.json();
    const filtered = products.filter(p => p.category.toLowerCase() === cat.toLowerCase());
    currentSearchResults = filtered.map(p => ({ ...p, similarity: 100.0 }));
    
    const queryBadge = document.getElementById("queryBadge");
    if (queryBadge) queryBadge.textContent = `Category: ${cat}`;

    const categoryFilterSelect = document.getElementById("categoryFilter");
    if (categoryFilterSelect) categoryFilterSelect.value = cat;

    const resultCount = document.getElementById("resultCount");
    if (resultCount) resultCount.textContent = `${currentSearchResults.length} Products Found`;
    
    applyFiltersAndRender();
  } catch (e) {
    alert("Failed to filter products.");
  } finally {
    hideLoading();
  }
}

function setupFilterListeners() {
  const categoryFilter = document.getElementById("categoryFilter");
  const minPriceInput = document.getElementById("minPrice");
  const maxPriceInput = document.getElementById("maxPrice");
  const minSimInput = document.getElementById("minSimilarity");
  const applyBtn = document.getElementById("applyFiltersBtn");

  if (applyBtn) {
    applyBtn.addEventListener("click", () => applyFiltersAndRender());
  }

  if (minSimInput) {
    minSimInput.addEventListener("input", (e) => {
      const valLabel = document.getElementById("similarityVal");
      if (valLabel) valLabel.textContent = `${e.target.value}%`;
    });
  }
}

function applyFiltersAndRender() {
  const categoryFilter = document.getElementById("categoryFilter")?.value || "All";
  const minPrice = parseFloat(document.getElementById("minPrice")?.value) || 0;
  const maxPrice = parseFloat(document.getElementById("maxPrice")?.value) || 999999;
  const minSim = parseFloat(document.getElementById("minSimilarity")?.value) || 0;

  filteredResults = currentSearchResults.filter((product) => {
    const matchCat = (categoryFilter === "All") || (product.category.toLowerCase() === categoryFilter.toLowerCase());
    const matchPrice = product.price >= minPrice && product.price <= maxPrice;
    const matchSim = (product.similarity === undefined) || (product.similarity >= minSim);

    return matchCat && matchPrice && matchSim;
  });

  renderProductGrid(filteredResults);
}

function renderProductGrid(products) {
  const grid = document.getElementById("productsGrid");
  if (!grid) return;

  if (products.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; margin-bottom: 0.5rem; color: var(--text-main);">No Products Match Criteria</h3>
        <p>Try refining your search text, uploading a clearer reference photo, or broadening filters.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = products.map((product) => {
    const similarityBadge = product.similarity !== undefined ? `
      <div class="similarity-badge">
        Match ${product.similarity}%
      </div>
    ` : "";

    const imageSrc = `${API_BASE_URL}/${product.image}`;

    return `
      <div class="product-card">
        <div class="card-img-wrapper">
          <img src="${imageSrc}" alt="${product.name}" class="product-card-img" onerror="this.src='https://via.placeholder.com/300?text=Product+Image'">
          ${similarityBadge}
        </div>
        <div class="card-body">
          <span class="product-category">${product.category}</span>
          <h3 class="product-title">${product.name}</h3>
          <div class="product-price">₹${product.price.toLocaleString('en-IN')}</div>
          <a href="product.html?id=${product.id}&sim=${product.similarity || ''}" class="btn-view-product">View Specs</a>
        </div>
      </div>
    `;
  }).join("");
}

/* ==========================================================================
   Product Details Page Logic
   ========================================================================== */
async function initProductPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get("id");
  const similarityScore = urlParams.get("sim");

  if (!productId) {
    alert("No product specified.");
    window.location.href = "index.html";
    return;
  }

  showLoading("Loading product details...");

  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);
    if (!response.ok) {
      throw new Error("Product not found.");
    }

    const product = await response.json();

    const productTitle = document.getElementById("productTitle");
    const productCategory = document.getElementById("productCategory");
    const productPrice = document.getElementById("productPrice");
    const productDesc = document.getElementById("productDescription");
    const productImage = document.getElementById("productImage");
    const detailBadge = document.getElementById("detailSimilarityBadge");
    const similarBtn = document.getElementById("findSimilarBtn");

    if (productTitle) productTitle.textContent = product.name;
    if (productCategory) productCategory.textContent = product.category;
    if (productPrice) productPrice.textContent = `₹${product.price.toLocaleString('en-IN')}`;
    if (productDesc) productDesc.textContent = product.description;
    if (productImage) productImage.src = `${API_BASE_URL}/${product.image}`;

    if (detailBadge && similarityScore) {
      detailBadge.innerHTML = `Match ${similarityScore}%`;
      detailBadge.style.display = "inline-block";
    }

    if (similarBtn) {
      similarBtn.addEventListener("click", async () => {
        showLoading("Searching visually similar items...");
        try {
          const imgResponse = await fetch(`${API_BASE_URL}/${product.image}`);
          const blob = await imgResponse.blob();
          const file = new File([blob], "product_image.jpg", { type: blob.type });

          const formData = new FormData();
          formData.append("image", file);

          const searchRes = await fetch(`${API_BASE_URL}/search/image`, {
            method: "POST",
            body: formData
          });

          if (!searchRes.ok) throw new Error("Search failed.");
          const searchData = await searchRes.json();

          sessionStorage.setItem("searchResults", JSON.stringify(searchData));
          sessionStorage.setItem("searchQuery", `Visually similar to ${product.name}`);
          
          const reader = new FileReader();
          reader.onload = () => {
            sessionStorage.setItem("searchImageBase64", reader.result);
            window.location.href = "results.html";
          };
          reader.readAsDataURL(file);

        } catch (err) {
          hideLoading();
          alert(`Error: ${err.message}`);
        }
      });
    }

  } catch (error) {
    alert(error.message);
    window.location.href = "index.html";
  } finally {
    hideLoading();
  }
}

/* ==========================================================================
   Loading Overlay Helper
   ========================================================================== */
function showLoading(message = "Processing request...") {
  const overlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  if (loadingText) loadingText.textContent = message;
  if (overlay) overlay.classList.add("active");
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.classList.remove("active");
}
