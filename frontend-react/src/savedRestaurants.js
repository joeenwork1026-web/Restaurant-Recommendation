const STORAGE_KEY = "forkai_saved_restaurants";

export function loadSavedRestaurants() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            return [];
        }

        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

export function saveRestaurantsToStorage(restaurants) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(restaurants));
}

export function toggleSavedRestaurant(restaurant, savedList) {
    const exists = savedList.some(
        (item) => item.restaurant_id === restaurant.restaurant_id
    );

    if (exists) {
        return savedList.filter(
            (item) => item.restaurant_id !== restaurant.restaurant_id
        );
    }

    const snapshot = {
        restaurant_id: restaurant.restaurant_id,
        name: restaurant.name,
        cuisine: restaurant.cuisine,
        price_range: restaurant.price_range,
        rating: restaurant.rating,
        review_count: restaurant.review_count,
        city: restaurant.city,
        image_url: restaurant.image_url,
        image_urls: Array.isArray(restaurant.image_urls)
            ? restaurant.image_urls
            : restaurant.image_url
              ? [restaurant.image_url]
              : [],
        explanation: restaurant.explanation || "",
    };

    return [snapshot, ...savedList];
}

export function isRestaurantSaved(restaurantId, savedList) {
    return savedList.some((item) => item.restaurant_id === restaurantId);
}
