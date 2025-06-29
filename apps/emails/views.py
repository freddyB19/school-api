from django.shortcuts import render

# Create your views here.


def test_view_email(request):
	context = {
		"name": "Freddy",
		"password": "123456"
	}
	return render(request, "emails/reset_user_password.html", context)