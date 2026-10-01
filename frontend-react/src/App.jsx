import { useEffect, useRef, useState } from "react";
import {
    isRestaurantSaved,
    loadSavedRestaurants,
    saveRestaurantsToStorage,
    toggleSavedRestaurant,
} from "./savedRestaurants.js";
import RestaurantPhotoCarousel from "./RestaurantPhotoCarousel.jsx";

const API_BASE = "http://127.0.0.1:8000";

const CUISINE_TAGS = [
    "Japanese",
    "Korean",
    "Chinese",
    "Western",
    "Thai",
    "Indian",
    "Italian",
    "Mexican",
    "Malaysian",
    "Vegetarian",
];

function RestaurantCard({
    restaurant,
    showExplanation,
    isSaved,
    onToggleSave,
}) {
    return (
        <article className="restaurant-card">
            <div className="restaurant-image-wrap">
                <RestaurantPhotoCarousel restaurant={restaurant} />
                <button
                    type="button"
                    className={
                        isSaved ? "save-heart saved" : "save-heart"
                    }
                    aria-label={
                        isSaved
                            ? "Remove from saved"
                            : "Save restaurant"
                    }
                    title={
                        isSaved
                            ? "Remove from saved"
                            : "Save restaurant"
                    }
                    onClick={() => onToggleSave(restaurant)}
                >
                    {isSaved ? "♥" : "♡"}
                </button>
            </div>

            <div className="restaurant-content">
                <div className="restaurant-top">
                    <h3>{restaurant.name}</h3>
                    <span className="rating">★ {restaurant.rating}</span>
                </div>

                <p className="restaurant-cuisine">{restaurant.cuisine}</p>

                <div className="restaurant-details">
                    <span>📍 {restaurant.city}</span>
                    <span>{restaurant.price_range}</span>
                    <span>{restaurant.review_count} reviews</span>
                </div>

                {showExplanation && restaurant.explanation ? (
                    <div className="ai-explanation">
                        <div className="ai-label">
                            ✦ Why ForkAI picked this
                        </div>
                        <p>{restaurant.explanation}</p>
                    </div>
                ) : null}
            </div>
        </article>
    );
}

