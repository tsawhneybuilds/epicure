import { search } from '../src/recommendationEngine';

describe('recommendationEngine', () => {
  it('returns recommendations with session id', () => {
    const res = search({
      query: 'test',
      location: { lat: 40.72, lng: -74.0 },
      preferences: {},
      userProfile: {},
    });
    expect(res.restaurants.length).toBeGreaterThan(0);
    expect(res.sessionId).toBeDefined();
  });
});
