import { DataTransformService } from '../src/services/DataTransformService';
import { restaurants, getMenuItemsForRestaurant } from '../src/sampleData';

describe('DataTransformService', () => {
  it('transforms backend restaurant to frontend format', () => {
    const svc = new DataTransformService();
    const restaurant = restaurants[0];
    const items = getMenuItemsForRestaurant(restaurant.id);
    const result = svc.transformRestaurant(restaurant, items, { lat: 40.72, lng: -74.0 });
    expect(result).toMatchObject({
      id: restaurant.id,
      name: restaurant.name,
      distance: expect.stringContaining('mi'),
      highlights: expect.any(Array),
    });
  });
});
