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
            const { data: authData, error: authError } = await db.auth.signUp({ email, password });
            // if (authError) {
            //     alert(authError.message);
            //     return;
            // }

            const userId = authData.user.id;
            //const accessToken = data.session.accessToken;
            const response = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    username: name,
                    email
                }),
            });

            // If backend returned a JSON error, parse it
            const result = await response.json().catch(() => ({}));

            // if (!response.ok) {
            //     // Backend sent an error message
            //     alert(result.error || "Something went wrong.");
            //     return;
            // }
            // Registration succeeded, optionally reset form
            form.reset();
            
            
            // Redirect to login page
            window.location.href = "http://localhost:5500/index.html";
        } catch (err) {
            console.error("Unexpected error:", err);
            //alert("An unexpected error occurred. Please try again.");
        }

        alert("Registration successful!");
        window.location.href = "http://localhost:5500/index.html"; // redirect to login
    });
});
