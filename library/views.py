from django.shortcuts import render
from library.models import Books, Storages, Loans, Comments, Reserves
from django.contrib.auth.decorators import login_required
from .forms import SearchBookForm

@login_required
def books(request):
    if request.method == 'POST':
        form = SearchBookForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            books = Books.objects.filter(isbn__icontains=text) | \
                    Books.objects.filter(title__icontains=text) | \
                    Books.objects.filter(authors__icontains=text) | \
                    Books.objects.filter(publisher__icontains=text)
        else:
            books = Books.objects.all()
    else:
        form = SearchBookForm()
        books = Books.objects.all()

    all = []
    for book in books:
        storages = Storages.objects.filter(isbn=book.isbn)
        loaned_count = Loans.objects.filter(stono__in=storages, return_date__isnull=True, admin_id__isnull=True).count()
        dic = {'isbn': book.isbn, 'title': book.title, 'authors': book.authors,
               'publisher': book.publisher, 'price': book.price,
               'count': storages.count(), 'loaned': loaned_count}
        all.append(dic)

    context = {'form': form, 'books': all}
    return render(request, 'books.html', context)


@login_required
def book(request, book_isbn):
    book = Books.objects.get(isbn=book_isbn)
    storages = Storages.objects.filter(isbn=book.isbn).order_by('lno')
    comments = Comments.objects.filter(isbn=book.isbn)
    all = []

    for storage in storages:
        try:
            loan = Loans.objects.get(stono=storage.stono, return_date__isnull=True, admin_id__isnull=True)
            due_date = loan.due_date
            available = 0
        except Loans.DoesNotExist:
            due_date = None
            available = 1
        try:
            reserve = Reserves.objects.get(stono=storage.stono, admin_id__isnull=True)
            reservable = 0
        except Reserves.DoesNotExist:
            reservable = 1
        dic = {'stono': storage.stono, 'isbn': storage.isbn, 'lno': storage.lno,
               'due_date': due_date, 'available': available, 'reservable': reservable}
        all.append(dic)

    context = {'book': book, 'storages': all, 'comments': comments}
    return render(request, 'book.html', context)

def signup(request):
    form = UserCreationForm(data=request.POST) if request.method == 'POST' else UserCreationForm()
    
    if request.method == 'POST' and form.is_valid():
        new_user = form.save()
        authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
        login(request, authenticated_user)
        return HttpResponseRedirect(reverse('library:index'))
    
    context = {'form': form}
    return render(request, 'signup.html', context)

@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('library:index'))

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('library:profile'))
        else:
            error = form.errors
            return render(request, 'profile_edit.html', {'form': form, 'errors': error})
    else:
        form = ProfileForm(instance=request.user)
        return render(request, 'profile_edit.html', {'form': form})

@login_required
def loans(request):
    loans = []
    if request.user.is_staff:
        loans = models.Loans.objects.all()
    else:
        loans = models.Loans.objects.filter(id=request.user.id)
    
    all = []
    for loan in loans:
        try:
            reserve = models.Reserves.objects.get(stono=loan.stono, admin_id__isnull=True)
            reservable = 0
        except ObjectDoesNotExist:
            reservable = 1
        
        dic = {
            'loan_date': loan.loan_date, 'due_date': loan.due_date,
            'renewed': loan.renewed, 'stono': loan.stono,
            'id': loan.id, 'return_date': loan.return_date,
            'admin_id': loan.admin_id, 'loanno': loan.loanno,
            'reservable': reservable
        }
        all.append(dic)

    context = {'loans': all}
    return render(request, 'loans.html', context)

@login_required
def comments(request):
    if request.user.is_staff:
        comments = models.Comments.objects.all()
    else:
        comments = models.Comments.objects.filter(id=request.user.id)

    context = {'comments': comments}
    return render(request, 'comments.html', context)

@login_required
def loan(request, storage_stono):
    try:
        loan = models.Loans.objects.get(stono=storage_stono, return_date__isnull=True, admin_id__isnull=True)
    except ObjectDoesNotExist:
        try:
            reserve = models.Reserves.objects.get(stono=storage_stono, admin_id__isnull=True)
        except ObjectDoesNotExist:
            loan_date = now().date()
            due_date = loan_date + timedelta(days=30)
            storage = models.Storages.objects.get(stono=storage_stono)
            user = models.AuthUser.objects.get(id=request.user.id)
            add_loan = models.Loans.objects.create(loan_date=loan_date, due_date=due_date,
                                                   renewed=0, stono=storage, id=user)
            add_loan.save()

    return HttpResponseRedirect(reverse('library:loans'))

@login_required
def return_book(request, loan_loanno):
    if request.user.is_staff:
        try:
            loan = models.Loans.objects.get(loanno=loan_loanno)
            loan.return_date = now().date()
            loan.admin_id = request.user.id
            loan.save()
        except ObjectDoesNotExist:
            error = "Not loaned out"

    return HttpResponseRedirect(reverse('library:loans'))

