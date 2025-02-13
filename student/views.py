from django.shortcuts import render,redirect
from django.views.generic import View,FormView,TemplateView,CreateView
from student.forms import StudentCreateForm,SignInForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login
from instructor.models import Course,Cart,Order,Lesson,Module
from django.db.models import Sum
import razorpay


RZP_KEY_ID="rzp_test_EYY5XmeS5VDAYk"
RZP_KEY_SECRET="n0Dt9S6aHY7NHuUzXYMuAl3a"
# Create your views here.
class StudentRegistrationView(CreateView):

    template_name="student_register.html"

    form_class=StudentCreateForm

    success_url=reverse_lazy("signin")

class SignInView(FormView):

    template_name="signin.html"

    form_class=SignInForm

    def post(self,request,*args,**kwargs):

        form_data=request.POST

        form_instance=SignInForm(form_data)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            uname=data.get("username")

            pwd=data.get("password")

            user_instance=authenticate(request,username=uname,password=pwd)

            if user_instance:

                login(request,user_instance)

                return redirect("index")

        return render(request,"signin.html",{"form":form_instance})
    
class IndexView(View):

   def get(self,request,*args,**kwargs):
       
       all_courses=Course.objects.all()

       purchased_courses=request.user.purchase.all().values_list("course_objects",flat=True)

       print(purchased_courses,"================")

       return render(request,"home.html",{"courses":all_courses,"purchased_courses":purchased_courses})
   

class CourseDetailView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        course_instance=Course.objects.get(id=id)

        return render(request,"course_detail.html",{"course":course_instance})
    
class AddToCartView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        course_instance=Course.objects.get(id=id)

        user_instance=request.user

        cart_instance,created=Cart.objects.get_or_create(course_object=course_instance,user=user_instance)

        print(created)

        return redirect("index")

class CartSummmaryView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.basket.all()

        cart_total=qs.values("course_object__price").aggregate(total=Sum("course_object__price")).get("total")

        print("======" ,cart_total)

        return render(request,"cart-summary.html",{"carts":qs,"basket_total":cart_total})

class CartItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Cart.objects.get(id=id).delete()

        return redirect("cart-summary") 

class CheckOutView(View):

    def get(self,request,*args,**kwargs):

        cart_items=request.user.basket.all()
        
        order_total=sum([ci.course_object.price for ci in cart_items])
        
        order_instance=Order.objects.create(student=request.user,total=order_total)

        for ci in cart_items:

            order_instance.course_objects.add(ci.course_object)

            ci.delete()
        order_instance.save()

        if order_total>0:

          client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

          data = { "amount": int(order_total*100), "currency": "INR", "receipt": "order_rcptid_11" }

          payment = client.order.create(data=data)

          rzp_id=payment.get("id")

          order_instance.rzp_order_id=rzp_id

          order_instance.save()

          context={
             "rzp_key_id":RZP_KEY_ID,
             "amount":int(order_total*100),
             "rzp_order_id":rzp_id,
             
           } 
          return render(request,"payment.html",context)
         
        elif order_total==0:

            order_instance.is_paid=True
            
            order_instance.save()

        return redirect("index") 

class MyCoursesView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.purchase.filter(is_paid=True)

        return render(request,"mycourses.html",{"orders":qs})


class LessonDetailView(View):

    def get(self,request,*args,**kwargs):

        course_id=kwargs.get("pk")

        course_instance=Course.objects.get(id=course_id)

        query_params=request.GET

        module_id=query_params.get("module") if "module" in query_params else course_instance.modules.all().first().id

        module_instance=Module.objects.get(id=module_id,course_object=course_instance)

        lesson_id=query_params.get("lesson") if "lesson" in query_params else module_instance.lessons.all().first().id

        lesson_instance=Lesson.objects.get(id=lesson_id,module_object=module_instance)

        return render(request,"lesson_detail.html",{"course":course_instance,"lesson":lesson_instance})          

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator([csrf_exempt],name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST,"+++++++++++++++")
        
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))
        try:
          client.utility.verify_payment_signature(request.POST)

          print("payment success")
          
          rzp_order_id=request.POST.get("razorpay_order_id")

          order_instance=Order.objects.get(rzp_order_id=rzp_order_id)

          order_instance.is_paid=True

          order_instance.save()



        except:
            print("payment failed")

        return redirect("index")        

        


