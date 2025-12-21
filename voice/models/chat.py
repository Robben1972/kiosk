from django.db import models



def audio_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"{instance.chat.clinic}/{instance.id}_audio.{ext}"


class Chat(models.Model):
    clinic = models.CharField(max_length=255)

    def __str__(self):
        return "Chat of " + self.clinic

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    is_user = models.BooleanField(default=True)
    
    audio = models.FileField(upload_to=audio_upload_path, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.text[:20]}..."
    
