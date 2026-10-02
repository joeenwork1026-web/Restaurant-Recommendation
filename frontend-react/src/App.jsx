import { useEffect, useRef, useState } from "react";
import LoginModal from "./LoginModal.jsx";
import RestaurantImage from "./RestaurantImage.jsx";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const SEARCH_STAGES = [
    "Understanding your request",
    "Finding matching restaurants",
    "Ranking the best matches",
    "Preparing your recommendations",
];

const STAGE_DELAYS_MS = [0, 1200, 2800, 4500];
const COMPLETE_DISPLAY_MS = 500;

function RestaurantCard({ restaurant, showExplanation, onSaveClick }) {
    return (
        <article className="restaurant-card">
            <div className="restaurant-image-wrap">
                <RestaurantImage restaurant={restaurant} />
                <button
                    type="button"
                    className="save-heart"
                    aria-label="Save restaurant (sign in required)"
                    title="Sign in to save restaurants"
                    onClick={() => onSaveClick(restaurant)}
                >
                    ♡
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

function SearchProgress({ completedCount, activeStage }) {
    return (
        <div className="search-progress" aria-live="polite">
            <ul className="search-progress-list">
                {SEARCH_STAGES.map((label, index) => {
                    const isDone = index < completedCount;
                    const isActive =
                        !isDone &&
                        index === activeStage &&
                        completedCount < SEARCH_STAGES.length;

                    let icon = "○";
                    let rowClass = "search-progress-item pending";

                    if (isDone) {
                        icon = "✓";
                        rowClass = "search-progress-item done";
                    } else if (isActive) {
                        icon = "✦";
                        rowClass = "search-progress-item active";
                    }

                    return (
                        <li key={label} className={rowClass}>
                            <span className="search-progress-icon">{icon}</span>
                            <span>
                                {label}
                                {isActive ? "..." : ""}
                            </span>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}

function App() {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState("");
    const [recommendations, setRecommendations] = useState([]);
    const [matchType, setMatchType] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [loginOpen, setLoginOpen] = useState(false);
    const [showSearchProgress, setShowSearchProgress] = useState(false);
    const [completedCount, setCompletedCount] = useState(0);
    const [activeStage, setActiveStage] = useState(0);

    const resultsRef = useRef(null);
    const heroRef = useRef(null);
    const progressTimersRef = useRef([]);
    const finishTimerRef = useRef(null);

    const clearProgressTimers = () => {
        progressTimersRef.current.forEach((timerId) => {
            clearTimeout(timerId);
        });
        progressTimersRef.current = [];

        if (finishTimerRef.current) {
            clearTimeout(finishTimerRef.current);
            finishTimerRef.current = null;
        }
    };

    const startProgressAnimation = () => {
        clearProgressTimers();
        setCompletedCount(0);
        setActiveStage(0);

        STAGE_DELAYS_MS.slice(1).forEach((delayMs, index) => {
            const timerId = setTimeout(() => {
                setCompletedCount(index + 1);
                setActiveStage(index + 1);
            }, delayMs);
            progressTimersRef.current.push(timerId);
        });
    };

    const finishProgressThen = (onDone) => {
        clearProgressTimers();
        setCompletedCount(SEARCH_STAGES.length);
        setActiveStage(-1);

        finishTimerRef.current = setTimeout(() => {
            setShowSearchProgress(false);
            onDone();
        }, COMPLETE_DISPLAY_MS);
    };

    useEffect(() => {
        return () => {
            clearProgressTimers();
        };
    }, []);

    useEffect(() => {
        if (!loading && recommendations.length > 0 && resultsRef.current) {
            resultsRef.current.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }
    }, [loading, recommendations]);

    const openLogin = () => {
        setLoginOpen(true);
    };

    const closeLogin = () => {
        setLoginOpen(false);
    };

    const scrollToHero = (event) => {
        event.preventDefault();
        heroRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    };

    const handleSavedClick = (event) => {
        event.preventDefault();
        openLogin();
    };

    const handleSaveClick = () => {
        openLogin();
    };

    const handleSearch = async () => {
        if (!query.trim() || loading) {
            return;
        }

        clearProgressTimers();
        setLoading(true);
        setError("");
        setRecommendations([]);
        setMatchType("");
        setSubmittedQuery(query);
        setShowSearchProgress(true);
        startProgressAnimation();

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
            const nextMatchType = data.match_type || "";

            finishProgressThen(() => {
                setRecommendations(items);
                setMatchType(nextMatchType);
                setLoading(false);
            });
        } catch (err) {
            console.error(err);
            clearProgressTimers();
            setShowSearchProgress(false);
            setLoading(false);
            setCompletedCount(0);
            setActiveStage(0);
            setError("Something went wrong while finding restaurants.");
        }
    };

    const handleSuggestion = (suggestion) => {
        setQuery(suggestion);
    };

    const renderRestaurantGrid = (restaurants) => (
        <div className="restaurant-grid">
            {restaurants.map((restaurant) => (
                <RestaurantCard
                    key={restaurant.restaurant_id}
                    restaurant={restaurant}
                    showExplanation
                    onSaveClick={handleSaveClick}
                />
            ))}
        </div>
    );

    return (
        <div className="app">
            <nav className="navbar">
                <div className="navbar-start">
                    <div className="logo">
                        <span className="logo-icon">🍴</span>
                        <span>ForkAI</span>
                    </div>

                    <div className="nav-links">
                        <a
                            href="#top"
                            className="nav-active"
                            onClick={scrollToHero}
                        >
                            Discover
                        </a>
                        <button
                            type="button"
                            className="nav-saved-button"
                            onClick={handleSavedClick}
                        >
                            Saved
                            <span className="nav-login-hint">Sign in required</span>
                        </button>
                    </div>
                </div>

                <button
                    type="button"
                    className="sign-in-button"
                    onClick={openLogin}
                >
                    Sign in
                </button>
            </nav>

            <LoginModal isOpen={loginOpen} onClose={closeLogin} />

            <main
                ref={heroRef}
                id="top"
                className={
                    recommendations.length > 0 ? "hero hero-compact" : "hero"
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
                            onChange={(event) => setQuery(event.target.value)}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" && !loading) {
                                    handleSearch();
                                }
                            }}
                            placeholder="Try “cheap Japanese food in Kuala Lumpur...”"
                            disabled={loading}
                        />
                        <button
                            className="search-button"
                            onClick={handleSearch}
                            disabled={loading}
                        >
                            {loading ? "Searching..." : "Find restaurants"}
                        </button>
                    </div>

                    <div className="suggestions">
                        <span>Try asking:</span>
                        <button
                            onClick={() => handleSuggestion("Japanese food")}
                            disabled={loading}
                        >
                            🍜 Japanese food
                        </button>
                        <button
                            onClick={() =>
                                handleSuggestion("Chinese food under $$")
                            }
                            disabled={loading}
                        >
                            🥟 Chinese food under $$
                        </button>
                        <button
                            onClick={() =>
                                handleSuggestion("Highly rated restaurants")
                            }
                            disabled={loading}
                        >
                            ⭐ Highly rated
                        </button>
                    </div>

                    {showSearchProgress && (
                        <SearchProgress
                            completedCount={completedCount}
                            activeStage={activeStage}
                        />
                    )}

                    {error && <div className="error-message">{error}</div>}

                    {!loading &&
                        !error &&
                        submittedQuery &&
                        recommendations.length > 0 && (
                            <div className="search-result-message">
                                <span>✦</span>
                                {matchType === "exact" ? (
                                    <>
                                        Found{" "}
                                        <strong>{recommendations.length}</strong>{" "}
                                        restaurants for{" "}
                                        <strong>{submittedQuery}</strong>.
                                    </>
                                ) : (
                                    <>
                                        No exact matches for{" "}
                                        <strong>{submittedQuery}</strong>. Showing{" "}
                                        <strong>{recommendations.length}</strong>{" "}
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
                                No restaurants found. Try another search.
                            </div>
                        )}
                </div>
            </main>

            {!loading && recommendations.length > 0 && (
                <section className="results-section" ref={resultsRef}>
                    <div className="results-header">
                        <div>
                            <p className="results-eyebrow">✦ AI PICKS</p>
                            <h2>Restaurants picked for you</h2>
                        </div>
                        <span className="results-count">
                            {recommendations.length} matches
                        </span>
                    </div>

                    {renderRestaurantGrid(recommendations)}
                </section>
            )}
        </div>
    );
}

export default App;
