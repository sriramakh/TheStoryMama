import jwt from "jsonwebtoken";
import { auth } from "./auth";
import { API_URL } from "./constants";

interface BackendUser {
  id: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
  provider: string;
}

function getSecret(): string {
  const secret = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET;
  if (!secret) throw new Error("AUTH_SECRET / NEXTAUTH_SECRET is not set");
  return secret;
}

async function upsertBackendUser(
  email: string,
  name: string | null,
  image: string | null,
  providerId: string
): Promise<BackendUser> {
  const res = await fetch(`${API_URL}/api/v1/auth/oauth-user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      name: name || undefined,
      avatar_url: image || undefined,
      provider: "nextauth",
      provider_id: providerId,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Failed to sync user (${res.status})`);
  }
  return res.json();
}

/**
 * Resolve the current session → backend User row → signed HS256 JWT the
 * FastAPI `require_auth` middleware accepts.
 *
 * Returns null when no user is signed in.
 */
export async function getBackendAuth(): Promise<{
  token: string;
  user: BackendUser;
} | null> {
  const session = await auth();
  if (!session?.user?.email) return null;

  const user = await upsertBackendUser(
    session.user.email,
    session.user.name || null,
    session.user.image || null,
    session.user.id || session.user.email
  );

  const token = jwt.sign({ sub: user.id, email: user.email }, getSecret(), {
    algorithm: "HS256",
    expiresIn: "1h",
  });

  return { token, user };
}

/**
 * Forward a request to the FastAPI backend with a minted JWT.
 * Returns the raw Response so callers can stream, inspect status, etc.
 */
export async function backendFetch(
  path: string,
  init: RequestInit & { token?: string } = {}
): Promise<Response> {
  const token = init.token ?? (await getBackendAuth())?.token;
  if (!token) {
    return new Response(JSON.stringify({ detail: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);

  const { token: _t, ...rest } = init;
  return fetch(`${API_URL}${path}`, { ...rest, headers });
}
