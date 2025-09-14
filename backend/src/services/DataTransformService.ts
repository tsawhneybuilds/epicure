import { BackendRestaurant, BackendMenuItem, FrontendRestaurant } from '../types';

export class DataTransformService {
  transformRestaurant(
    restaurant: BackendRestaurant,
    items: BackendMenuItem[],
    userLocation: { lat: number; lng: number }
  ): FrontendRestaurant {
    return {
      id: restaurant.id,
      name: restaurant.name,
      cuisine: this.inferCuisine(restaurant.name, items),
      image: this.getRestaurantImage(restaurant),
      distance: this.calculateDistance(restaurant, userLocation),
      price: this.normalizePriceLevel(restaurant.yelp?.price, items),
      rating: restaurant.google_rating || restaurant.yelp?.rating || 4.0,
      waitTime: this.estimateWaitTime(),
      calories: this.getAverage(items, 'calories'),
      protein: this.getAverage(items, 'protein'),
      carbs: this.getAverage(items, 'carbs'),
      fat: this.getAverage(items, 'fat'),
      dietary: this.extractDietaryFlags(items),
      highlights: this.generateHighlights(items),
      address: restaurant.address,
      phone: restaurant.phone,
    };
  }

  private inferCuisine(_name: string, items: BackendMenuItem[]): string {
    const combined = items.map(i => i.name + ' ' + (i.description || '')).join(' ').toLowerCase();
    if (/(sushi|ramen|kimchi)/.test(combined)) return 'Asian';
    if (/(taco|burrito)/.test(combined)) return 'Mexican';
    if (/(pizza|pasta)/.test(combined)) return 'Italian';
    return 'American';
  }

  private getRestaurantImage(_restaurant: BackendRestaurant): string {
    // Placeholder image while real images are not available
    return 'https://images.unsplash.com/photo-1555992336-03a23c04d017?w=400';
  }

  private calculateDistance(
    restaurant: BackendRestaurant,
    userLocation: { lat: number; lng: number }
  ): string {
    const R = 6371e3; // metres
    const toRad = (v: number) => (v * Math.PI) / 180;
    const φ1 = toRad(userLocation.lat);
    const φ2 = toRad(restaurant.lat);
    const Δ2 = toRad(restaurant.lat - userLocation.lat);
    const Δλ = toRad(restaurant.lng - userLocation.lng);
    const a = Math.sin(Δ2 / 2) * Math.sin(Δ2 / 2) +
      Math.cos(φ1) * Math.cos(φ2) *
      Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // in metres
    const miles = d / 1609.34;
    return miles.toFixed(1) + ' mi';
  }

  private normalizePriceLevel(price?: string, items?: BackendMenuItem[]): string {
    if (price) return price;
    const avg = this.getAverage(items || [], 'price');
    if (!avg) return '$$';
    if (avg < 10) return '$';
    if (avg < 20) return '$$';
    return '$$$';
  }

  private estimateWaitTime(): string {
    return '15 min';
  }

  private getAverage(items: BackendMenuItem[], field: keyof BackendMenuItem): number | undefined {
    const values = items.map(i => (i[field] as number | undefined)).filter((v): v is number => typeof v === 'number');
    if (!values.length) return undefined;
    const sum = values.reduce((a, b) => a + b, 0);
    return Math.round((sum / values.length) * 10) / 10;
  }

  private extractDietaryFlags(items: BackendMenuItem[]): string[] {
    const flags = new Set<string>();
    items.forEach(i => (i.tags || []).forEach(t => flags.add(t)));
    return Array.from(flags);
  }

  private generateHighlights(items: BackendMenuItem[]): string[] {
    return items.slice(0, 3).map(i => i.name);
  }
}
