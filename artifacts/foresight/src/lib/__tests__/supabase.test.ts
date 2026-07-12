import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getSupabaseEnv, resetSupabaseClient } from '../supabase';

describe('supabase client', () => {
  beforeEach(() => {
    resetSupabaseClient();
    // Clear any stubbed environment variables
    vi.unstubAllEnvs();
  });

  it('module imports without throwing', () => {
    expect(() => {
      // This should not throw even if env vars are missing
      import('../supabase');
    }).not.toThrow();
  });

  it('getSupabaseEnv throws clear error when env missing', () => {
    // Ensure env vars are not stubbed
    vi.unstubAllEnvs();

    expect(() => {
      getSupabaseEnv();
    }).toThrow(
      'Missing VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY — copy .env.example to .env.local'
    );
  });

  it('getSupabaseEnv returns values when env vars are stubbed', () => {
    vi.stubEnv('VITE_SUPABASE_URL', 'http://localhost:54321');
    vi.stubEnv('VITE_SUPABASE_ANON_KEY', 'test-key');

    const env = getSupabaseEnv();

    expect(env.url).toBe('http://localhost:54321');
    expect(env.anonKey).toBe('test-key');
  });
});
