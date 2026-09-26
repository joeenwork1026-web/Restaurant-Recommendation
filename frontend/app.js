const input = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

const restaurantGrid =
    document.getElementById("restaurant-grid");

const loading =
    document.getElementById("loading");

const emptyState =
    document.getElementById("empty-state");

const resultsTitle =
    document.getElementById("results-title");

const resultsCount =
    document.getElementById("results-count");


// =========================
// RESTAURANT CARD
// =========================

function addRestaurantCard(restaurant) {

    const card = document.createElement("article");

    card.className = "restaurant-card";


    /*
        We don't have real image URLs
        in restaurants.csv yet.

        So for now we use a visual placeholder.
    */

    card.innerHTML = `

        <div class="restaurant-image-placeholder">
            🍜
        </div>

        <button
            class="save-button"
            title="Save restaurant"
        >
            ♡
        </button>

        <div class="restaurant-body">

            <div class="restaurant-name-row">

                <h3 class="restaurant-name">
                    ${restaurant.name}
                </h3>

                <div class="rating">
                    <span>★</span>
                    ${restaurant.rating}
                </div>

            </div>


            <div class="restaurant-details">

                <span class="tag">
                    ${restaurant.cuisine}
                </span>

                <span class="tag">
                    ${restaurant.price_range}
                </span>

                <span class="tag">
                    ${restaurant.review_count} reviews
                </span>

            </div>


            <div class="restaurant-location">
                📍 ${restaurant.city}
            </div>


            <div class="ai-match">

                <div class="ai-match-title">
                    ✨ AI Match
                </div>

                <p>
                    ${restaurant.explanation}
                </p>

            </div>

        </div>
    `;


    // Save button

    const saveButton =
        card.querySelector(".save-button");

    saveButton.addEventListener(
        "click",
        function () {

            if (saveButton.textContent === "♡") {

                saveButton.textContent = "♥";

            } else {

                saveButton.textContent = "♡";

            }

        }
    );


    restaurantGrid.appendChild(card);
}


// =========================
// SEARCH
// =========================

async function searchRestaurants() {

    const text = input.value.trim();

    if (!text) {
        return;
    }


    // Disable search

    sendButton.disabled = true;


    // Clear old results

    restaurantGrid.innerHTML = "";

    emptyState.classList.add("hidden");

    loading.classList.remove("hidden");


    resultsTitle.textContent =
        "Finding restaurants...";

    resultsCount.textContent =
        "AI is searching";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/recommend",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    user_request: text,

                    top_k: 5

                })

            }
        );


        if (!response.ok) {

            throw new Error(
                `API request failed: ${response.status}`
            );

        }


        const data =
            await response.json();


        loading.classList.add("hidden");


        // No results

        if (
            !data.recommendations ||
            data.recommendations.length === 0
        ) {

            resultsTitle.textContent =
                "No matches found";

            resultsCount.textContent =
                "Try another search";

            emptyState.classList.remove(
                "hidden"
            );

            return;
        }


        // Results

        resultsTitle.textContent =
            "Recommended for you";

        resultsCount.textContent =
            `${data.recommendations.length} restaurants found`;


        data.recommendations.forEach(
            function (restaurant) {

                addRestaurantCard(
                    restaurant
                );

            }
        );


    } catch (error) {

        console.error(
            "Recommendation request failed:",
            error
        );


        loading.classList.add("hidden");


        resultsTitle.textContent =
            "Something went wrong";

        resultsCount.textContent =
            "Please try again";


        emptyState.classList.remove(
            "hidden"
        );


    } finally {

        sendButton.disabled = false;

        input.focus();

    }

}


// =========================
// SEARCH BUTTON
// =========================

sendButton.addEventListener(
    "click",
    searchRestaurants
);


// =========================
// ENTER KEY
// =========================

input.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            searchRestaurants();

        }

    }
);


// =========================
// SUGGESTION BUTTONS
// =========================

const suggestions =
    document.querySelectorAll(
        ".suggestion"
    );


suggestions.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                input.value =
                    button.dataset.query;

                searchRestaurants();

            }
        );

    }
);