# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Breed, Dog
from .forms import DogForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages

@require_http_methods(["POST"])
@login_required
def add_dog_to_profile(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)

    if dog.owner:
        messages.error(request, f"Собака '{dog.name}' уже принадлежит пользователю {dog.owner.username}.")
    else:
        dog.owner = request.user
        dog.save()
        messages.success(request, f"Собака '{dog.name}' успешно добавлена в ваш профиль.")

    return redirect(request.META.get('HTTP_REFERER', reverse('dogs:dogs_list')))

@require_http_methods(["DELETE"])
@login_required
def remove_dog_from_profile(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id, owner=request.user)
    dog.owner = None
    dog.save()
    return JsonResponse({'message': 'Собака успешно удалена из профиля.'})

@login_required
def index(request):
    title = 'Главная страница'
    context = {'title': title}
    return render(request, 'dogs/index.html', context)


@login_required
def breeds(request):
    title = 'Породы собак'
    breeds = Breed.objects.all()
    breeds_data = []
    for breed in breeds:
        dogs = Dog.objects.filter(breed=breed).order_by('?')[:3]
        breeds_data.append({'breed': breed, 'dogs': dogs})
    context = {'title': title, 'breeds_data': breeds_data}
    return render(request, 'dogs/breeds.html', context)

@login_required
def dogs_list(request):
    title = 'Список всех собак'
    dogs = Dog.objects.all()
    context = {'title': title, 'dogs': dogs}
    return render(request, 'dogs/dogs_list.html', context)

@login_required
def dog_create(request):
    title = 'Добавить собаку'
    if request.method == 'POST':
        form = DogForm(request.POST, request.FILES)
        if form.is_valid():
            dog = form.save()
            messages.success(request, f"Собака '{dog.name}' успешно добавлена!")
            return redirect('dogs:dogs_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form[field].label}: {error}")
    else:
        form = DogForm()

    context = {'title': title, 'form': form}
    return render(request, 'dogs/dog_create.html', context)

@login_required
def dog_update(request, pk):
    title = 'Редактировать информацию о собаке'
    dog = get_object_or_404(Dog, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = DogForm(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            messages.success(request, f"Информация о собаке '{dog.name}' успешно обновлена!")
            return redirect('dogs:dog_read', pk=dog.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form[field].label}: {error}")
    else:
        form = DogForm(instance=dog)

    context = {'title': title, 'form': form, 'dog': dog}
    return render(request, 'dogs/dog_update.html', context)

@login_required
def dog_delete(request, pk):
    dog = get_object_or_404(Dog, pk=pk, owner=request.user)
    dog_name = dog.name
    dog.delete()
    messages.success(request, f"Собака '{dog_name}' успешно удалена.")
    return redirect(reverse('dogs:dogs_list'))

@login_required
def dog_read(request, pk):
    title = 'Информация о собаке'
    dog = get_object_or_404(Dog, pk=pk)
    is_owner = dog.owner == request.user
    context = {'title': title, 'dog': dog, 'is_owner': is_owner}
    return render(request, 'dogs/dog_read.html', context)

@login_required
def all_dogs(request):
    title = 'Все собаки'
    dogs = Dog.objects.all()
    context = {'title': title, 'dogs': dogs}
    return render(request, 'dogs/all_dogs.html', context)

