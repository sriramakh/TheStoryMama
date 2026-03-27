export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
}

export interface CreditBalance {
  available: number;
  total: number;
  used: number;
  plan_type?: string;
  expires_at?: string;
}

export interface Order {
  id: string;
  plan_type: string;
  amount_cents: number;
  currency: string;
  status: string;
  created_at: string;
}
