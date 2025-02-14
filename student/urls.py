from django.urls import path
from student import views

urlpatterns=[
    path("register/",views.StudentRegistrationView.as_view(),name="student-register"),
    path("signin/",views.SignInView.as_view(),name="signin"),
    path("index/",views.IndexView.as_view(),name="index"),
    path("courses/<int:pk>/",views.CourseDetailView.as_view(),name="course-detail"),
    path("courses/<int:pk>/add-to-cart/",views.AddToCartView.as_view(),name="add-to-cart"),
    path("cart/summary/",views.CartSummmaryView.as_view(),name="cart-summary"),
    path("cart/<int:pk>/remove/",views.CartItemDeleteView.as_view(),name="cart-item-remove"),
    path("checkout/",views.CheckOutView.as_view(),name="check-out"),
    path("mycourses/",views.MyCoursesView.as_view(),name="mycourses"),
    path("courses/<int:pk>/watch/",views.LessonDetailView.as_view(),name="lesson-detail"),
    path("payment/verify/",views.PaymentVerificationView.as_view(),name="payment-verify"),
    path("signout/",views.SignoutView.as_view(),name="logout"),

]