import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import F, Q
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

from .models import ChatRoom, Message, Participant

CustomUser = get_user_model()

class ChatConsumer( AsyncWebsocketConsumer):
    """
    Consumer to handle WebSocket connections for the chat functionality.
    This consumer manages joining or leaving chat rooms, sending messages, and receiving real-time updates.
    """

    async def connect(self):
        """
        This function is called when the WebSocket connection is established.
        It authernticates the user and adds them to the appropriate chat room group.
        """

        # Get the chat room ID from the URL route
        self.chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        # Create a group name specific for this chat room for broadcasting messages
        self.chat_room_group_name = f"chat_{self.chat_room_id}"

        self.channel_layer.group_add(self.chat_room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

        # Check if the user is authenticated
        if not self.scope["user"].is_authenticated:
            # Close the connection
            await self.send(text_data=json.dumps({
                "type": "auth_error",
                "message": "Authentication is required to access chat."
            }))
            await self.close(code=4001) # Unauthenticated access
            return

        # Ensure the user is a participant of this chat room
        user = self.scope["user"]
        chat_room_exists = await sync_to_async(ChatRoom.objects.filter(id=self.chat_room_id).exists)()

        if not chat_room_exists:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Chat room does not exist."
            }))
            await self.close(code=4004) # Not found
            return

        is_participant = await sync_to_async(Participant.objects.filter(user=user, chatroom__id=self.chat_room_id).exists)()

        if not is_participant:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "You are not a participant of this chat room."
            }))
            await self.close(code=4003) # Forbidden
            return

        # Add the user to the chat room group in the channel layer
        await self.channel_layer.group_add(self.chat_room_group_name, self.channel_name)

        # Send a 'joined' message to the client
        await self.send(text_data=json.dumps({
                "type": "chat_joined",
                "message": "You have joined chat room {self.chat_room_id}."
            }))

    async def disconnect(self, close_code):
        """
        This function is called when the WebSocket connection is closed.
        It removes the user from the chat room group.
        """

        # Remove the user from the chat room group in the channel layer
        await self.channel_layer.group_discard(self.chat_room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        This function is called when a message is received from the WebSocket.
        It parses the message, saves it to the database, and broadcasts it to the chat room group.
        """

        # Parse the incoming JSON message
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message")
        # Capture the temporary ID
        temp_message_id = text_data_json.get("temp_message_id")

        # Validate the message
        if not message_content or not isinstance(message_content, str) or message_content.strip() == "":
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Message content cannot be empty."
            }))
            return

        # Get the sender and chat room objects
        sender = self.scope["user"]

        # Ensure chat room exists
        try:
            chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.chat_room_id)
        except ObjectDoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Chat room not found."
            }))
            await self.close(code=4004)
            return

        # Save the message to the database asynchronously
        new_message = await sync_to_async(Message.objects.create)(chatroom=chat_room, sender=sender, content=message_content)

        # Prepare the message for broadcasting
        message_data = {
            "type": "chat_message",
            "message": message_content,
            "sender_username": sender.username,
            "timestamp": new_message.timestamp.isoformat(),
            "message_id": str(new_message.id), # Server generated ID
            "chatroom_id": str(chat_room.id),
        }
        # Include the temporary ID if provided
        if temp_message_id:
            message_data["temp_message_id"] = temp_message_id

        # Send the message to the chat room group
        await self.channel_layer.group_send(self.chat_room_group_name, message_data)

    async def chat_message(self, event):
        """
        This function handles messages received from the channel layer (i.e., broadcasts from other clients or server generated messages for this group).
        Sends the message back to the WebSocket.
        """
        
        # Extract the message data from the event dictionary
        message = event["message"]
        sender_username = event["sender_username"]
        timestamp = event["timestamp"]
        message_id = event["message_id"]
        chatroom_id = event["chatroom_id"]
        # temp_message_id = event.get("temp_message_id", None) # Get temporary ID if exists

        # Send the message to WebSocket (to the client)
        response_data = {
            "type": "chat_message",
            "message": message,
            "sender_username": sender_username,
            "timestamp": timestamp,
            "message_id": message_id,
            "chatroom_id": chatroom_id,
        }

        # Check if the message is for the sender
        if self.scope["user"].username == sender_username and "temp_message_id" in event:
            response_data["temp_message_id"] = event["temp_message_id"]

        await self.send(text_data=json.dumps(response_data))
