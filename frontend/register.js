// ======================================
// AgriConnect Register
// register.js - Part 1
// ======================================

const API_BASE = "http://127.0.0.1:5000/api";

const form = document.getElementById("registerForm");
const message = document.getElementById("message");

const registerBtn = document.getElementById("registerBtn");

const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const phoneInput = document.getElementById("phone");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");
const userTypeInput = document.getElementById("userType");

// ==========================
// Message Box
// ==========================

function showMessage(text, type){

    message.innerText = text;

    message.className = `message ${type}`;

}

// ==========================
// Clear Message
// ==========================

function clearMessage(){

    message.innerText = "";

    message.className = "message";

}

// ==========================
// Validation
// ==========================

function validateForm(){

    clearMessage();

    if(nameInput.value.trim() === ""){

        showMessage("Please enter your full name.","error");

        nameInput.focus();

        return false;

    }

    if(emailInput.value.trim() === ""){

        showMessage("Please enter your email.","error");

        emailInput.focus();

        return false;

    }

    if(phoneInput.value.trim() === ""){

        showMessage("Please enter your phone number.","error");

        phoneInput.focus();

        return false;

    }

    if(passwordInput.value.length < 6){

        showMessage("Password must contain at least 6 characters.","error");

        passwordInput.focus();

        return false;

    }

    if(passwordInput.value !== confirmPasswordInput.value){

        showMessage("Passwords do not match.","error");

        confirmPasswordInput.focus();

        return false;

    }

    if(userTypeInput.value === ""){

        showMessage("Please select a user type.","error");

        userTypeInput.focus();

        return false;

    }

    return true;

}
// ==========================
// Register Form Submit
// ==========================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    if (!validateForm()) {

        return;

    }

    registerBtn.disabled = true;

    registerBtn.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin"></i> Registering...';

    const data = {

        name: nameInput.value.trim(),

        email: emailInput.value.trim(),

        phone: phoneInput.value.trim(),

        password: passwordInput.value,

        user_type: userTypeInput.value

    };

    try {

        const response = await fetch(`${API_BASE}/auth/register`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const result = await response.json();

        if (response.ok) {

            showMessage(

                "Registration successful! Redirecting...",

                "success"

            );

            setTimeout(() => {

                window.location.href = "login.html";

            }, 1500);

        }

        else {

            showMessage(

                result.message || "Registration failed.",

                "error"

            );

        }

    }

    catch (error) {

        console.error(error);

        showMessage(

            "Unable to connect to the server.",

            "error"

        );

    }

    finally {

        registerBtn.disabled = false;

        registerBtn.innerHTML =
            '<i class="fa-solid fa-user-plus"></i> Register';

    }

});
// ======================================
// Additional Features
// ======================================

// Clear messages while typing
nameInput.addEventListener("input", clearMessage);
emailInput.addEventListener("input", clearMessage);
phoneInput.addEventListener("input", clearMessage);
passwordInput.addEventListener("input", clearMessage);
confirmPasswordInput.addEventListener("input", clearMessage);
userTypeInput.addEventListener("change", clearMessage);

// Auto focus on page load
window.addEventListener("load", () => {

    nameInput.focus();

});

// Password visibility (Optional)
// Add an eye icon in HTML if needed
function togglePassword(inputId){

    const input = document.getElementById(inputId);

    if(input.type === "password"){

        input.type = "text";

    }else{

        input.type = "password";

    }

}

// Prevent multiple form submissions
let isSubmitting = false;

form.addEventListener("submit", function(event){

    if(isSubmitting){

        event.preventDefault();

        return;

    }

    isSubmitting = true;

    setTimeout(() => {

        isSubmitting = false;

    },3000);

});

// Allow Enter key submission
document.addEventListener("keydown",(e)=>{

    if(e.key === "Enter"){

        form.requestSubmit();

    }

});

// Console message
console.log("🌱 AgriConnect Register Page Loaded Successfully");