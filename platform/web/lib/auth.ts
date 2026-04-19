import { createBrowserClient } from "./supabase";

const notConfiguredError = {
  name: "AuthNotConfigured",
  message: "Sign-in is not enabled in this deployment.",
};

function getClient() {
  return createBrowserClient();
}

export async function signUp(
  email: string,
  password: string,
  displayName: string
) {
  const supabase = getClient();
  if (!supabase) return { data: null, error: notConfiguredError };
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: { display_name: displayName },
    },
  });
  return { data, error };
}

export async function signIn(email: string, password: string) {
  const supabase = getClient();
  if (!supabase) return { data: null, error: notConfiguredError };
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
}

export async function signOut() {
  const supabase = getClient();
  if (!supabase) return { error: null };
  const { error } = await supabase.auth.signOut();
  return { error };
}

export async function getCurrentSession() {
  const supabase = getClient();
  if (!supabase) return { session: null, error: null };
  const { data, error } = await supabase.auth.getSession();
  return { session: data.session, error };
}
