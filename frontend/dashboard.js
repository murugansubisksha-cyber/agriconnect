// ======================================
// AgriConnect Dashboard
// dashboard.js - Part 1
// ======================================

const API_BASE = "http://127.0.0.1:5000/api";

// ==========================
// DOM Elements
// ==========================

const username = document.getElementById("username");

const farmerCount = document.getElementById("farmerCount");

const customerCount = document.getElementById("customerCount");

const orderCount = document.getElementById("orderCount");

const productCount = document.getElementById("productCount");

const activityList = document.getElementById("activityList");

const recentOrders = document.getElementById("recentOrders");

const aiSummary = document.getElementById("aiSummary");

// ==========================
// Load Logged-in User
// ==========================

const currentUser = JSON.parse(

    localStorage.getItem("agri_user")

);

if(currentUser){

    username.textContent =

        currentUser.name ||

        currentUser.username ||

        "User";

}

// ==========================
// Dashboard Statistics
// ==========================

async function loadDashboardStats(){

    try{

        const response = await fetch(

            `${API_BASE}/dashboard/stats`,

            {

                headers:{

                    Authorization:
                    `Bearer ${localStorage.getItem("agri_token")}`

                }

            }

        );

        const data = await response.json();

        farmerCount.textContent =
            data.farmers || 0;

        customerCount.textContent =
            data.customers || 0;

        orderCount.textContent =
            data.orders || 0;

        productCount.textContent =
            data.products || 0;

    }

    catch(error){

        console.error(

            "Dashboard Statistics Error:",

            error

        );

    }

}

// ==========================
// Initialize
// ==========================

loadDashboardStats();
// ==========================
// Load Recent Orders
// ==========================

async function loadRecentOrders(){

    try{

        const response = await fetch(

            `${API_BASE}/orders`,

            {

                headers:{

                    Authorization:
                    `Bearer ${localStorage.getItem("agri_token")}`

                }

            }

        );

        const data = await response.json();

        recentOrders.innerHTML = "";

        if(!data.orders || data.orders.length === 0){

            recentOrders.innerHTML = `
                <tr>
                    <td colspan="2">
                        No recent orders found.
                    </td>
                </tr>
            `;

            return;

        }

        data.orders.slice(0,5).forEach(order=>{

            recentOrders.innerHTML += `
                <tr>
                    <td>#${order.id}</td>
                    <td>${order.status}</td>
                </tr>
            `;

        });

    }

    catch(error){

        console.error(

            "Recent Orders Error:",

            error

        );

    }

}

// ==========================
// Load Recent Activity
// ==========================

function loadActivity(){

    activityList.innerHTML = "";

    const activities = [

        "🌾 New farmer registered",

        "🛒 Customer placed an order",

        "📦 Order shipped",

        "🤖 AI crop prediction completed",

        "💬 New quotation received"

    ];

    activities.forEach(activity=>{

        const li = document.createElement("li");

        li.textContent = activity;

        activityList.appendChild(li);

    });

}

// ==========================
// Load AI Summary
// ==========================

function loadAISummary(){

    aiSummary.innerHTML =

        "AI Recommendation system is active. Crop prediction, soil analysis and weather-based recommendations are available for farmers.";

}

// ==========================
// Initialize Components
// ==========================

loadRecentOrders();

loadActivity();

loadAISummary();
// ======================================
// Dashboard Utilities
// dashboard.js - Part 3
// ======================================

// Refresh Dashboard Every 60 Seconds
setInterval(() => {

    loadDashboardStats();

    loadRecentOrders();

}, 60000);

// ==========================
// Logout
// ==========================

function logout() {

    localStorage.removeItem("agri_token");

    localStorage.removeItem("agri_refresh");

    localStorage.removeItem("agri_user");

    window.location.href = "login.html";

}

// ==========================
// Authentication Check
// ==========================

function checkAuthentication() {

    const token = localStorage.getItem("agri_token");

    if (!token) {

        window.location.href = "login.html";

    }

}

checkAuthentication();

// ==========================
// Welcome Message
// ==========================

const currentHour = new Date().getHours();

let greeting = "Welcome";

if (currentHour < 12) {

    greeting = "Good Morning";

}
else if (currentHour < 17) {

    greeting = "Good Afternoon";

}
else {

    greeting = "Good Evening";

}

const heading = document.querySelector(".topbar h2");

if (heading) {

    heading.textContent = `${greeting}, ${username.textContent}`;

}

// ==========================
// Card Hover Animation
// ==========================

document.querySelectorAll(".stat-card").forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-8px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0)";

    });

});

// ==========================
// Console Message
// ==========================

console.log("🌱 AgriConnect Dashboard Loaded Successfully");