// Get chat room ID from the Django template context
const chatRoomId = JSON.parse(chat_room_id_json);
const currentUserName = JSON.parse(currentUserName_json);

const chatSocket = new WebSocket(
	'ws://' + window.location.host + '/ws/chat/' + chatRoomId + '/'
);

const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("chat-message-input");
const messageSubmit = document.getElementById("chat-message-submit");

// Map to store references to optimistic messages by their temporary ID
const optimisticMessages = new Map()

// A variable to manage stagger delay for incoming messages
let messageStaggerDelay = 0;
const staggerIncrement = 0.05; // 50ms delay between messages

// Scroll to the bottom on initial load
// A slight delay here ensures that the chat-container animation has started before scrolling or if the content loads dynamically later
setTimeout(() => {
	chatMessages.scrollTop = chatMessages.scrollHeight;
}, 100);

// Function to add or update a message in the UI
function addOrUpdateMessageInUI(message, senderUsername, timestamp, isCurrentUser, messageId=null, tempMessageId=null) {
	const options = {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
		hour12: false
	};
	const localFormattedTime = new Intl.DateTimeFormat(navigator.language, options).format(timestamp);
	
	let messageItem;
	
	if (tempMessageId && optimisticMessages.has(tempMessageId)) {
		// This is a server confirmation for an optimistic messsage
		messageItem = optimisticMessages.get(tempMessageId);
		// Update its content with the server's actual timestamp and messageId
		messageItem.dataset.messageId = messageId; // Store the real ID
		messageItem.classList.remove("message-sending"); // Remove sending state style
		
	// Ensure that the sending status span is removed before updating the innerHTML
	const sendingStatusSpan = messageItem.querySelector(".sending-status");
	if (sendingStatusSpan) {
		sendingStatusSpan.remove(); // Remove the "Sending..." text
	}
		messageItem.querySelector(".message-meta").innerHTML = `
			${isCurrentUser ? "You" :senderUsername} at ${localFormattedTime}
		`;
		// Remove from optimistic map as now it's confirmed
		optimisticMessages.delete(tempMessageId);
		
	// Reset stagger delay after an optimistic message is confirmed so subsequent "new" messages don't get an inherited delay
	messageStaggerDelay = 0;
		
	} else {
		// This is a new message (either optimistic or from another user)
		messageItem = document.createElement("div");
		messageItem.classList.add("message-item");
		messageItem.classList.add(isCurrentUser ? "message-sent" :"message-received");
		
		if (tempMessageId) {
			// Mark as optimistic (sending)
			messageItem.dataset.tempId = tempMessageId; // Store a temporary ID
			messageItem.classList.add("message-sending"); // Add a class for styling "sending" messages
			optimisticMessages.set(tempMessageId, messageItem); // Store reference
	messageStaggerDelay = 0;
		} else {
			// This is a confirmed message from another user, or a pre-loaded message
			messageItem.dataset.messageId = messageId; // Store the real ID
	messageItem.style.animationDelay = `${messageStaggerDelay}s`;
	messageItem.style.animationFillMode = "both"; // Ensure animation end-state persists
	messageStaggerDelay += staggerIncrement; // Increment for the text message
		}
		
		messageItem.innerHTML = `	
			<div>
			
				<div class="message-bubble">
					${message}
				</div>
				
				<div class="message-meta">
					${isCurrentUser ? "You" : senderUsername} at ${localFormattedTime}
					${tempMessageId ? '<span class="sending-status"> (Sending...)</span>' : ''}
				</div>
			
			</div>
		`;
		chatMessages.appendChild(messageItem);
	}
		
	// Scroll to the bottom after adding new a message
	setTimeout(() => {
		chatMessages.scrollTop = chatMessages.scrollHeight;
	}, 50);
}

chatSocket.onmessage = function(e) {
	const data = JSON.parse(e.data);
	console.log("Received data:", data);
	
	if (data.type === "chat_message") {
		const message = data.message;
		const senderUsername = data.sender_username;
		const timestamp = new Date(data.timestamp);
		const messageId = data.message_id; //Server generated ID
		const tempMessageId = data.temp_message_id || null; // Temporary client-side ID
		const isCurrentUser = (senderUsername === currentUserName);
		
		addOrUpdateMessageInUI(message, senderUsername, timestamp, isCurrentUser, messageId, tempMessageId);
		
	}
	else if (data.type === "error" || data.type === "auth_error") {
		console.error("Chat error:", data.message);
		console.warn("Chat error: " + data.message);
		if (data.type === "auth_error") {
			window.location.href = "{% url 'login' %}";
		}
	}
	else if (data.type === "chat_joined") {
		console.log(data.message);
	}
};
	
chatSocket.onclose = function(e) {
	console.error("Chat socket closed unexpectedly.", e)
};
	
messageInput.focus();
messageInput.onkeyup = function(e) {
	if (e.key === "Enter") {
		messageSubmit.click();
	}
};

messageSubmit.onclick = function(e) {
	const message = messageInput.value.trim();
	if (message) {
		// Generate a temporary client-side ID for this message
		const tempId = crypto.randomUUID();
		// Optimistically add the message to the UI before sending
		// Use current time and current user for optimistic display
		const now = new Date()
		addOrUpdateMessageInUI(message, currentUserName, now, true, null, tempId);
		
	// This ensures new incoming messages (from other users) after you send will start their staggered animation from 0 rather than a continuation
	messageStaggerDelay = 0;
	
		chatSocket.send(JSON.stringify({
			"message": message,
			"temp_message_id": tempId // Include the temporary ID in the sent payload
		}));
		messageInput.value = ""; // Clear input field
	}
};