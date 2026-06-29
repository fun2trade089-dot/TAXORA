import { supabase } from '../supabase';

const API_BASE_URL = 'http://localhost:8000';

// Helper to get authorization headers
async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export interface TaxpayerProfile {
  name: string;
  pan: string;
  age: number;
  salary: {
    basic: number;
    da: number;
    hra_received: number;
    special_allowance: number;
    lta: number;
    perquisites: number;
    employer_nps: number;
    professional_tax: number;
    standard_deduction: number;
  };
  deductions: {
    section_80c: number;
    section_80d_self: number;
    section_80d_parents?: number;
    section_80ccd1b?: number;
    section_80ccd2_employer?: number;
    section_80e?: number;
    section_80g_100pct?: number;
    section_80g_50pct?: number;
    section_80gg?: number;
    section_80tta?: number;
    section_80ttb?: number;
  };
  hra_details: {
    basic_salary: number;
    da: number;
    hra_received: number;
    rent_paid: number;
    is_metro: boolean;
  };
}

export async function optimizeTax(profile: TaxpayerProfile) {
  try {
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders
      },
      body: JSON.stringify(profile)
    });
    
    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }
    
    return await response.json();
  } catch (err) {
    console.warn("FastAPI backend optimize unreachable, using mock calculation fallback:", err);
    throw err; // Let caller handle mock fallback
  }
}

export async function sendChatMessage(query: string, sessionId: string, profile?: any) {
  try {
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders
      },
      body: JSON.stringify({ query, session_id: sessionId, profile })
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  } catch (err) {
    console.warn("FastAPI backend chat unreachable, using mock chat fallback:", err);
    throw err;
  }
}

export async function getChatHistory(sessionId: string) {
  try {
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/chat/history/${sessionId}`, {
      headers: authHeaders
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const data = await response.json();
    return data.history;
  } catch (err) {
    console.warn("FastAPI backend history unreachable, returning empty history:", err);
    return [];
  }
}

export async function sendEmailReport(email: string, memoText: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/email-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, memo_text: memoText })
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.warn("FastAPI backend email service unreachable:", err);
    return { status: 'failed', message: 'Connection to email server failed' };
  }
}

export async function uploadDocument(file: File) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.warn("FastAPI backend document parser unreachable, returning mock parsed values:", err);
    throw err;
  }
}
