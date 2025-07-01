from django.conf import settings
from django.db import models
from SkillSwap_Network.models import CustomUser

class ChatRoom(models.Model):
    """
    Represents a chat room or a private conversation between users.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"
        ordering = ["-updated_at"]

    def __str__(self):
        """
        Returns a string representation of the ChatRoom.
        """

        # Dynamically generates a descriptive name for the chat room based on its participants
        participants = self.participants.all()
        if participants.count() == 2:
            return f"Chat between {participants[0].user.username} and {participants[1].user.username}"
        elif participants.count() == 1:
            return f"Chat with {participants[0].user.username}"
        else:
            return f"Chat Room {self.id}"


class Participant(models.Model):
    """
    Represent a user's participation in a specific chat room.
    This model allows for easy querying of which users are in which chat rooms.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_participants",
        help_text="The user participating in the chat room."
    )
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="The chat room, the user is participating in."
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chatroom") # A user can only be a participant once per chat room
        verbose_name = "Chat Participant"
        verbose_name_plural = "Chat Participants"

    def __str__(self):
        """
        Returns a string representation of the Participant.
        """
        return f"{self.user.username} in Chat Room {self.chatroom.id}"


class Message(models.Model):
    """
    Represents an individual message sent within a chat room.
    """

    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The chat room where the message was sent."
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="The user who sent the message."
    )
    content = models.TextField(
        help_text="The actual content of the message."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time the message was sent."
    )
    is_read= models.BooleanField(
        default=False,
        help_text="Indicates if the message has been read by the recipent."
    )

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["timestamp"]

    def __str__(self):
        """
        Represents a string representation of the Message.
        """

        return f"Message from {self.sender.username} in Chat {self.chatroom.id} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
