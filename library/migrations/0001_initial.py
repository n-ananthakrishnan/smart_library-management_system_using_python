"""Initial migration for library app models."""
from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.models.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('role', models.CharField(choices=[('student', 'Student'), ('librarian', 'Librarian'), ('admin', 'Admin')], default='student', max_length=20)),
                ('roll_number', models.CharField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('isbn', models.CharField(max_length=20, unique=True)),
                ('barcode', models.CharField(db_index=True, max_length=100, unique=True)),
                ('genre', models.CharField(db_index=True, max_length=50)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('rack_no', models.CharField(max_length=20)),
                ('shelf_no', models.CharField(blank=True, max_length=20)),
                ('edition', models.CharField(blank=True, max_length=50)),
                ('publication_year', models.IntegerField(blank=True, null=True)),
                ('publisher', models.CharField(blank=True, max_length=200)),
                ('pages', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='book_covers/')),
                ('status', models.CharField(choices=[('available', 'Available'), ('borrowed', 'Borrowed'), ('reserved', 'Reserved'), ('lost', 'Lost'), ('maintenance', 'Maintenance')], default='available', max_length=20)),
                ('total_copies', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('available_copies', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)])),
                ('average_rating', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_location_verified', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('review_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('helpful_count', models.IntegerField(default=0)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='library.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='library.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'book')},
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_at', models.DateTimeField(auto_now_add=True)),
                ('expected_return_date', models.DateTimeField(blank=True, null=True)),
                ('is_fulfilled', models.BooleanField(default=False)),
                ('fulfilled_at', models.DateTimeField(blank=True, null=True)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='library.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='library.user')),
            ],
            options={
                'ordering': ['-reserved_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('overdue', 'Overdue'), ('available', 'Available'), ('reminder', 'Reminder'), ('borrow', 'Borrow'), ('reservation', 'Reservation'), ('info', 'Info')], default='info', max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='library.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Borrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_at', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('returned_at', models.DateTimeField(blank=True, null=True)),
                ('fine_paid', models.FloatField(default=0.0)),
                ('notes', models.TextField(blank=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to='library.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to='library.user')),
            ],
            options={
                'ordering': ['-borrowed_at'],
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('search', 'Search'), ('view_book', 'View Book'), ('borrow', 'Borrow'), ('return', 'Return'), ('reserve', 'Reserve'), ('add_book', 'Add Book'), ('edit_book', 'Edit Book'), ('delete_book', 'Delete Book'), ('scan_success', 'Scan Success'), ('scan_misplaced', 'Scan Misplaced')], max_length=50)),
                ('details', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip_address', models.CharField(blank=True, max_length=50)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='library.book')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='library.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='library_use_usernam_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='library_use_email_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['role'], name='library_use_role_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['title'], name='library_boo_title_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['isbn'], name='library_boo_isbn_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['barcode'], name='library_boo_barcode_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['status'], name='library_boo_status_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['book'], name='library_rev_book_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['user'], name='library_rev_user_idx'),
        ),
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['user', 'is_fulfilled'], name='library_res_user_fulfil_idx'),
        ),
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['book', 'is_fulfilled'], name='library_res_book_fulfil_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='library_not_user_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['expires_at'], name='library_not_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='borrowing',
            index=models.Index(fields=['user', 'returned_at'], name='library_bor_user_return_idx'),
        ),
        migrations.AddIndex(
            model_name='borrowing',
            index=models.Index(fields=['book', 'returned_at'], name='library_bor_book_return_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['user', 'timestamp'], name='library_act_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['action', 'timestamp'], name='library_act_action_timestamp_idx'),
        ),
    ]
