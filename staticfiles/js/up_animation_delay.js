document.addEventListener("DOMContentLoaded", () => {
	
	// @param {string} selector - The CSS selector for the elements to animate.
	// @param {number} delayStep - Th delay in milliseconds between each element's animation.
	function animateStaggeredElements(selector, delayStep = 50) {
		
		// Get all elements matching the provided selector
		const elements = document.querySelectorAll(selector);
		
		// Iterate over each element and apply animation with a delay
		elements.forEach((element, index) => {
			
			
			setTimeout(() => {
				// Add the "is_visible" class, which triggers the CSS transition defined in "style_user_profile.css"
				element.classList.add("is_visible");
			},
			// Calculate the delay based on index and delayStep
			index * delayStep);
		});
	}
	
	// Call the function to animate skill items when the DOM is fully loaded
	animateStaggeredElements(".skill-item", 50);
});