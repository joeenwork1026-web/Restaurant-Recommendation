import { useMemo, useState } from "react";
import {
    GENERIC_RESTAURANT_IMAGE,
    getRestaurantImageUrl,
} from "./cuisineImages.js";

export default function RestaurantImage({ restaurant }) {
    const cuisineImage = useMemo(
        () => getRestaurantImageUrl(restaurant),
        [restaurant]
    );

    const [showEmojiFallback, setShowEmojiFallback] = useState(false);

    if (showEmojiFallback) {
        return (
            <div className="restaurant-image">
                <span className="restaurant-image-fallback visible">🍽️</span>
            </div>
        );
    }

    return (
        <div className="restaurant-image">
            <img
                src={cuisineImage}
                alt={`${restaurant.name} — ${restaurant.cuisine} food`}
                loading="lazy"
                onError={(event) => {
                    const img = event.currentTarget;

                    if (!img.dataset.triedGeneric) {
                        img.dataset.triedGeneric = "true";
                        img.src = GENERIC_RESTAURANT_IMAGE;
                        return;
                    }

                    setShowEmojiFallback(true);
                }}
            />
        </div>
    );
}
