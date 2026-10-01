import { useMemo, useState } from "react";

function getPhotoList(restaurant) {
    if (Array.isArray(restaurant.image_urls) && restaurant.image_urls.length > 0) {
        return restaurant.image_urls;
    }

    if (restaurant.image_url) {
        return [restaurant.image_url];
    }

    return [];
}

export default function RestaurantPhotoCarousel({ restaurant }) {
    const photos = useMemo(() => getPhotoList(restaurant), [restaurant]);
    const [activeIndex, setActiveIndex] = useState(0);

    const fallbackUrl =
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80";

    if (photos.length === 0) {
        return (
            <div className="restaurant-image">
                <span className="restaurant-image-fallback visible">🍽️</span>
            </div>
        );
    }

    const safeIndex = activeIndex % photos.length;
    const currentPhoto = photos[safeIndex];

    const goToPrevious = () => {
        setActiveIndex(
            (index) => (index - 1 + photos.length) % photos.length
        );
    };

    const goToNext = () => {
        setActiveIndex((index) => (index + 1) % photos.length);
    };

    return (
        <div className="restaurant-image restaurant-carousel">
            <img
                key={currentPhoto}
                src={currentPhoto}
                alt={`${restaurant.name} photo ${safeIndex + 1}`}
                loading="lazy"
                onError={(event) => {
                    const img = event.currentTarget;

                    if (!img.dataset.triedFallback) {
                        img.dataset.triedFallback = "true";
                        img.src = fallbackUrl;
                        return;
                    }

                    img.style.display = "none";
                }}
            />

            {photos.length > 1 ? (
                <>
                    <button
                        type="button"
                        className="carousel-arrow carousel-arrow-left"
                        aria-label="Previous photo"
                        onClick={goToPrevious}
                    >
                        ‹
                    </button>
                    <button
                        type="button"
                        className="carousel-arrow carousel-arrow-right"
                        aria-label="Next photo"
                        onClick={goToNext}
                    >
                        ›
                    </button>

                    <div className="carousel-dots">
                        {photos.map((photo, index) => (
                            <button
                                key={photo}
                                type="button"
                                className={
                                    index === safeIndex
                                        ? "carousel-dot active"
                                        : "carousel-dot"
                                }
                                aria-label={`Show photo ${index + 1}`}
                                onClick={() => setActiveIndex(index)}
                            />
                        ))}
                    </div>

                    <span className="carousel-count">
                        {safeIndex + 1}/{photos.length}
                    </span>
                </>
            ) : null}
        </div>
    );
}