@login_required
def addbook(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = AddBookForm(data=request.POST)
            if form.is_valid():
                add_book = models.Books.objects.create(isbn=form.cleaned_data['isbn'],
                                                       title=form.cleaned_data['title'],
                                                       authors=form.cleaned_data['authors'],
                                                       publisher=form.cleaned_data['publisher'],
                                                       price=form.cleaned_data['price'])
                add_book.save()
                lno = form.cleaned_data['lno']
                library = models.Libraries.objects.get(lno=lno)
                add_storage = models.Storages.objects.create(isbn=add_book, lno=library)
                add_storage.save()
                return HttpResponseRedirect(reverse('library:books'))
            else:
                error = form.errors
                context = {'form': form, 'error': error}
                return render(request, 'addbook.html', context)
        else:
            form = AddBookForm()
            context = {'form': form}
            return render(request, 'addbook.html', context)
    else:
        return HttpResponseRedirect(reverse('library:books'))


@login_required
def deletebook(request, storage_stono):
    if request.user.is_staff:
        #loaned out, can't be deleted
        try:
            loan = models.Loans.objects.get(stono=storage_stono, return_date__isnull=True, admin_id__isnull=True)
            return HttpResponseRedirect(reverse('library:books'))
        #not exist
        except ObjectDoesNotExist:
            #reserved, can't be deleted
            try:
                reserve = models.Reserves.objects.get(stono=storage_stono)
            except ObjectDoesNotExist:
                try:
                    storage = models.Storages.objects.get(stono=storage_stono)
                    count = models.Storages.objects.filter(isbn=storage.isbn.isbn).count()
                    storage_isbn = storage.isbn.isbn
                    loans = models.Loans.objects.filter(stono = storage.stono)
                    for loan in loans:
                        loan.delete()
                    storage.delete()
                    if count <= 1:
                        book = models.Books.objects.get(isbn=storage_isbn)
                        book.delete()

                    return HttpResponseRedirect(reverse('library:books'))
                except ObjectDoesNotExist:
                    return HttpResponseRedirect(reverse('library:books'))

    return HttpResponseRedirect(reverse('library:books'))

@login_required
def deletecomment(request, comment_comno):
    comment = get_object_or_404(models.Comments, comno=comment_comno)
    if request.user.id == comment.id.id or request.user.is_staff:
        comment.delete()
    return HttpResponseRedirect(reverse('library:comments'))

@login_required
def addcomment(request, book_isbn):
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            user = get_object_or_404(models.AuthUser, id=request.user.id)
            book = get_object_or_404(models.Books, isbn=book_isbn)
            comment = models.Comments.objects.create(isbn=book, text=text, id=user)
            comment.save()
            return HttpResponseRedirect(reverse('library:books'))
        else:
            error = form.errors
            context = {'form': form, 'error': error}
            return HttpResponseRedirect(reverse('library:books'))
    else:
        form = CommentForm()
        book = get_object_or_404(models.Books, isbn=book_isbn)
        context = {'form': form, 'book_isbn': book_isbn, 'book': book}
        return render(request, 'addcomment.html', context)

@login_required
def renew(request, loan_loanno):
    loan = get_object_or_404(models.Loans, loanno=loan_loanno, return_date__isnull=True, admin_id__isnull=True)
    if request.user.id == loan.id.id or request.user.is_staff:
        if loan.renewed:
            return HttpResponseRedirect(reverse('library:loans'))
        else:
            loan.due_date += timedelta(days=30)
            loan.renewed = 1
            loan.save()
            return HttpResponseRedirect(reverse('library:loans'))
    else:
        return HttpResponseRedirect(reverse('library:loans'))

@login_required
def reserves(request):
    if request.user.is_staff:
        reserves = models.Reserves.objects.all()
    else:
        reserves = models.Reserves.objects.filter(id=request.user.id)
    context = {'reserves': reserves}
    return render(request, 'reserves.html', context)

@login_required
def reservebook(request, storage_stono):
    try:
        get_object_or_404(models.Loans, stono=storage_stono, admin_id__isnull=True, return_date__isnull=True)
        return HttpResponseRedirect(reverse('library:books'))
    except models.Loans.DoesNotExist:
        try:
            get_object_or_404(models.Reserves, stono=storage_stono, admin_id__isnull=True)
            return HttpResponseRedirect(reverse('library:books'))
        except models.Reserves.DoesNotExist:
            if request.method == 'POST':
                form = ReserveForm(data=request.POST)
                if form.is_valid():
                    lno = form.cleaned_data['lno']
                    library = get_object_or_404(models.Libraries, lno=lno)
                    storage = get_object_or_404(models.Storages, stono=storage_stono)
                    try:
                        get_object_or_404(models.Storages, stono=storage_stono, lno__lno=lno)
                        return HttpResponseRedirect(reverse('library:books'))
                    except models.Storages.DoesNotExist:
                        user = get_object_or_404(models.AuthUser, id=request.user.id)
                        reserve = models.Reserves.objects.create(lno=library, stono=storage, id=user)
                        reserve.save()
                        return HttpResponseRedirect(reverse('library:books'))
                    else:
                        return HttpResponseRedirect(reverse('library:books'))
                else:
                    error = form.errors
                    storage = get_object_or_404(models.Storages, stono=storage_stono)
                    context = {'form': form, 'error': error, 'storage': storage}
                    return render(request, 'reservebook.html', context)
            else:
                form = ReserveForm()
                storage = get_object_or_404(models.Storages, stono=storage_stono)
                context = {'form': form, 'storage_stono': storage_stono, 'storage': storage}
                return render(request, 'reservebook.html', context)

@login_required
def confirmreserve(request, reserve_reno):
    if request.user.is_staff:
        try:
            reserve = get_object_or_404(models.Reserves, reno=reserve_reno)
            storage = get_object_or_404(models.Storages, stono=reserve.stono.stono)
            user = get_object_or_404(models.AuthUser, id=request.user.id)
            storage.lno = reserve.lno
            storage.save()
            reserve.admin_id = request.user.id
            reserve.save()
            return HttpResponseRedirect(reverse('library:reserves'))
        except models.Reserves.DoesNotExist:
            return HttpResponseRedirect(reverse('library:reserves'))
    else:
        return HttpResponseRedirect(reverse('library:reserves'))
