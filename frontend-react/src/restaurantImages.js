/**
 * Deterministic cuisine → image mapping for restaurant cards.
 * The API is unchanged; the UI picks the photo from cuisine + restaurant_id.
 */

export const GENERIC_RESTAURANT_IMAGE =
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80";

/** Verified Unsplash food photos grouped by cuisine. */
export const CUISINE_IMAGES = {
    Japanese: [
        "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80",
        "https://images.unsplash.com/photo-1574484284002-952d92456975?w=800&q=80",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
    ],
    Korean: [
        "https://images.unsplash.com/photo-1590301157890-4810ed352733?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80",
    ],
    Chinese: [
        "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=800&q=80",
        "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
    ],
    Italian: [
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    ],
    Mexican: [
        "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&q=80",
        "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=800&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    ],
    Thai: [
        "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80",
        "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    ],
    Indian: [
        "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
        "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
    ],
    American: [
        "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80",
        "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800&q=80",
        "https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=800&q=80",
    ],
    Malaysian: [
        "https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?w=800&q=80",
        "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
    ],
    French: [
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
    ],
    Vegetarian: [
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
        "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&q=80",
    ],
};

/** Dataset uses "Western"; treat it as American for images. */
const CUISINE_ALIASES = {
    Western: "American",
};

export function normalizeCuisine(cuisine) {
    const trimmed = (cuisine || "").trim();
    return CUISINE_ALIASES[trimmed] || trimmed;
}

function restaurantIndex(restaurantId) {
    const match = String(restaurantId || "").match(/^R(\d+)$/i);
    if (match) {
        return parseInt(match[1], 10);
    }

    let total = 0;
    for (const char of String(restaurantId)) {
        total += char.charCodeAt(0);
    }
    return total;
}

/**
 * Pick one stable image URL for this restaurant.
 * Same restaurant_id + cuisine always returns the same URL.
 */
export function getRestaurantImageUrl(restaurant) {
    const cuisine = normalizeCuisine(restaurant?.cuisine);
    const pool = CUISINE_IMAGES[cuisine];

    if (!pool || pool.length === 0) {
        return GENERIC_RESTAURANT_IMAGE;
    }

    const index = (restaurantIndex(restaurant?.restaurant_id) - 1) % pool.length;
    return pool[index];
}
