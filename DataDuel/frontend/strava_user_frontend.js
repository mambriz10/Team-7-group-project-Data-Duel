import { createClient } from "https://esm.sh/@supabase/supabase-js";

const db_URL = "https://gbvyveaifvqneyayloks.supabase.co"
const db_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1ODU1ODgsImV4cCI6MjA3NzE2MTU4OH0.Vn3LUVeRaLAQ7EGX97Z9PSPK-J7o9rR0-HPxbvXGH9I"
export const db = createClient(db_URL, db_KEY);