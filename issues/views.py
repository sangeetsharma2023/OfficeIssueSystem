from django.shortcuts import render, get_object_or_404, redirect
from .models import Issue, Event, Reference
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
        event = Event.objects.create(
            issue=issue,
            event_date=request.POST.get('event_date'),
            event_type=request.POST.get('event_type'),
            short_note=request.POST.get('short_note'),
            detailed_note=request.POST.get('detailed_note'),
            file_name=request.POST.get('file_name'),
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

    return render(request, 'issues/add_event.html', {'issue': issue})


@login_required
def add_issue(request):
    if request.method == 'POST':
        Issue.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority'),
            created_by=request.user
        )
        return redirect('issue_list')

    return render(request, 'issues/add_issue.html')


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
