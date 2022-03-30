from django.shortcuts import render,redirect
from .models import User,Course,Questions,Result,Faculty_Subject
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
import random
from django.conf import settings
from django.core.mail import send_mail

# Create your views here.

# def change_status(request):
# 	status = request.GET.get('status', None)
# 	user=User.objects.get(pk=status)
# 	user.status="approved"
# 	user.save()
# 	#students=User.objects.filter(usertype="student")
# 	#
# 	#return HttpResponse(qs_json, content_type='application/json')
# 	qs_json = serializers.serialize('json', [user,])
# 	print(qs_json)
# 	return HttpResponse(qs_json)
	

def validate_username(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)
def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="student":
			return render(request,'index.html')
		else:
			return render(request,'faculty_index.html')
	except:
		return render(request,'index.html')

def faculty_index(request):
	return render(request,'faculty_index.html')

def contact(request):
	return render(request,'contact.html')

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						usertype=request.POST['usertype'],
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic']
					)
				msg="User Sign Up Successfull"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})

	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password']
				)
			if user.status=="pending":
				msg="Your Login Status Is Not Approved"
				return render(request,'login.html',{'msg':msg})

			elif user.usertype=="student":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return render(request,'index.html')
			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				return render(request,'faculty_index.html')

		except:
			msg="Email Or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['password']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Does Not Matched"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')

def faculty_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'faculty_change_password.html',{'msg':msg})
		else:
			msg="Old Password Does Not Matched"
			return render(request,'faculty_change_password.html',{'msg':msg})
	else:
		return render(request,'faculty_change_password.html')

def mystudents(request):
	students=User.objects.filter(usertype="student")
	return render(request,'mystudents.html',{'students':students})

def change_status(request,pk):
	student=User.objects.get(pk=pk)
	student.status="approved"
	student.save()
	return redirect('mystudents')

def add_course(request):
	if request.method=="POST":
		faculty=User.objects.get(email=request.session['email'])
		Course.objects.create(
				faculty=faculty,
				cname=request.POST['cname']
			)
		msg="Course Added Successfully"
		courses=Course.objects.all()
		return render(request,'add_course.html',{'msg':msg,'courses':courses})
	else:
		courses=Course.objects.all()
		return render(request,'add_course.html',{'courses':courses})

def add_questions(request):
	courses=Course.objects.all()
	if request.method=="POST":
		course=Course.objects.get(pk=request.POST['cname'])
		Questions.objects.create(
				cname=course,
				question=request.POST['question'],
				op1=request.POST['op1'],
				op2=request.POST['op2'],
				op3=request.POST['op3'],
				op4=request.POST['op4'],
				answer=request.POST['answer']
			)
		msg="Question Added Successfully"
		return render(request,'add_questions.html',{'courses':courses,'msg':msg})
	else:
		return render(request,'add_questions.html',{'courses':courses})

def exam(request):
	courses=Course.objects.all()
	return render(request,'exam.html',{'courses':courses})

def exam_course(request,cname):
	return render(request,'exam_instruction.html',{'cname':cname})

def start_exam(request,cname):
	course=Course.objects.get(cname=cname)
	questions=Questions.objects.filter(cname=course)
	questions=set(questions)
	que=random.sample(questions,3)
	return render(request,'mcq.html',{'questions':que})

def exam_checker(request):
	user=User.objects.get(email=request.session['email'])
	l=list(request.POST.items())[1:]
	marks=0
	for i in l:
		question=Questions.objects.get(pk=i[0])
		course=Course.objects.get(cname=question.cname.cname)
		print(course)
		if question.answer==i[1]:
			marks=marks+1
	result=Result.objects.create(
			student=user,
			course=course,
			marks=marks
		)
	subject = 'Exam Result'
	message = 'You have given '+result.course.cname+' exam.\n You have obtain '+str(result.marks)
	email_from = settings.EMAIL_HOST_USER
	recipient_list = [user.email, ]
	send_mail( subject, message, email_from, recipient_list )
	return redirect('myresult')

def myresult(request):
	student=User.objects.get(email=request.session['email'])
	print(student)
	result=Result.objects.filter(student=student)
	return render(request,'myresult.html',{'result':result})

def result(request):
	faculty=User.objects.get(email=request.session['email'])
	course=Course.objects.get(faculty=faculty)
	result=Result.objects.filter(course=course)
	return render(request,'result.html',{'result':result})

def faculty_profile(request):
	faculty=User.objects.get(email=request.session['email'])
	faculty_subject=Faculty_Subject.objects.filter(faculty=faculty)
	if request.method=="POST":
		try:
			Faculty_Subject.objects.get(faculty=faculty,subject=request.POST['subject'])
			msg="You Already Selected This Subject"
			return render(request,'faculty_profile.html',{'faculty_subject':faculty_subject,'msg':msg})
		except:
			Faculty_Subject.objects.create(
					faculty=faculty,
					subject=request.POST['subject']
				)
			return render(request,'faculty_profile.html',{'faculty_subject':faculty_subject})
	else:
		return render(request,'faculty_profile.html',{'faculty_subject':faculty_subject})