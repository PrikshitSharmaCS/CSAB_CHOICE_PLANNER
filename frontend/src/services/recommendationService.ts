import { RecommendationResult, StudentProfile } from '../types';

const API_URL = '/api/recommend';

export async function fetchRecommendations(profile: StudentProfile): Promise<RecommendationResult> {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(profile)
  });

  if (!response.ok) {
    throw new Error('Failed to connect to recommendation backend.');
  }

  return response.json();
}
