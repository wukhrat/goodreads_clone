from django.urls import path
from api.views import BookReviewDetailApiView, BookReviewsApiView

app_name = "api"
urlpatterns = [
    path("reviews/", BookReviewsApiView.as_view(), name="review-list"),
    path("reviews/<int:id>/", BookReviewDetailApiView.as_view(), name="review-detail"),

]