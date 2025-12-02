

const supabaseUrl = "https://gbvyveaifvqneyayloks.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1ODU1ODgsImV4cCI6MjA3NzE2MTU4OH0.Vn3LUVeRaLAQ7EGX97Z9PSPK-J7o9rR0-HPxbvXGH9I"; // Yes, this is the public key

export const db = supabase.createClient(supabaseUrl, supabaseKey);

//export db = supabase.createClient(supabaseUrl, supabaseKey);