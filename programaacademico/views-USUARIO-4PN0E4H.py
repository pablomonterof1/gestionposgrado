from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdmisionForm
from .models import Admision
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def admision(request):
    admision_list = Admision.objects.filter(
        important=True).order_by('-created')
    return render(request, 'admision.html', {
        'admision_list': admision_list
    })

@login_required
def admision_create(request):
    if request.method == 'POST':
        try:
            form = AdmisionForm(request.POST)
            form.save()
            return redirect('admision')
        except ValueError:
            return render(request, 'admision_create.html', {
                'form': AdmisionForm,
                'error': 'Error al crear la admisión'
            })
    else:
        return render(request, 'admision_create.html', {
            'form': AdmisionForm
        })

@login_required
def admision_detail(request, admision_id):
    if request.method == 'POST':
        admision = get_object_or_404(Admision, id=admision_id)
        admisionform = AdmisionForm(request.POST, instance=admision)
        if admisionform.is_valid():
            admisionform.save()
            return redirect('admision')
    else:
        admision = get_object_or_404(Admision, id=admision_id)
        admisionform = AdmisionForm(instance=admision)
        return render(request, 'admision_detail.html', {
            'admision': admision,
            'admisionform': admisionform
        })

@login_required
def admision_delete(request, admision_id):
    admision = get_object_or_404(Admision, id=admision_id)
    if request.method == 'POST':
        admision.delete()
        return redirect('admision')
    return render(request, 'admision_delete.html', {
        'admision': admision
    })
