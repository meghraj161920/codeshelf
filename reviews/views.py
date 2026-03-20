from django.shortcuts import render, redirect
from .models import Review
from projects.models import Project


def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/review_list.html', {'reviews': reviews})


def add_review(request):
    if request.method == "POST":
        review_text = request.POST.get("comment")
        rating = request.POST.get("rating")
        project_id = request.POST.get("project_id")

        project = Project.objects.get(id=project_id)

        Review.objects.create(
            user=request.user,
            project=project,
            rating=rating,
            review_text=review_text
        )

        return redirect('reviews')   # 👈 better redirect

    return render(request, 'reviews/add_review.html')