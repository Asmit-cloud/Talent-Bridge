document.addEventListener("DOMContentLoaded", function() {
	let cachedSkillsData = [];
	let cachedProficiencyLevelsData = [];
	
	// Function to fetch skills from the Django API endpoint
	async function fetchSkills() {
		if (cachedSkillsData.length > 0) {
			return cachedSkillsData;
		}
		try {
			const response = await fetch("/SkillSwap_Network/api/skills/");
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			const data = await response.json();
			cachedSkillsData = data;
			return data;
		}
		catch (error) {
			console.error("Error fetching skills:", error);
			return [];
		}
	}
	
	// Function to generate options for the skill select dropdown
	function generateSkillOptions(skills, selectedSkillValue = "") {
		let optionsHtml = "<option value=''>--- Select a Skill ---</option>";
		skills.forEach(skill => {
			const isSelected = (skill.value === selectedSkillValue) ? "selected" : "";
			optionsHtml += `<option value="${skill.value}" ${isSelected}>${skill.label}</option>`;
		}
		);
		return optionsHtml;
	}
	
	// Function to fetch proficiency levels from the Django API endpoint
	async function fetchProficiencyLevels() {
		if (cachedProficiencyLevelsData.length > 0) {
			return cachedProficiencyLevelsData;
		}
		try {
			const response = await fetch("/SkillSwap_Network/api/proficiency_levels/");
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			const data = await response.json();
			cachedProficiencyLevelsData = data;
			return data;
		}
		catch (error) {
			console.error("Error fetching proficiency levels:", error);
			return [];
		}
	}
	
	// Function to generate options for the proficiency level select dropdown
	function generateProficiencyOptions(levels, selectedProficiencyValue = "", prefix) {
		let emptyLabel = "--- Select a Proficiency Level ---";
		if (prefix && prefix.includes("needed")) {
			emptyLabel = "--- Desired Proficiency Level (Optional) ---";
		}
		let optionsHtml = `<option value=''>${emptyLabel}</option>`;
		levels.forEach(level => {
			const isSelected = (level.value === selectedProficiencyValue) ? "selected" : "";
			optionsHtml += `<option value="${level.value}" ${isSelected}>${level.label}</option>`;
		}
		);
		return optionsHtml;
	}
	
	// Function to add a new form to a formset dynamically
	async function addForm(containerId, prefix) {
		const container = document.getElementById(containerId);
		const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);
		
		// Check if totalFormsInput is found before proceeding
		if (!totalFormsInput) {
			console.error(`Error: Could not find TOTAL_FORMS input for prefix: ${prefix}.`);
			return;
		}
		
		// Get the currect number of rendered forms
		const currentDisplayedForms = container.children.length;
		
		// The new index for the dynamically added form (0-based)
		const newFormIndex = currentDisplayedForms;
		
		// Calculate the display number (1-based)
		const displaySkillNumber = newFormIndex + 1;
		
		// Add placeholder for the description box
		const descriptionPlaceholder = prefix.includes("offered") ?
			"Optional: Add notes about the skill (e.g., specific technologies, projects)":
			"Optional: Why do you need this skill? (e.g.,for a specific project)";
		
		const skills = await fetchSkills();
		const proficiencyLevels = await fetchProficiencyLevels();
		
		const newCardLikeDiv = document.createElement("div");
		newCardLikeDiv.className = "card-like";
		
		// Construt the full HTML content, including the heading and all fields
		const innerFormContent = `
			<p>Skill ${displaySkillNumber}</p>
			<input type="hidden" name="${prefix}-${newFormIndex}-id" id="${prefix}-${newFormIndex}-id">
			<div class="form-group">
				<label for="${prefix}-${newFormIndex}-skill">Skill:</label>
				<select name="${prefix}-${newFormIndex}-skill" id="${prefix}-${newFormIndex}-skill">
					${generateSkillOptions(skills)}
				</select>
			</div>
			<div class="form-group">
				<label for="${prefix}-${newFormIndex}-proficiency_level">Proficiency Level:</label>
				<select name="${prefix}-${newFormIndex}-proficiency_level" id="${prefix}-${newFormIndex}-proficiency_level">
					${generateProficiencyOptions(proficiencyLevels, "", prefix)}
				</select>
			</div>
			<div class="form-group">
				<label for="${prefix}-${newFormIndex}-description">Description:</label>
				<textarea name="${prefix}-${newFormIndex}-description" id="${prefix}-${newFormIndex}-description" rows="3" placeholder="${descriptionPlaceholder}"></textarea>
			</div>
			<div class="form-group checkbox-container">
				<input type="checkbox" name="${prefix}-${newFormIndex}-DELETE" id="${prefix}-${newFormIndex}-DELETE">
				<label for="${prefix}-${newFormIndex}-DELETE">DELETE</label>
			</div>
			<input type="hidden" name="${prefix}-${newFormIndex}-user" id="${prefix}-${newFormIndex}-user" value="${document.getElementById('user_id').value}">
		`;
		
		// Set the innerHTML of the newly created .card-like div
		newCardLikeDiv.innerHTML = innerFormContent;
		// Append the entire .card-like div (containing all the fields) to the main container
		container.appendChild(newCardLikeDiv);
		
		// Update TOTAL_FORMS in the management form
		totalFormsInput.value = newFormIndex + 1;
		
	}
	
	const addOfferedSkillButton = document.getElementById("add-offered-skill");
	if (addOfferedSkillButton) {
		addOfferedSkillButton.addEventListener("click", function() {
			addForm("offered-skills-container", "offered_skills");
		}
		);
	}
	
	const addNeededSkillButton = document.getElementById("add-needed-skill");
	if (addNeededSkillButton) {
		addNeededSkillButton.addEventListener("click", function() {
			addForm("needed-skills-container", "needed_skills");
		}
		);
	}
}
);