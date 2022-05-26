# from asyncio.windows_events import NULL
import email
import profile
from re import template
import subprocess
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from authentication.forms import ProfileForm
from webtrustapp import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from . import models
from authentication.models import Profile
from django.views.generic import DetailView
# Create your views here.

class ProfileView(DetailView):
    model = User
    template_name = 'authentication/profile.html'

    def get_context_data(self, *args, **kwargs):
        users = User.objects.all()
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        page_user = get_object_or_404(User, id=self.kwargs['pk'])
        context["page_user"] = page_user
        return context

def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        models.Profile.objects.create(user=myuser)
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to TrustWebApp!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to TrustWebApp!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. "        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
        
    return render(request, "authentication/signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser,backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
        # return render(request, "authentication/fb_login.html")
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            # fname = user.first_name
            # email = user.email 
            # trustscore = user.profile.trustscore
            # fb = user.profile.fb_url
            # username = user.username
            # messages.success(request, "Logged In Sucessfully!!")
            # if not user.profile.profile_pic:
            if not models.Profile.objects.filter(user=user).exists():
                models.Profile.objects.create(user=request.user)
            if not user.profile.profile_pic:
                return render(request, "authentication/upload.html")
            return render(request, "authentication/index.html")
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

# @login_required
def upload(request):
    if request.method == 'POST':
        p_form = ProfileForm(request.POST , request.FILES, instance=request.user.profile)
  
        if p_form.is_valid():
            # # username = request.POST['user']
            # m=User(user=request.user)
            # m.profile_pic=request.FILES['frormFile']
            # m.save()
            # newuser = User.profile
            # newuser = 
            # models.Profile.filter(user=request.user).profile_pic = request.FILES['formFile']
            p_form.save()
            return render(request, 'authentication/links.html')
    else:
        form = ProfileForm()
    return render(request, 'authentication/upload.html', {'form' : form})


def index(request):
    user=request.user
    if user is not None:
        return render(request, 'authentication/index.html')
    else:
        return render(request, "authentication/signin.html")

def search(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        users = User.objects.filter(username__contains = searched)

        return render(request, "authentication/search.html", {'searched':searched, 'users':users})


def links(request):
    if request.method == "POST":
        fb_url = request.POST['fb_url']
        insta_url = request.POST['insta_url']
        request.user.profile.fb_url = fb_url
        request.user.profile.insta_url = insta_url
        request.user.profile.save()
        return render(request, 'authentication/index.html')


def verify(request):
    # process = subprocess.Popen(['python','main.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # output = process.stdout.read() 
    # if output == "spoof":
    #     messages.error(request, "Spoofed Face, try again.")
    # else:
        return render(request, 'authentication/webcam.html')

    # return render(request, 'authentication/index.html')

def verification(request):
    process = subprocess.Popen(['python','getfaces.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # exitstatus = process.poll()
    code2 = subprocess.Popen(['python','compare.py','opencv9.jpg',request.user.profile.profile_pic], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = code2.stdout.read()
    output = str(output)
    print(type(output))
    print(output)
    t = "b'[True]\n'"
    if output.find(t):
        messages.success(request, "Verification Sucessful")
        request.user.profile.verified = True
        request.user.profile.trustscore += 5
        request.user.profile.save()
        return render(request, 'authentication/index.html')
    else:
        return render(request, 'authentication/webcam.html')

    # return render(request, 'authentication/index.html')
