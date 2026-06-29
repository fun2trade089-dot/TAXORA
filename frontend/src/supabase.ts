import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://oidlpxwibztrxzgcoqmv.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pZGxweHdpYnp0cnh6Z2NvcW12Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3NTE3NDYsImV4cCI6MjA5ODMyNzc0Nn0.bG3zJEpSEk-qFQHm5lnX6vbJgydsnoiFwxoM4w3ZLAc';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
