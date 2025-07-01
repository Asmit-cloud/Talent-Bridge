document.addEventListener("DOMContentLoaded", function () {
	const skillItems = document.querySelectorAll(".skill-item");
	
	const baseDelay = 1.2;
	const delayIncrement = 0.03;
	
	// Iterate over each skill item found
	skillItems.forEach((item, index) => {
		// Calculate delay for each item
		const delay = baseDelay + (index * delayIncrement);
		
		// Ensure the animation properties are set
		item.style.animation = "fadeInUp 0.6s ease-out forwards";
		item.style.animationDelay = `${delay}s`;
		item.style.opacity = "0";
	});
});