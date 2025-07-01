document.addEventListener("DOMContentLoaded", function () {
	const skillItems = document.querySelectorAll(".user-skill-item");
	
	const baseDelay = 0.1;
	const delayIncrement = 0.05;
	
	// Iterate over each skill item found
	skillItems.forEach((item, index) => {
		// Calculate delay for each item
		const delay = baseDelay + (index * delayIncrement);
		// Apply the animation delay using inline style
		item.style.animationDelay = `${delay}s`;
		
		// Ensure the animation properties are set
		item.style.animationName = "fadeInScale";
		item.style.animationDuratoin = "0.6s";
		item.style.animationTimingFunction = "ease-out";
		item.animationFillMode = "forwards"
	});
});