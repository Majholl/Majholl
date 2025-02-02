from django.shortcuts import render , redirect
from django.http import HttpRequest , HttpResponse 
from django.template import loader
from django.core.paginator import Paginator

from django.contrib import messages
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required , user_passes_test


from .models import users , products , admins


# Create your views here.


def load_product(request):
    
    products_ = products.objects.all() 
    template = loader.get_template('products.html')

    page_number = request.GET.get('page')
    Paginator_ = Paginator(products_ , 3)
    page_obj = Paginator_.get_page((page_number))

    for i in page_obj:
        i.data_limit = int(i.data_limit)
        i.product_price = format(i.product_price , ',')
        

    context = {'products' : page_obj}
    return HttpResponse(template.render(context , request))







def load_product_details(request , id):
    products_ = products.objects.get(id = int(id))
    template = loader.get_template('product_details.html')
    products_.data_limit = int(products_.data_limit)
    products_.product_price = format(products_.product_price , ',')
    context = {'pro_detail' : products_}
    return HttpResponse(template.render(context , request))






def login_view(request):
    if 'user_id' in request.session:
        return redirect('admin_dashboard')

    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try :
            if len(username) < 2 :
                messages.error(request , 'فیلد های بالا باید با مقدار مناسب پرشوند')
            else:
                admins_users = admins.objects.get(user_id = username)   
                if admins_users.password == password:
                    request.session['user_id'] = admins_users.user_id
                    return redirect('admin_dashboard')  
                else:
                    messages.error(request , 'رمز اشتباه است.')

        except admins.DoesNotExist:
            messages.error(request , 'کاربری با این مقدار یافت نشد.')
    return render(request , 'login.html')





def admin_dashboard(request):
    print(request)
    if 'user_id' not in request.session:
        return redirect('login')
    admin_user = admins.objects.get(user_id = request.session['user_id'])
    return render(request , 'dashboard.html' , {'admin_user' : admin_user})
    





def logout_view(request):
    request.session.flush()
    return redirect('login')




def manage_users(request):
    users_ = users.objects.all()
    template = loader.get_template('manage_users.html')
    context = {'users' : users_}
    
    return HttpResponse(template.render(context , request))