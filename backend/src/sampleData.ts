import { BackendRestaurant, BackendMenuItem } from './types';

export const restaurants: BackendRestaurant[] = [
  {
    id: '1',
    name: 'Green Bowl Kitchen',
    lat: 40.7209,
    lng: -74.0003,
    phone: '555-1234',
    yelp: { rating: 4.8, price: '$$' },
  },
  {
    id: '2',
    name: 'Muscle Fuel',
    lat: 40.7215,
    lng: -74.001,
    phone: '555-5678',
    yelp: { rating: 4.6, price: '$$$' },
  }
];

export const menuItems: BackendMenuItem[] = [
  {
    id: 'm1',
    restaurantId: '1',
    menuId: 'menu1',
    section: 'Bowls',
    name: 'Avocado Power Bowl',
    description: 'Fresh greens with avocado and quinoa',
    price: 12,
    currency: 'USD',
    tags: ['Vegetarian'],
    calories: 420,
    protein: 28,
    carbs: 35,
    fat: 18,
  },
  {
    id: 'm2',
    restaurantId: '2',
    menuId: 'menu2',
    section: 'Mains',
    name: 'Grilled Chicken Plate',
    description: 'Lean grilled chicken with vegetables',
    price: 15,
    currency: 'USD',
    tags: ['High protein'],
    calories: 580,
    protein: 45,
    carbs: 22,
    fat: 15,
  }
];

export function getMenuItemsForRestaurant(id: string): BackendMenuItem[] {
  return menuItems.filter(m => m.restaurantId === id);
}
