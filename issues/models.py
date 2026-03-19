from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class FileTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class File(models.Model):

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Archived', 'Archived'),
    ]

    file_no = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=300)
    efile_no = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)

    description = models.TextField(blank=True)
    remark = models.TextField(blank=True)

    physical_location = models.CharField(max_length=200, blank=True)
    section = models.CharField(max_length=200, blank=True)
    MOVEMENT_STATUS = [
        ('received', 'Received'),
        ('sent', 'Sent'),
    ]

    movement_status = models.CharField(
        max_length=10,
        choices=MOVEMENT_STATUS,
        default='received'
    )

    last_movement_date = models.DateTimeField(null=True, blank=True)
    last_movement_remark = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    open_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)

    tags = models.ManyToManyField(FileTag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_no} - {self.name}"


class Issue(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    opened_on = models.DateField(auto_now_add=True)
    closed_on = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    files = models.ManyToManyField(File, blank=True)
    status = models.CharField(max_length=50, default="Open")
    priority = models.CharField(max_length=20, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issue_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    EVENT_TYPES = [
        ('note', 'General Note'),
        ('received', 'Letter Received'),
        ('sent', 'Letter Issued'),
        ('discussion', 'Discussion'),
        ('meeting', 'Meeting'),
        ('update', 'Update'),
    ]

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='events')

    event_date = models.DateField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    short_note = models.CharField(max_length=300)
    detailed_note = models.TextField(blank=True)

    file = models.ForeignKey(
        File,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    # Communication fields (optional)
    letter_no = models.CharField(max_length=200, blank=True)
    letter_date = models.DateField(null=True, blank=True)
    sender = models.CharField(max_length=300, blank=True)
    sender_address = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue} - {self.short_note}"


class Reference(models.Model):
    REF_TYPES = [
        ('N', 'Notesheet'),
        ('C', 'Correspondence'),
        ('V', 'Volume'),
        ('P', 'Page'),
        ('F', 'Flag'),
        ('O', 'Other'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='references')
    ref_type = models.CharField(max_length=1, choices=REF_TYPES)
    ref_value = models.CharField(max_length=50)
    remarks = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.ref_type}/{self.ref_value}"


