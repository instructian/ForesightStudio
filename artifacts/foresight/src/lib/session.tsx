import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { User } from '@supabase/supabase-js';
import { getSupabase } from './supabase';
import type { Tables } from './database.types';

export type Profile = Tables<'profiles'>;

export type Status = 'loading' | 'signedOut' | 'unapproved' | 'student' | 'admin';

/**
 * Pure status derivation — no side effects, safe to unit test directly.
 *
 * - no user                              -> 'signedOut'
 * - user present, profile not loaded yet -> 'loading'
 * - profile.is_approved === false        -> 'unapproved'
 * - approved + role 'Administrator'      -> 'admin'
 * - approved + role 'Student'|'Subscriber' -> 'student' (subscriber surfaces come later)
 */
export function deriveStatus(user: User | null, profile: Profile | null): Status {
  if (!user) {
    return 'signedOut';
  }

  if (!profile) {
    return 'loading';
  }

  if (!profile.is_approved) {
    return 'unapproved';
  }

  if (profile.role === 'Administrator') {
    return 'admin';
  }

  // 'Student' and 'Subscriber' are both student-read surfaces for now.
  return 'student';
}

type SessionContextValue = {
  user: User | null;
  profile: Profile | null;
  status: Status;
  refreshProfile: () => Promise<void>;
};

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

async function fetchProfile(userId: string): Promise<Profile | null> {
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .maybeSingle();

  if (error) {
    console.error('Failed to fetch profile', error);
    return null;
  }

  return data;
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [initializing, setInitializing] = useState(true);

  const loadProfile = useCallback(async (currentUser: User | null) => {
    if (!currentUser) {
      setProfile(null);
      return;
    }
    const nextProfile = await fetchProfile(currentUser.id);
    setProfile(nextProfile);
  }, []);

  useEffect(() => {
    const supabase = getSupabase();
    let cancelled = false;

    supabase.auth.getSession().then(async ({ data }) => {
      if (cancelled) return;
      const currentUser = data.session?.user ?? null;
      setUser(currentUser);
      await loadProfile(currentUser);
      if (!cancelled) setInitializing(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        const currentUser = session?.user ?? null;
        setUser(currentUser);
        await loadProfile(currentUser);
        setInitializing(false);
      },
    );

    return () => {
      cancelled = true;
      subscription.subscription.unsubscribe();
    };
  }, [loadProfile]);

  const refreshProfile = useCallback(async () => {
    await loadProfile(user);
  }, [loadProfile, user]);

  const status: Status = initializing ? 'loading' : deriveStatus(user, profile);

  const value = useMemo<SessionContextValue>(
    () => ({ user, profile, status, refreshProfile }),
    [user, profile, status, refreshProfile],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
