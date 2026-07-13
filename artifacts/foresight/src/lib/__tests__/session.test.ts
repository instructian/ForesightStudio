import { describe, it, expect } from 'vitest';
import type { User } from '@supabase/supabase-js';
import { deriveStatus } from '../session';
import type { Tables } from '../database.types';

type Profile = Tables<'profiles'>;

function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: 'user-1',
    app_metadata: {},
    user_metadata: {},
    aud: 'authenticated',
    created_at: new Date().toISOString(),
    ...overrides,
  } as User;
}

function makeProfile(overrides: Partial<Profile> = {}): Profile {
  return {
    id: 'user-1',
    full_name: 'Test User',
    role: 'Student',
    term_id: null,
    is_approved: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

describe('deriveStatus', () => {
  it('returns signedOut when there is no user', () => {
    expect(deriveStatus(null, null)).toBe('signedOut');
  });

  it('returns loading when a user exists but the profile has not loaded yet', () => {
    expect(deriveStatus(makeUser(), null)).toBe('loading');
  });

  it('returns unapproved for an unapproved student', () => {
    const profile = makeProfile({ role: 'Student', is_approved: false });
    expect(deriveStatus(makeUser(), profile)).toBe('unapproved');
  });

  it('returns admin for an approved Administrator', () => {
    const profile = makeProfile({ role: 'Administrator', is_approved: true });
    expect(deriveStatus(makeUser(), profile)).toBe('admin');
  });

  it('returns student for an approved Student', () => {
    const profile = makeProfile({ role: 'Student', is_approved: true });
    expect(deriveStatus(makeUser(), profile)).toBe('student');
  });

  it('returns student for an approved Subscriber (student-read for now)', () => {
    const profile = makeProfile({ role: 'Subscriber', is_approved: true });
    expect(deriveStatus(makeUser(), profile)).toBe('student');
  });
});
