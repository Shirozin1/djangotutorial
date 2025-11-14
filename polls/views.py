from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, Usuario

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
        ]
    
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/details.html"
    
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

# Create your views here.
def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    if request.user.is_authenticated:
        print(f"Usuário logado: {request.user.username}")
        # Pode fazer ações específicas para usuários logados
        mensagem = f"Bem-vindo de volta, {request.user.username}!"
    else:
        print("Usuário não está logado")
        # Pode redirecionar ou mostrar conteúdo diferente
        mensagem = "Bem-vindo! Faça login para continuar."
    return render(request, "polls/index.html", context)

def details(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/details.html", {"question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos!')

    return render(request, 'polls/login.html')

def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('polls:login')

def registro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'As senhas não são iguais!')
            return render(request, 'polls/registro.html')
        
        if len(password) < 6:
            messages.error(request, "A senha deve ter pelo menos 6 caracteres!")
            return render(request, 'polls/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já utilizado!')
            return render(request, 'polls/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado!')
            return render(request, 'polls/registro.html')
        
        # Cria o usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Cria o perfil
        perfil = Usuario.objects.create(
            user=user,
            data_nascimento=data_nascimento if data_nascimento else None,
            idade=idade if idade else None
        )

        messages.success(request, 'Conta criada com sucesso! Agora faça login.')
        return redirect('login')
    
    return render(request, 'polls/registro.html')



# View protegida (requer login)
@login_required(login_url='login')
def perfil_view(request):
    #request.user já esta disponivel e autenticado
    return render(request, 'polls/perfil.html', {'user': request.user})
