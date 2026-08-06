// ======================================
// AgriConnect Login
// login.js - Part 1
// ======================================

const API_BASE = "http://127.0.0.1:5000/api";

let currentRole = "farmer";

// ==========================
// Cached DOM Elements
// ==========================

const loginForm = document.getElementById("loginForm");
const identifier = document.getElementById("identifier");
const password = document.getElementById("password");

const submitBtn = document.getElementById("submitBtn");
const msgBox = document.getElementById("msgBox");

const tabFarmer = document.getElementById("tabFarmer");
const tabCustomer = document.getElementById("tabCustomer");

// ==========================
// Change User Role
// ==========================

function setRole(role){

    currentRole = role;

    tabFarmer.classList.toggle(
        "active",
        role === "farmer"
    );

    tabCustomer.classList.toggle(
        "active",
        role === "customer"
    );

}

// ==========================
// Message Box
// ==========================

function showMsg(text,type){

    msgBox.textContent = text;

    msgBox.className = `msg ${type}`;

}

// ==========================
// Clear Message
// ==========================

function clearMsg(){

    msgBox.textContent = "";

    msgBox.className = "msg";

}

// ==========================
// Input Validation
// ==========================

function validateForm(){

    clearMsg();

    if(identifier.value.trim()===""){

        showMsg(
            "Please enter your email or mobile number.",
            "error"
        );

        identifier.focus();

        return false;

    }

    if(password.value.trim()===""){

        showMsg(
            "Please enter your password.",
            "error"
        );

        password.focus();

        return false;

    }

    return true;

}
// ==========================
// Login Form Submit
// ==========================

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    if (!validateForm()) {

        return;

    }

    submitBtn.disabled = true;

    submitBtn.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';

    const payload = {

        user_type: currentRole,

        password: password.value

    };

    if (identifier.value.includes("@")) {

        payload.email = identifier.value.trim();

    } else {

        payload.mobile_number = identifier.value.trim();

    }

    try {

        const response = await fetch(`${API_BASE}/auth/login`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(payload)

        });

        const data = await response.json();

        if (data.success) {

            localStorage.setItem(
                "agri_token",
                data.access_token
            );

            localStorage.setItem(
                "agri_refresh",
                data.refresh_token
            );

            localStorage.setItem(
                "agri_user",
                JSON.stringify({
                    ...data.user,
                    user_type: data.user_type
                })
            );

            showMsg(
                "Login successful! Redirecting...",
                "success"
            );

            setTimeout(() => {

                window.location.href = "dashboard.html";

            }, 800);

        } else {

            showMsg(

                data.message || "Login failed.",

                "error"

            );

        }

    } catch (error) {

        console.error(error);

        showMsg(

            "Could not connect to the AgriConnect server.",

            "error"

        );

    } finally {

        submitBtn.disabled = false;

        submitBtn.innerHTML =
            '<i class="fa-solid fa-right-to-bracket"></i> Login';

    }

});
// ======================================
// Additional Features
// ======================================

// Allow Enter key to submit
document.addEventListener("keydown", (e) => {

    if (e.key === "Enter") {

        loginForm.requestSubmit();

    }

});

// Clear error message while typing
identifier.addEventListener("input", clearMsg);

password.addEventListener("input", clearMsg);

// Auto focus
window.addEventListener("load", () => {

    identifier.focus();

});

// Password visibility (works if you add a toggle icon later)
function togglePassword() {

    if (password.type === "password") {

        password.type = "text";

    } else {

        password.type = "password";

    }

}

// Prevent multiple submissions
let isSubmitting = false;

loginForm.addEventListener("submit", function (event) {

    if (isSubmitting) {

        event.preventDefault();

        return;

    }

    isSubmitting = true;

    setTimeout(() => {

        isSubmitting = false;

    }, 3000);

});

// Check existing login
const existingUser = localStorage.getItem("agri_user");

if (existingUser) {

    console.log("Existing user session found.");

}

// Console message
console.log("🌱 AgriConnect Login Page Loaded Successfully");