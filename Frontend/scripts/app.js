// Wait for the DOM to fully load before running scripts
document.addEventListener("DOMContentLoaded", () => {
  const hamMenu = document.querySelector(".ham-menu");
  const offScreenMenu = document.querySelector(".off-screen-menu");

  // Toggle hamburger menu
  if (hamMenu && offScreenMenu) {
    hamMenu.addEventListener("click", () => {
      hamMenu.classList.toggle("active");
      offScreenMenu.classList.toggle("active");
    });
  }

  // Restore state from URL params
  const urlParams = new URLSearchParams(window.location.search);
  const searchQuery = urlParams.get("search") || "";
  const page = parseInt(urlParams.get("page")) || 1;
  const set = urlParams.get("set") || "";
  const rarity = urlParams.get("rarity") || "";

  document.getElementById("pokemonName").value = searchQuery;
  document.getElementById("setInput").value = set;
  document.getElementById("rarityInput").value = rarity;

  if (searchQuery) fetchData(page); // Trigger auto-search on page load
});

// Fetch Pokémon card data based on filters and render them
async function fetchData(page = 1) {
  try {
    const nameInput = document.getElementById("pokemonName").value.toLowerCase();
    const setInput = document.getElementById("setInput").value;
    const rarityInput = document.getElementById("rarityInput").value;

    // Build query string
    const queryParts = [];
    if (nameInput) queryParts.push(`name:"${nameInput}"`);
    if (setInput) queryParts.push(`set.name:"${setInput}"`);
    if (rarityInput) queryParts.push(`rarity:"${rarityInput}"`);
    const fullQuery = queryParts.join(" ");

    // Update URL parameters
    const newUrl = new URL(window.location.href);
    newUrl.searchParams.set("search", nameInput);
    newUrl.searchParams.set("page", page);
    setInput ? newUrl.searchParams.set("set", setInput) : newUrl.searchParams.delete("set");
    rarityInput ? newUrl.searchParams.set("rarity", rarityInput) : newUrl.searchParams.delete("rarity");
    window.history.pushState({}, "", newUrl.toString());

    // API request
    const response = await fetch(`https://api.pokemontcg.io/v2/cards?q=${encodeURIComponent(fullQuery)}&page=${page}&pageSize=25`);
    if (!response.ok) throw new Error("Failed to fetch Pokémon cards.");
    const data = await response.json();

    const imgContainer = document.getElementById("imgContainer");
    imgContainer.innerHTML = ""; // Clear previous results

    const matchingCards = data.data;
    if (matchingCards.length === 0) {
      console.log("No matching cards found.");
      document.getElementById("paginationControls").style.display = "none";
      return;
    }

    // Display cards
    matchingCards.forEach((card) => {
      const imageUrl = card.images.large;
      const cardId = card.id;
      const encodedParams = {
        name: card.name,
        set: card.set.name,
        rarity: card.rarity || "Unknown",
        image: imageUrl,
        low: formatPrice(card),
        mid: formatPrice(card, "mid"),
        high: formatPrice(card, "high"),
        market: formatPrice(card, "market"),
        search: nameInput,
        page
      };

      const queryString = Object.entries(encodedParams)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join("&");

      const linkElement = document.createElement("a");
      linkElement.href = `pokemoninfo.html?id=${cardId}&${queryString}`;
      linkElement.style.textDecoration = "none";

      const imgElement = document.createElement("img");
      imgElement.src = imageUrl;
      imgElement.alt = card.name;
      imgElement.loading = "lazy";
      imgElement.style.display = "block";
      imgElement.style.cursor = "pointer";
      imgElement.style.maxWidth = "200px";

      linkElement.appendChild(imgElement);
      imgContainer.appendChild(linkElement);
    });

    // Show pagination controls
    document.getElementById("paginationControls").style.display = "flex";
    window.scrollTo({ top: 0, behavior: "smooth" });

  } catch (error) {
    console.error("Error loading data:", error);
  }
}

// Get the formatted price from card object
function formatPrice(card, tier = "low") {
  const prices = card.tcgplayer?.prices?.normal || card.tcgplayer?.prices?.holofoil || {};
  return prices[tier] ? `$${prices[tier]}` : "Not Available";
}

// Pagination navigation
function nextPage() {
  fetchData(getCurrentPage() + 1);
}

function prevPage() {
  const current = getCurrentPage();
  if (current > 1) fetchData(current - 1);
}

// Helper: Get current page from URL
function getCurrentPage() {
  const params = new URLSearchParams(window.location.search);
  return parseInt(params.get("page")) || 1;
}