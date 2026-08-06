// ==========================
// AgriConnect - index.js
// Part 1
// ==========================

// API Base URL
const API_BASE = "";

// DOM Elements
const loadingScreen = document.getElementById("loadingScreen");
const productGrid = document.getElementById("productGrid");
const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const toast = document.getElementById("toast");
const menuBtn = document.getElementById("menuBtn");

const farmerCount = document.getElementById("farmerCount");
const productCount = document.getElementById("productCount");
const customerCount = document.getElementById("customerCount");

// ==========================
// Page Loading
// ==========================

window.addEventListener("load", () => {

    setTimeout(() => {

        loadingScreen.style.display = "none";

    }, 700);

    loadProducts();

    loadStatistics();

});

// ==========================
// Toast Notification
// ==========================

function showToast(message, type = "success") {

    toast.textContent = message;

    if (type === "error") {

        toast.style.background = "#e53935";

    } else {

        toast.style.background = "#2E7D32";

    }

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}

// ==========================
// Load Statistics
// ==========================

function loadStatistics() {

    farmerCount.textContent = "250+";

    productCount.textContent = "1200+";

    customerCount.textContent = "500+";

}

// ==========================
// Load Products
// ==========================

async function loadProducts() {

    try {

        const response = await fetch(`${API_BASE}/api/products/`);

        if (!response.ok) {

            throw new Error("Unable to fetch products");

        }

        const products = await response.json();

        displayProducts(products);

    }

    catch (error) {

        console.error(error);

        showToast("Failed to load products", "error");

    }

}
// ==========================
// Display Products
// ==========================

function displayProducts(products) {

    productGrid.innerHTML = "";

    if (!products || products.length === 0) {

        productGrid.innerHTML = `
            <div class="no-products">
                <h3>No Products Found</h3>
                <p>Please check again later.</p>
            </div>
        `;

        return;
    }

    products.forEach(product => {

        const card = document.createElement("div");

        card.className = "product-card";

        card.innerHTML = `

            <img src="${product.image || 'https://via.placeholder.com/400x250'}"
                 alt="${product.name}">

            <div class="product-content">

                <h3>${product.name}</h3>

                <p>${product.description || "Fresh farm product"}</p>

                <div class="product-price">
                    ₹${product.price}
                </div>

                <button onclick="viewProduct(${product.id})">
                    View Details
                </button>

            </div>

        `;

        productGrid.appendChild(card);

    });

}

// ==========================
// View Product
// ==========================

function viewProduct(productId) {

    window.location.href = `product.html?id=${productId}`;

}

// ==========================
// Search Products
// ==========================

searchInput.addEventListener("keyup", function () {

    const keyword = this.value.toLowerCase();

    const cards = document.querySelectorAll(".product-card");

    cards.forEach(card => {

        const text = card.innerText.toLowerCase();

        if (text.includes(keyword)) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

});

// ==========================
// Category Filter
// ==========================

categoryFilter.addEventListener("change", function () {

    const category = this.value.toLowerCase();

    const cards = document.querySelectorAll(".product-card");

    cards.forEach(card => {

        if (
            category === "" ||
            card.innerText.toLowerCase().includes(category)
        ) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

});
// ==========================
// Mobile Menu
// ==========================

menuBtn.addEventListener("click", () => {

    const navbar = document.querySelector(".navbar");

    if (navbar.style.display === "flex") {

        navbar.style.display = "none";

    } else {

        navbar.style.display = "flex";

        navbar.style.flexDirection = "column";

    }

});

// ==========================
// Active Navigation
// ==========================

const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach(link => {

    link.addEventListener("click", function () {

        navLinks.forEach(item => {

            item.classList.remove("active");

        });

        this.classList.add("active");

    });

});

// ==========================
// Smooth Scroll
// ==========================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));

        if (target) {

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});

// ==========================
// Check Logged-in User
// ==========================

const currentUser = localStorage.getItem("agri_user");

if (currentUser) {

    console.log("Logged in:", currentUser);

}

// ==========================
// Utility Functions
// ==========================

function formatCurrency(price) {

    return `₹${Number(price).toLocaleString("en-IN")}`;

}

function formatDate(date) {

    return new Date(date).toLocaleDateString("en-IN");

}

// ==========================
// Error Handler
// ==========================

window.addEventListener("error", function (event) {

    console.error(event.error);

});

// ==========================
// Console Message
// ==========================

console.log("🌱 AgriConnect Home Page Loaded Successfully");