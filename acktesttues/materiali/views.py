from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Profile, Resource, Supply
from .forms import ResourceForm

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