from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, Resource, Supply
from .forms import ResourceForm, SupplyForm
from Hacktesttues.materiali import models
from django.core.exceptions import PermissionDenied

@login_required
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.uploader != request.user:
        raise PermissionDenied("You do not have permission to delete this resource.")
    if request.method == 'POST':
        resource.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'resource': resource})

@login_required
def add_supply(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user # Link the item to the logged-in user
            item.save()
            return redirect('marketplace')
    else:
        form = SupplyForm()
    return render(request, 'add_supply.html', {'form': form})

def marketplace(request):
    user_focus = request.user.profile.learning_focus
    query = request.GET.get('search')
    if query:
        supplies = Supply.objects.filter(item_name__icontains=query, is_available=True)
    else:
        supplies = Supply.objects.filter(is_available=True).order_by('-id')  # Show newest first
        return render(request, 'marketplace.html', {
            'supplies': supplies,
            'user_focus': user_focus,
        })

@login_required
def dashboard(request):
    user_major = request.user.profile.current_major
    resources = Resource.objects.filter(subject=user_major)
    supplies = Supply.objects.filter(is_available=True)
    recomended_resources = Resource.objects.filter(subject=user_major)[:5]
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            new_resource = form.save(commit=False)
            new_resource.uploader = request.user  # Attach the logged-in user
            new_resource.save()
            return redirect('dashboard.html')
    else:
        form = ResourceForm()
    context = {
        'resources': recomended_resources,
        'supplies': supplies,
        'form': form,
        'major': user_major,
    }
    return render(request, 'materiali/dashboard.html', context)

def resource_list(request):
    query = request.GET.get('q')
    if query:
        results = Resource.objects.filter(
            models.Q(course_code__icontains=query) |
            models.Q(subject__icontains=query) |
            models.Q(title__icontains=query)
        )
    else:
        resources = Resource.objects.all()

    return render(request, 'materiali/resource_list.html', {'resources': results})