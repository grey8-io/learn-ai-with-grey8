import { isSupabaseConfigured } from "./supabase";
import { createSupabaseServerClient } from "./supabase-server";

/**
 * Trusted identity headers forwarded to the tutor backend.
 *
 * The tutor enforces auth + quotas only in hosted mode; in local mode it
 * ignores these headers entirely. So we attach them whenever a Supabase session
 * exists and harmlessly omit them otherwise — there is no client-side "mode"
 * flag to manage.
 *
 * SECURITY: this runs server-side in the Next.js BFF, which is the auth
 * boundary. Hosted deployments MUST keep the tutor reachable only by this BFF
 * (internal ingress) so the X-Account-* headers can be trusted.
 */
export async function tutorIdentityHeaders(): Promise<Record<string, string>> {
  if (!isSupabaseConfigured()) return {};
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase.auth.getUser();
    if (error || !data?.user) return {};
    // Paid status is admin-controlled (app_metadata) and will be set by a
    // future billing system. Until then every account resolves to the
    // generous free tier.
    const tier = data.user.app_metadata?.tier === "paid" ? "paid" : "free";
    return { "X-Account-Id": data.user.id, "X-Account-Tier": tier };
  } catch {
    return {};
  }
}
