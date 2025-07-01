from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatRoom, Participant, Message
import json

@login_required
def chat_room_view(request, chat_room_id):
    """
    Renders the chat room interface for a specific chat room ID.
    This view will pass the chat room details and messages to the template.
    """

    # Ensure chat room exists and the current user is a participant
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)

    # Verify the current user is a participant of this chat room
    if not Participant.objects.filter(user=request.user, chatroom=chat_room).exists():
        messages.error(request, "You are not authorised to view this chat room.")
        return redirect("public_user_profile")

    # Fetch messages for this chat room
    messages_in_chat = Message.objects.filter(chatroom=chat_room).order_by("timestamp")

    # Get the other participant's name for display
    other_participant = None
    participants = chat_room.participants.all()
    if participants.count() == 2:
        for participant_obj in participants:
            if participant_obj.user != request.user:
                other_participant = participant_obj.user
                break
    elif participants.count() == 1 and participants.first().user == request.user:
        other_participant = request.user
    elif participants.count() > 2:
        other_participant = "Group Chat"

    context = {
        "chat_room": chat_room,
        "messages": messages_in_chat,
        "current_user": request.user,
        "other_participant": other_participant, # For displaying who you are chatting with
        "chat_room_id_json": json.dumps(str(chat_room.id)),
    }

    return render(request, "chat/chat_room.html", context)
