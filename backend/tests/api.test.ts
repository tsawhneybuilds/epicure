import request from 'supertest';
import app from '../src/index';

describe('API integration', () => {
  it('responds with recommendations', async () => {
    const res = await request(app)
      .post('/api/recommendations/search')
      .send({
        query: 'test',
        location: { lat: 40.72, lng: -74.0 },
        preferences: {},
        userProfile: {},
      });
    expect(res.status).toBe(200);
    expect(res.body.restaurants).toBeDefined();
    expect(res.body.sessionId).toBeDefined();
  });
});