function App() {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState("");
    const [recommendations, setRecommendations] = useState([]);
    const [matchType, setMatchType] = useState("");
    const [resultMode, setResultMode] = useState("search");
    const [selectedCuisine, setSelectedCuisine] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [activePage, setActivePage] = useState("home");
    const [savedRestaurants, setSavedRestaurants] = useState([]);
    const resultsRef = useRef(null);
    const discoverRef = useRef(null);
    const savedRef = useRef(null);

    useEffect(() => {
        setSavedRestaurants(loadSavedRestaurants());
    }, []);

    useEffect(() => {
        saveRestaurantsToStorage(savedRestaurants);
    }, [savedRestaurants]);

    useEffect(() => {
        if (
            activePage === "home" &&
            !loading &&
            recommendations.length > 0 &&
            resultsRef.current
        ) {
            resultsRef.current.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }
    }, [loading, recommendations, activePage]);

    useEffect(() => {
        if (activePage === "saved" && savedRef.current) {
            savedRef.current.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }
    }, [activePage, savedRestaurants.length]);

    const handleToggleSave = (restaurant) => {
        setSavedRestaurants((current) =>
            toggleSavedRestaurant(restaurant, current)
        );
    };

    const scrollToDiscover = (event) => {
        event.preventDefault();
        setActivePage("home");
        discoverRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    };

    const openSavedPage = (event) => {
        event.preventDefault();
        setActivePage("saved");
    };

    const handleCuisineDiscover = async (cuisine) => {
        setActivePage("home");
        setLoading(true);
        setError("");
        setRecommendations([]);
        setMatchType("discover");
        setResultMode("discover");
        setSelectedCuisine(cuisine);
        setSubmittedQuery(`${cuisine} restaurants`);
        setQuery(`${cuisine} food`);

        try {
            const response = await fetch(
                `${API_BASE}/restaurants?cuisine=${encodeURIComponent(cuisine)}&limit=20`
            );

            if (!response.ok) {
                throw new Error("Failed to load restaurants.");
            }

            const data = await response.json();
            setRecommendations(data.restaurants || []);
        } catch (err) {
            console.error(err);
            setError("Something went wrong while loading restaurants.");
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!query.trim()) {
            return;
        }

        setActivePage("home");
        setLoading(true);
        setError("");
        setRecommendations([]);
        setMatchType("");
        setResultMode("search");
        setSelectedCuisine("");
        setSubmittedQuery(query);

        try {
            const response = await fetch(`${API_BASE}/recommend`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_request: query,
                    top_k: 5,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to get recommendations.");
            }

            const data = await response.json();
            const items = Array.isArray(data.recommendations)
                ? data.recommendations
                : [];

            setRecommendations(items);
            setMatchType(data.match_type || "");
        } catch (err) {
            console.error(err);
            setError("Something went wrong while finding restaurants.");
        } finally {
            setLoading(false);
        }
    };

    const handleSuggestion = (suggestion) => {
        setQuery(suggestion);
    };

    const resultsEyebrow =
        resultMode === "discover" ? "✦ DISCOVER" : "✦ AI PICKS";

    const resultsTitle =
        resultMode === "discover" && selectedCuisine
            ? `${selectedCuisine} restaurants`
            : "Restaurants picked for you";

    const renderRestaurantGrid = (restaurants, showExplanation) => (
        <div className="restaurant-grid">
            {restaurants.map((restaurant) => (
                <RestaurantCard
                    key={restaurant.restaurant_id}
                    restaurant={restaurant}
                    showExplanation={showExplanation}
                    isSaved={isRestaurantSaved(
                        restaurant.restaurant_id,
                        savedRestaurants
                    )}
                    onToggleSave={handleToggleSave}
                />
            ))}
        </div>
    );

    return (
        <div className="app">
            <nav className="navbar">
                <div className="logo">
                    <span className="logo-icon">🍴</span>
                    <span>ForkAI</span>
                </div>

                <div className="nav-links">
                    <a
                        href="#discover"
                        className={
                            activePage === "home" ? "nav-active" : ""
                        }
                        onClick={scrollToDiscover}
                    >
                        Discover
                    </a>
                    <a href="#">For You</a>
                    <a
                        href="#saved"
                        className={
                            activePage === "saved" ? "nav-active" : ""
                        }
                        onClick={openSavedPage}
                    >
                        Saved
                        {savedRestaurants.length > 0 ? (
                            <span className="nav-badge">
                                {savedRestaurants.length}
                            </span>
                        ) : null}
                    </a>
                </div>

                <button className="profile-button">JD</button>
            </nav>

            {activePage === "home" ? (
                <>
                    <main
                        className={
                            recommendations.length > 0
                                ? "hero hero-compact"
                                : "hero"
                        }
                    >
                        <div className="hero-content">
                            <div className="ai-badge">
                                ✦ AI-powered restaurant discovery
                            </div>

                            <h1>
                                Find somewhere
                                <br />
                                <span>you'll love.</span>
                            </h1>

                            <p className="hero-description">
                                Tell ForkAI what you're craving. We'll find the
                                restaurants that match you.
                            </p>

                            <div className="search-box">
                                <div className="search-icon">✦</div>
                                <input
                                    type="text"
                                    value={query}
                                    onChange={(event) =>
                                        setQuery(event.target.value)
                                    }
                                    onKeyDown={(event) => {
                                        if (event.key === "Enter") {
                                            handleSearch();
                                        }
                                    }}
                                    placeholder="Try “cheap Japanese food in Kuala Lumpur...”"
                                />
                                <button
                                    className="search-button"
                                    onClick={handleSearch}
                                    disabled={loading}
                                >
                                    {loading
                                        ? "Finding..."
                                        : "Find restaurants"}
                                </button>
                            </div>

                            <div className="suggestions">
                                <span>Try asking:</span>
                                <button
                                    onClick={() =>
                                        handleSuggestion("Japanese food")
                                    }
                                >
                                    🍜 Japanese food
                                </button>
                                <button
                                    onClick={() =>
                                        handleSuggestion(
                                            "Chinese food under $$"
                                        )
                                    }
                                >
                                    🥟 Chinese food under $$
                                </button>
                                <button
                                    onClick={() =>
                                        handleSuggestion(
                                            "Highly rated restaurants"
                                        )
                                    }
                                >
                                    ⭐ Highly rated
                                </button>
                            </div>

                            <section
                                id="discover"
                                className="discover-section"
                                ref={discoverRef}
                            >
                                <p className="discover-eyebrow">
                                    Browse by cuisine
                                </p>
                                <h2 className="discover-title">Discover</h2>
                                <p className="discover-description">
                                    Tap a cuisine to see restaurants in our
                                    dataset.
                                </p>

                                <div className="cuisine-tags">
                                    {CUISINE_TAGS.map((cuisine) => (
                                        <button
                                            key={cuisine}
                                            type="button"
                                            className={
                                                selectedCuisine === cuisine
                                                    ? "cuisine-tag active"
                                                    : "cuisine-tag"
                                            }
                                            onClick={() =>
                                                handleCuisineDiscover(cuisine)
                                            }
                                            disabled={loading}
                                        >
                                            {cuisine}
                                        </button>
                                    ))}
                                </div>
                            </section>

                            {loading && (
                                <div className="search-result-message">
                                    <span>✦</span>
                                    ForkAI is finding restaurants for you...
                                </div>
                            )}

                            {error && (
                                <div className="error-message">{error}</div>
                            )}

                            {!loading &&
                                !error &&
                                submittedQuery &&
                                recommendations.length > 0 && (
                                    <div className="search-result-message">
                                        <span>✦</span>
                                        {resultMode === "discover" ? (
                                            <>
                                                Showing{" "}
                                                <strong>
                                                    {recommendations.length}
                                                </strong>{" "}
                                                <strong>
                                                    {selectedCuisine}
                                                </strong>{" "}
                                                restaurants.
                                            </>
                                        ) : matchType === "exact" ? (
                                            <>
                                                Found{" "}
                                                <strong>
                                                    {recommendations.length}
                                                </strong>{" "}
                                                restaurants for{" "}
                                                <strong>
                                                    {submittedQuery}
                                                </strong>
                                                .
                                            </>
                                        ) : (
                                            <>
                                                No exact matches for{" "}
                                                <strong>
                                                    {submittedQuery}
                                                </strong>
                                                . Showing{" "}
                                                <strong>
                                                    {recommendations.length}
                                                </strong>{" "}
                                                similar restaurants instead.
                                            </>
                                        )}
                                    </div>
                                )}

                            {!loading &&
                                !error &&
                                submittedQuery &&
                                recommendations.length === 0 && (
                                    <div className="search-result-message">
                                        <span>✦</span>
                                        No restaurants found. Try another
                                        cuisine or search.
                                    </div>
                                )}
                        </div>
                    </main>

                    {!loading && recommendations.length > 0 && (
                        <section
                            className="results-section"
                            ref={resultsRef}
                        >
                            <div className="results-header">
                                <div>
                                    <p className="results-eyebrow">
                                        {resultsEyebrow}
                                    </p>
                                    <h2>{resultsTitle}</h2>
                                </div>
                                <span className="results-count">
                                    {recommendations.length} matches
                                </span>
                            </div>

                            {renderRestaurantGrid(
                                recommendations,
                                resultMode === "search"
                            )}
                        </section>
                    )}
                </>
            ) : (
                <section
                    id="saved"
                    className="saved-page"
                    ref={savedRef}
                >
                    <div className="saved-header">
                        <div>
                            <p className="results-eyebrow">✦ SAVED</p>
                            <h2>Your saved restaurants</h2>
                            <p className="saved-description">
                                Tap the heart on any card to add or remove a
                                restaurant here.
                            </p>
                        </div>
                        <span className="results-count">
                            {savedRestaurants.length} saved
                        </span>
                    </div>

                    {savedRestaurants.length === 0 ? (
                        <div className="saved-empty">
                            <p>No saved restaurants yet.</p>
                            <button
                                type="button"
                                className="saved-empty-button"
                                onClick={(event) => scrollToDiscover(event)}
                            >
                                Discover restaurants
                            </button>
                        </div>
                    ) : (
                        renderRestaurantGrid(savedRestaurants, false)
                    )}
                </section>
            )}
        </div>
    );
}

export default App;
