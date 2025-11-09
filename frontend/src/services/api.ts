import type { IdeasResponse, OutlineRequest, OutlineResponse, DraftRequest, DraftResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function generateIdeas(topic: string, numIdeas: number = 3): Promise<IdeasResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ideas`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ topic, num_ideas: numIdeas }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate ideas');
  }

  return response.json();
}

export async function generateOutline(request: OutlineRequest): Promise<OutlineResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/outlines`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to generate outline');
  }

  return response.json();
}

export async function generateDraft(request: DraftRequest): Promise<DraftResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/drafts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to generate draft');
  }

  return response.json();
}
