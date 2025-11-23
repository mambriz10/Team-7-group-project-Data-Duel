// js/login.js
import { db } from "./../supabaseClient/supabaseClient.js";

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const remember = document.getElementById("remember").checked;

    if (!email || !password) {
        alert("Please enter email and password.");
        return;
    }

    // Real login — done by Supabase
    const { data: {user}, error } = await db.auth.signInWithPassword({
        email,
        password
    });

    if (error) {
        alert("Login failed: " + error.message);
        console.error(error);
        return;
    }

    
    // Optional: remember me
    // if (remember) {
    //     localStorage.setItem("supabase_session", JSON.stringify(data.session));
    // }


    window.location.href = "http://localhost:5500/index.html"; // redirect to login
});