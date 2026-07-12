import { createClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

/**
 * Get Supabase environment variables from import.meta.env
 * Throws a clear error if either variable is missing
 */
export function getSupabaseEnv() {
  const url = import.meta.env.VITE_SUPABASE_URL;
  const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    throw new Error(
      'Missing VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY — copy .env.example to .env.local'
    );
  }

  return { url, anonKey };
}

let supabaseClient: ReturnType<typeof createClient<Database>> | null = null;

/**
 * Get or create the Supabase client singleton
 * Lazily initialized to allow tests to stub import.meta.env without errors at import time
 */
export function getSupabase() {
  if (supabaseClient) {
    return supabaseClient;
  }

  const { url, anonKey } = getSupabaseEnv();
  supabaseClient = createClient<Database>(url, anonKey);
  return supabaseClient;
}

/**
 * Reset the Supabase client (used in tests)
 */
export function resetSupabaseClient() {
  supabaseClient = null;
}
