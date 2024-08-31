from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from .models import Photo, Album
from PIL import Image, ImageDraw, ImageFont
from django import forms
from .forms import FileFieldForm, AlbumForm, PhotoForm
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_album')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('create_album')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def upload_photo(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        watermark_text = request.POST['watermark']
        photo = Photo(image=image, watermark_text=watermark_text)
        photo.save()
        return render(request, 'delivery/upload_success.html')
    return render(request, 'delivery/upload.html')

def watermark_photo(photo):
    input_image_path = photo.image.path
    output_image_path = f'watermarked/{photo.image.name}'

    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = photo.watermark_text
    textwidth, textheight = draw.textsize(text, font)
    width, height = image.size
    x, y = width - textwidth - 10, height - textheight - 10
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    image.save(output_image_path)
    return output_image_path

@login_required
def album_list(request):
    albums = Album.objects.filter(user=request.user)
    return render(request, 'delivery/album_list.html', {'albums': albums})

@login_required
def album_detail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    photos = album.photos.all()
    return render(request, 'delivery/album_detail.html', {'album': album, 'photos': photos})


@login_required
def create_album(request):
    if request.method == 'POST':
        album_form = AlbumForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)

        if album_form.is_valid() and photo_form.is_valid():
            album = album_form.save()

            images = request.FILES.getlist('images')
            watermarked = photo_form.cleaned_data.get('watermarked')

            for image in images:
                photo_instance = Photo(album=album, image=image, watermarked=watermarked)
                photo_instance.save()

                if watermarked:
                    apply_watermark(photo_instance)

            return redirect('album_list')
    else:
        album_form = AlbumForm()
        photo_form = PhotoForm()

    return render(request, 'delivery/create_album.html', {
        'album_form': album_form,
        'photo_form': photo_form,
    })

def apply_watermark(photo_instance):
    image = Image.open(photo_instance.image.path)
    watermark_text = "Watermark"  # Example watermark text
    watermark_position = (10, 10)  # Position of the watermark

    # Apply the watermark
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text(watermark_position, watermark_text, font=font)

    # Save the watermarked image
    image.save(photo_instance.image.path)


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "upload.html"  # Replace with your template.
    success_url = "..."  # Replace with your URL or reverse().

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
            ...  # Do something with each file.
        return super().form_valid(form)