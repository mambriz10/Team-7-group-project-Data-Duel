// js/register.js
const supabaseUrl = "https://gbvyveaifvqneyayloks.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1ODU1ODgsImV4cCI6MjA3NzE2MTU4OH0.Vn3LUVeRaLAQ7EGX97Z9PSPK-J7o9rR0-HPxbvXGH9I"; // Yes, this is the public key
const supabase = Supabase.createClient(supabaseUrl, supabaseKey);

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
            const { data, error } = await supabase.auth.signUp({ email, password });

            if (error) {
                alert("Registration failed: " + error.message);
                return;
            }

            // Registration succeeded, optionally reset form
            form.reset();
            alert("Registration successful! Please check your email to confirm if required.");
            
            // Redirect to login page
            window.location.href = "http://localhost:5500/index.html";
        } catch (err) {
            console.error("Unexpected error:", err);
            alert("An unexpected error occurred. Please try again.");
        }

        alert("Registration successful! Please check your email to confirm if required.");
        window.location.href = "http://localhost:5500/index.html"; // redirect to login
    });
});