from django.shortcuts import render, get_object_or_404, redirect
from .models import Issue, Event, Reference, File, FileTag, Tag
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from itertools import chain

@login_required
def issue_list(request):
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.get('tag')


    if query:
        # --- Search in Issue table ---
        issue_matches = Issue.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

        # --- Search in Event table ---
        event_matches = Issue.objects.filter(
            events__in=Event.objects.filter(
                Q(short_note__icontains=query) |
                Q(detailed_note__icontains=query) |
                Q(letter_no__icontains=query) |
                Q(sender__icontains=query) |
                Q(file_name__icontains=query)
            )
        )

        # Combine both querysets
        issues = Issue.objects.filter(
            id__in=set(chain(issue_matches.values_list('id', flat=True),
                             event_matches.values_list('id', flat=True)))
        )
        if tag_filter:
            issues = issues.filter(tags__name=tag_filter)


    else:
        issues = Issue.objects.all()

    issues = issues.order_by('-opened_on')

    return render(request, 'issues/issue_list.html', {
        'issues': issues,
        'query': query
    })




@login_required
def issue_detail_full(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    events = issue.events.all().order_by('-event_date', '-created_at')
    return render(request, 'issues/issue_detail.html', {'issue': issue, 'events': events})



@login_required
def add_event(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if request.method == 'POST':
        file_id = request.POST.get('file')

        event = Event.objects.create(
            issue=issue,
            file=File.objects.get(id=file_id) if file_id else None,
            event_date=request.POST.get('event_date'),
            event_type=request.POST.get('event_type'),
            short_note=request.POST.get('short_note'),
            detailed_note=request.POST.get('detailed_note'),
            letter_no=request.POST.get('letter_no'),
            sender=request.POST.get('sender'),
            sender_address=request.POST.get('sender_address'),
            created_by=request.user
        )

        # references multiple lines separated by comma
        refs = request.POST.get('references')
        if refs:
            for r in refs.split(','):
                r = r.strip()
                if '/' in r:
                    t, v = r.split('/')
                    Reference.objects.create(event=event, ref_type=t.strip().upper(), ref_value=v.strip())

        return redirect('issue_detail', pk=issue.pk)

    return render(request, 'issues/add_event.html', {
        'issue': issue,
        'files': issue.files.all()   # 🔥 important
    })


@login_required
def add_issue(request):
    files = File.objects.all()

    if request.method == 'POST':
        issue = Issue.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority'),
            created_by=request.user
        )

        # 🔥 assign selected files
        selected_files = request.POST.getlist('files')
        if selected_files:
            issue.files.set(selected_files)

        return redirect('issue_list')

    return render(request, 'issues/add_issue.html', {
        'files': files
    })


@login_required
def edit_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    files = File.objects.all()

    if request.method == 'POST':
        issue.title = request.POST.get('title')
        issue.description = request.POST.get('description')
        issue.priority = request.POST.get('priority')
        issue.status = request.POST.get('status')
        issue.save()

        # update files
        selected_files = request.POST.getlist('files')
        issue.files.set(selected_files)

        return redirect('issue_detail', pk=issue.pk)

    return render(request, 'issues/edit_issue.html', {
        'issue': issue,
        'files': files
    })


@login_required
def delete_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if request.method == 'POST':
        issue.delete()
        return redirect('issue_list')

    return render(request, 'issues/delete_issue.html', {'issue': issue})

def user_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")
        else:
            error = "Invalid username or password"

    return render(request, "issues/login.html", {"error": error})

@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def print_issue(request, pk):
    issue = ensure_issue = get_object_or_404(Issue, pk=pk)
    events = issue.events.all().order_by('event_date', 'created_at')

    return render(request, 'issues/print_issue.html', {
        'issue': issue,
        'events': events
    })


@login_required
def issue_compact(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    events = issue.events.all().order_by('-event_date', '-created_at')

    return render(request, 'issues/issue_compact.html', {
        'issue': issue,
        'events': events
    })


@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()

    issue_results = []
    event_results = []

    if query:
        # Issue matches
        issue_results = Issue.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

        # Event matches
        event_results = Event.objects.filter(
            Q(short_note__icontains=query) |
            Q(detailed_note__icontains=query) |
            Q(letter_no__icontains=query) |
            Q(sender__icontains=query) |
            Q(file_name__icontains=query)
        ).select_related('issue')

    return render(request, 'issues/search.html', {
        'query': query,
        'issue_results': issue_results,
        'event_results': event_results
    })


@login_required
def file_list(request):
    status = request.GET.get('movement')

    
    files = File.objects.all().order_by('-created_at')
    if status:
        files = files.filter(movement_status=status)
    return render(request, 'issues/file_list.html', {'files': files})


@login_required
def add_file(request):
    tags = FileTag.objects.all()

    if request.method == 'POST':
        file = File.objects.create(
            file_no=request.POST.get('file_no'),
            name=request.POST.get('name'),
            efile_no=request.POST.get('efile_no'),
            year=request.POST.get('year') or None,
            description=request.POST.get('description'),
            remark=request.POST.get('remark'),
            physical_location=request.POST.get('physical_location'),
            section=request.POST.get('section'),
            status=request.POST.get('status'),
            open_date=request.POST.get('open_date') or None,
            close_date=request.POST.get('close_date') or None,
        )

        selected_tags = request.POST.getlist('tags')
        if selected_tags:
            file.tags.set(selected_tags)

        return redirect('file_list')

    return render(request, 'issues/add_file.html', {'tags': tags})


@login_required
def edit_file(request, pk):
    file = get_object_or_404(File, pk=pk)
    tags = FileTag.objects.all()

    if request.method == 'POST':
        file.file_no = request.POST.get('file_no')
        file.name = request.POST.get('name')
        file.efile_no = request.POST.get('efile_no')
        file.year = request.POST.get('year') or None
        file.description = request.POST.get('description')
        file.remark = request.POST.get('remark')
        file.physical_location = request.POST.get('physical_location')
        file.section = request.POST.get('section')
        file.status = request.POST.get('status')
        file.open_date = request.POST.get('open_date') or None
        file.close_date = request.POST.get('close_date') or None
        file.save()

        selected_tags = request.POST.getlist('tags')
        file.tags.set(selected_tags)

        return redirect('file_list')

    return render(request, 'issues/edit_file.html', {
        'file': file,
        'tags': tags
    })


@login_required
def delete_file(request, pk):
    file = get_object_or_404(File, pk=pk)

    if request.method == 'POST':
        file.delete()
        return redirect('file_list')

    return render(request, 'issues/delete_file.html', {'file': file})


@login_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    issue = event.issue

    # only files linked to issue
    files = issue.files.all()

    if request.method == 'POST':
        event.event_date = request.POST.get('event_date')
        event.event_type = request.POST.get('event_type')
        event.short_note = request.POST.get('short_note')
        event.detailed_note = request.POST.get('detailed_note')
        event.letter_no = request.POST.get('letter_no')
        event.sender = request.POST.get('sender')
        event.sender_address = request.POST.get('sender_address')

        file_id = request.POST.get('file')
        event.file = File.objects.get(id=file_id) if file_id else None

        event.save()

        # update references
        event.references.all().delete()
        refs = request.POST.get('references')
        if refs:
            for r in refs.split(','):
                r = r.strip()
                if '/' in r:
                    t, v = r.split('/')
                    Reference.objects.create(
                        event=event,
                        ref_type=t.strip().upper(),
                        ref_value=v.strip()
                    )

        return redirect('issue_detail', pk=issue.pk)

    return render(request, 'issues/edit_event.html', {
        'event': event,
        'issue': issue,
        'files': files
    })


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    issue_pk = event.issue.pk

    if request.method == 'POST':
        event.delete()
        return redirect('issue_detail', pk=issue_pk)

    return render(request, 'issues/delete_event.html', {'event': event})


from django.utils import timezone

@login_required
def send_file(request, pk):
    file = get_object_or_404(File, pk=pk)

    if request.method == 'POST':
        remark = request.POST.get('remark')

        file.movement_status = 'sent'
        file.last_movement_date = timezone.now()
        file.last_movement_remark = remark
        file.save()

        return redirect('file_list')

    return render(request, 'issues/send_file.html', {'file': file})


@login_required
def receive_file(request, pk):
    file = get_object_or_404(File, pk=pk)

    if request.method == 'POST':
        remark = request.POST.get('remark')

        file.movement_status = 'received'
        file.last_movement_date = timezone.now()
        file.last_movement_remark = remark
        file.save()

        return redirect('file_list')

    return render(request, 'issues/receive_file.html', {'file': file})

@login_required
def files_under_submission(request):
    files = File.objects.filter(movement_status='sent').order_by('-last_movement_date')

    return render(request, 'issues/files_submission.html', {
        'files': files
    })