import { DataTransformService } from './services/DataTransformService';
import { RecommendationRequest, FrontendRestaurant } from './types';
import { restaurants, getMenuItemsForRestaurant } from './sampleData';
import { randomUUID } from 'crypto';

const transformer = new DataTransformService();

export function search(req: RecommendationRequest) {
  const { location } = req;
  const results: FrontendRestaurant[] = restaurants.map(r => {
    const items = getMenuItemsForRestaurant(r.id);
    return transformer.transformRestaurant(r, items, location);
  });

  return {
    restaurants: results.slice(0, req.limit || 10),
    total: results.length,
    sessionId: randomUUID(),
    explanations: {},
  };
}
