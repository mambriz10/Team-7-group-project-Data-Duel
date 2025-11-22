// js/register.js
import { db } from "./../supabaseClient/supabaseClient.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!name || !email || !password) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            // Register user with Supabase Auth
            const { data, error } = await db.auth.signUp({ email, password });
            //const accessToken = data.session.accessToken;
            

            if (error) {
                alert("Registration failed: " + error.message);
                return;
            }

            // Registration succeeded, optionally reset form
            form.reset();
            
            
            // Redirect to login page
            window.location.href = "http://localhost:5500/index.html";
        } catch (err) {
            console.error("Unexpected error:", err);
            alert("An unexpected error occurred. Please try again.");
        }

        alert("Registration successful!");
        window.location.href = "http://localhost:5500/index.html"; // redirect to login
    });
});
