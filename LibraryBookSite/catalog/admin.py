from django.contrib import admin

from .models import Author, Genre, Book, BookInstance
# Register your models here.


# admin.site.register(Book)
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # pass
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


# admin.site.register(Author)
class BookInline(admin.TabularInline):
    model = Book
    extra = 0
# Define the admin class
# @admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # pass
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

admin.site.register(Genre)

# admin.site.register(BookInstance)
# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # pass
    list_display = ('id', 'book', 'status', 'borrower', 'due_back')
    list_filter = ('status', 'due_back')

    fieldsets = (
        ('Details', {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
