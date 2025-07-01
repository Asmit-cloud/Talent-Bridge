// Ensure DOM is fully loaded before running the script
document.addEventListener("DOMContentLoaded", function () {
	// Select all elements that represent a skill item container
	const skillItems = document.querySelectorAll(".skill-item-container");
	
	// Starting delay for the first item (e.g., after initial page animations)
	const baseDelay = 0.9;
	// How much delay to add for each subsequent item (0.05 seconds)
	const delayIncrement = 0.05;
	
	// Iterate over each skill item found
	skillItems.forEach((item, index) => {
		// Calculate the unique animation delay for the current item
		// The formual adds the base delay to the product of the item's index and the increment
		// For example:
		// Item 0: 0.9 + (0 * 0.05) = 0.9s
		// Item 1: 0.9 + (1 * 0.05) = 0.95s
		// Item 2: 0.9 + (2 * 0.05) = 1.0s
		const delay = baseDelay + (index * delayIncrement);
		
		// Set the CSS custom property (variable) "--animation-delay-factor" on the current skill item element
		// This variable is then used in the CSS to control the animation-delay of the fadeInScale animation for that specific item
		item.style.setProperty("--animation-delay-factor", `${delay}s`);
	});
});