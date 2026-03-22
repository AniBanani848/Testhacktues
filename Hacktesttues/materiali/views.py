from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, ResourceForm, SupplyForm, UserRegistrationForm
from .models import Resource, Supply


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile = user.profile
            profile.current_major = form.cleaned_data['current_major'].strip()
            profile.learning_focus = (form.cleaned_data.get('learning_focus') or '').strip()
            profile.save()
            login(request, user)
            messages.success(request, 'Welcome to StudyLink — your learning profile is set.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your learning profile was updated.')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {'form': form})


def _learning_match_q(user):
    major = (user.profile.current_major or '').strip()
    focus = (user.profile.learning_focus or '').strip()
    q = Q()
    if major:
        q |= Q(subject__iexact=major)
        q |= Q(uploader__profile__current_major__iexact=major)
    if focus:
        q |= Q(subject__icontains=focus)
        q |= Q(title__icontains=focus)
    return q, major, focus


@login_required
def dashboard(request):
    q, user_major, user_focus = _learning_match_q(request.user)
    if q:
        recommended = (
            Resource.objects.filter(q)
            .select_related('uploader', 'uploader__profile')
            .distinct()
            .order_by('-uploaded_at')[:15]
        )
    else:
        recommended = Resource.objects.none()
    return render(
        request,
        'dashboard.html',
        {
            'recommended': recommended,
            'user_major': user_major,
            'user_focus': user_focus,
        },
    )


@login_required
def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploader = request.user
            resource.save()
            messages.success(request, 'Material uploaded — thanks for helping your peers.')
            return redirect('resource_list')
    else:
        major = (request.user.profile.current_major or '').strip()
        form = ResourceForm(initial={'subject': major} if major else {})
    return render(request, 'add_resource.html', {'form': form})


@login_required
def resource_list(request):
    query = (request.GET.get('q') or '').strip()
    qs = Resource.objects.select_related('uploader').order_by('-uploaded_at')
    if query:
        qs = qs.filter(
            Q(course_code__icontains=query)
            | Q(subject__icontains=query)
            | Q(title__icontains=query)
        )
    return render(
        request,
        'resources.html',
        {'resources': qs, 'query': query},
    )


@login_required
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.uploader_id != request.user.id:
        raise PermissionDenied()
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated.')
            return redirect('resource_list')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'edit_resource.html', {'form': form, 'resource': resource})


@login_required
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.uploader_id != request.user.id:
        raise PermissionDenied()
    if request.method == 'POST':
        resource.delete()
        messages.info(request, 'Resource removed.')
        return redirect('resource_list')
    return render(request, 'confirm_delete.html', {'resource': resource})


def _supply_peer_q(user):
    major = (user.profile.current_major or '').strip()
    focus = (user.profile.learning_focus or '').strip()
    q = Q()
    if major:
        q |= Q(subject_area__iexact=major)
        q |= Q(owner__profile__current_major__iexact=major)
    if focus:
        q |= Q(subject_area__icontains=focus)
    return q


@login_required
def marketplace(request):
    search = (request.GET.get('search') or '').strip()
    show_all = request.GET.get('all') == '1'
    qs = Supply.objects.filter(is_available=True).select_related('owner', 'owner__profile')
    if search:
        qs = qs.filter(
            Q(item_name__icontains=search) | Q(description__icontains=search)
        )
    peer_q = _supply_peer_q(request.user)
    peers_first = False
    fallback_all = False
    if not show_all and peer_q:
        peer_supplies = qs.filter(peer_q).distinct().order_by('-id')
        if peer_supplies.exists():
            supplies = peer_supplies
            peers_first = True
        else:
            supplies = qs.order_by('-id')
            fallback_all = True
    else:
        supplies = qs.order_by('-id')
    return render(
        request,
        'marketplace.html',
        {
            'supplies': supplies,
            'search': search,
            'show_all': show_all,
            'peers_first': peers_first,
            'fallback_all': fallback_all,
            'user_major': (request.user.profile.current_major or '').strip(),
            'user_focus': (request.user.profile.learning_focus or '').strip(),
        },
    )


@login_required
def add_supply(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST)
        if form.is_valid():
            supply = form.save(commit=False)
            supply.owner = request.user
            supply.save()
            messages.success(request, 'Your supply listing was added.')
            return redirect('marketplace')
    else:
        major = (request.user.profile.current_major or '').strip()
        form = SupplyForm(initial={'subject_area': major} if major else {})
    return render(request, 'add_supply.html', {'form': form})
