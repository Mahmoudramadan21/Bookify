from django.urls import path
from api.views import book_views as views

urlpatterns = [

    path('', views.getBooks, name="Books"),
    path('top/', views.getTopRatedBooks, name='top-Books'),
    path('best-sales/', views.getBestSellingBooks, name='top-Books'),

    path('category/<str:name>/', views.getCategoryOfBooks, name="Book-category"),
    path('<int:pk>/', views.getBook, name="Book"),

    path('create/', views.createBook, name="Book-create"),
    path('update/<int:pk>/', views.updateBook, name="Book-update"),
    path('delete/<int:pk>/', views.deleteBook, name="Book-delete"),

    path('<int:pk>/reviews/', views.createBookReview, name="create-review"),
]