CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    requested_role user_role := 'Student'::user_role;
BEGIN
    IF new.raw_user_meta_data ? 'role'
       AND new.raw_user_meta_data->>'role' IN ('Administrator', 'Student', 'Subscriber') THEN
        requested_role := (new.raw_user_meta_data->>'role')::user_role;
    END IF;

    INSERT INTO public.profiles (id, full_name, role, is_approved)
    VALUES (
        new.id,
        COALESCE(NULLIF(new.raw_user_meta_data->>'full_name', ''), split_part(new.email, '@', 1), 'New user'),
        requested_role,
        false
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
