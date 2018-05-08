from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
# da
# from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm
from django.contrib.auth.decorators import permission_required

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
# from .models import Author
# Create your views here.

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    num_genres = Genre.objects.count()
    books_containing_word = Book.objects.filter(title__icontains='the').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_genres': num_genres, 'books_containing_word': books_containing_word,
                 'num_visits': num_visits},  # num_visits appended
        )


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author

# def AuthorDetailView(request):
#     books_by_author = Book.objects.filter(author__book=pk)
#     # Render the HTML template index.html with the data in the context variable
#     return render(
#         request,
#         'book_detail.html',
#         context=books_by_author,
#     )



class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedLibraryBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing library books on loan.
    """
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        # return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    success_url = reverse_lazy('authors')


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    success_url = reverse_lazy('authors')


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    success_url = reverse_lazy('books')
