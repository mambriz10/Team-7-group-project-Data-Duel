// js/login.js
const supabaseUrl = "https://gbvyveaifvqneyayloks.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1ODU1ODgsImV4cCI6MjA3NzE2MTU4OH0.Vn3LUVeRaLAQ7EGX97Z9PSPK-J7o9rR0-HPxbvXGH9I"; // Yes, this is the public key
const supabase = supabase.createClient(supabaseUrl, supabaseKey);

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
    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
    });

    if (error) {
        alert("Login failed: " + error.message);
        console.error(error);
        return;
    }

    // Optional: remember me
    if (remember) {
        localStorage.setItem("supabase_session", JSON.stringify(data.session));
    }

    alert("Login successful!");
    window.location.href = "index.html";
});