import { useQuery } from '@tanstack/react-query';
import { getSupabase } from './supabase';
import { useSession, type Profile } from './session';
import type { Tables } from './database.types';

export type Term = Tables<'terms'>;

/**
 * The current user's profile row, sourced from SessionProvider (already
 * fetched on auth state changes). Exposed as a query hook so pages can
 * consume it consistently with the rest of the react-query data layer.
 */
export function useProfile() {
  const { profile, status } = useSession();

  return useQuery<Profile | null>({
    queryKey: ['profile', profile?.id ?? null],
    queryFn: async () => profile,
    initialData: profile,
    enabled: status !== 'loading',
  });
}

/**
 * The terms row for the current user's profile.term_id. Disabled when the
 * profile has no term assigned yet (e.g. newly-approved users pending
 * assignment).
 */
export function useMyTerm() {
  const { data: profile } = useProfile();
  const termId = profile?.term_id ?? null;

  return useQuery<Term | null>({
    queryKey: ['term', termId],
    queryFn: async () => {
      if (!termId) return null;
      const supabase = getSupabase();
      const { data, error } = await supabase
        .from('terms')
        .select('*')
        .eq('id', termId)
        .maybeSingle();

      if (error) {
        throw error;
      }

      return data;
    },
    enabled: termId !== null,
  });
}
