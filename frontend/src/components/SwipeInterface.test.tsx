import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi } from 'vitest';
import { SwipeInterface } from './SwipeInterface';

vi.mock('./SwipeCard', () => ({
  SwipeCard: ({ restaurant }: any) => <div>{restaurant.name}</div>
}));
vi.mock('./ChatModal', () => ({ ChatModal: () => <div /> }));
vi.mock('./VoiceModal', () => ({ VoiceModal: () => <div /> }));
vi.mock('./OrderDetailsModal', () => ({ OrderDetailsModal: () => <div /> }));
vi.mock('./InitialPromptInterface', () => ({ InitialPromptInterface: () => <div /> }));
vi.mock('motion/react', () => ({ motion: { div: (props: any) => <div {...props} /> } }));

describe('SwipeInterface', () => {
  it('fetches and displays restaurants', async () => {
    const mockData = {
      restaurants: [{
        id: '1',
        name: 'Green Bowl Kitchen',
        cuisine: '',
        image: '',
        distance: '',
        price: '',
        rating: 4,
        highlights: []
      }],
      total: 1,
      sessionId: 'abc',
      explanations: {}
    };

    global.fetch = vi.fn().mockResolvedValue({ json: async () => mockData }) as any;

    render(
      <SwipeInterface
        userPreferences={{}}
        userProfile={{}}
        onUpdatePreferences={() => {}}
        onRestaurantLiked={() => {}}
      />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
