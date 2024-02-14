from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.serializers import BookSerializer
from api.models import Book, Review

# Get All Books
@api_view(['GET'])
def getBooks(request):
    try:
        query = request.query_params.get('q', '')  # Use default value directly in get() method
        page = request.query_params.get('page', 1)

        books = Book.objects.filter(name__icontains=query).order_by('-createdAt')
        paginator = Paginator(books, 4)

        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)

        serializer = BookSerializer(books, many=True)
        return Response({'books': serializer.data, 'page': page, 'pages': paginator.num_pages})

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Get Top Books (based on rating)
@api_view(['GET'])
def getTopRatedBooks(request):
    try:
        # Retrieve top 8 books based on rating
        top_rated_books = Book.objects.filter(rating__isnull=False).order_by('-rating')[:8]

        serializer = BookSerializer(top_rated_books, many=True)
        return Response({'top_rated_books': serializer.data})

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Get Best Selling Books
@api_view(['GET'])
def getBestSellingBooks(request):
    try:
        # Retrieve top 8 best-selling books
        best_selling_books = Book.objects.filter(numOfSales__isnull=False).order_by('-numOfSales')[:8]

        serializer = BookSerializer(best_selling_books, many=True)
        return Response({'best_selling_books': serializer.data})

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Get a Book
@api_view(['GET'])
def getBook(request, pk):
    try:
        book = Book.objects.get(id=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    except Book.DoesNotExist:
        return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Get a Category of Books
@api_view(['GET'])
def getCategoryOfBooks(request, name):
    try:
        query = request.query_params.get('q', '')
        books = Book.objects.filter(category__icontains=name, name__icontains=query).order_by('-createdAt')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Create a Book
@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'author', 'image', 'price', 'description', 'category', 'count-in-stock'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'author': openapi.Schema(type=openapi.TYPE_STRING),
        'image': openapi.Schema(type=openapi.TYPE_FILE),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING),
        'count-in-stock': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createBook(request):
    try:
        data = request.data
        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update a Book
@swagger_auto_schema(method='put', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'author', 'image', 'price', 'description', 'category', 'count-in-stock'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'author': openapi.Schema(type=openapi.TYPE_STRING),
        'image': openapi.Schema(type=openapi.TYPE_FILE),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING),
        'count-in-stock': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateBook(request, pk):
    try:
        book = Book.objects.get(id=pk)
        data = request.data
        serializer = BookSerializer(book, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Book.DoesNotExist:
        return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Delete a Book
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteBook(request, pk):
    try:
        book = Book.objects.get(id=pk)
        book.delete()
        return Response('Book was deleted successfully')

    except Book.DoesNotExist:
        return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Create a Book Review
@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['rating', 'comment'],
    properties={
        'rating': openapi.Schema(type=openapi.TYPE_INTEGER, format='int32'),
        'comment': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBookReview(request, pk):
    try:
        user = request.user
        book = Book.objects.get(id=pk)
        data = request.data

        # Check if review already exists
        already_exists = Review.objects.filter(user=user, book=book).exists()
        if already_exists:
            return Response({'detail': 'Review already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create review
        review = Review.objects.create(
            user=user,
            book=book,
            rating=data['rating'],
            comment=data['comment']
        )

        # Update book ratings
        reviews = Review.objects.filter(book=book)
        total_ratings = sum([review.rating for review in reviews])
        book.numOfReviews = len(reviews)
        book.rating = total_ratings / len(reviews)
        book.save()

        return Response('Review added successfully')

    except Book.DoesNotExist:
        return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle unexpected errors
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
