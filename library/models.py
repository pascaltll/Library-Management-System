from django.db import models


class BaseModel(models.Model):
    class Meta:
        managed = False


class Admins(BaseModel):
    id = models.ForeignKey('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    salary = models.FloatField()
    age = models.IntegerField()
    db_table = 'admins'


class AuthGroup(BaseModel):
    name = models.CharField(unique=True, max_length=80)
    db_table = 'auth_group'


class AuthGroupPermissions(BaseModel):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)
    db_table = 'auth_group_permissions'
    unique_together = (('group', 'permission'),)


class AuthPermission(BaseModel):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    db_table = 'auth_permission'
    unique_together = (('content_type', 'codename'),)


class AuthUser(BaseModel):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    db_table = 'auth_user'


class AuthUserGroups(BaseModel):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    db_table = 'auth_user_groups'
    unique_together = (('user', 'group'),)


class AuthUserUserPermissions(BaseModel):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)
    db_table = 'auth_user_user_permissions'
    unique_together = (('user', 'permission'),)


class Books(BaseModel):
    isbn = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=50)
    authors = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    price = models.FloatField()
    db_table = 'books'
class CmdbUserinfo(models.Model):
    email = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    pos = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'cmdb_userinfo'


class Comments(models.Model):
    comno = models.AutoField(primary_key=True)
    isbn = models.ForeignKey(Books, models.DO_NOTHING, db_column='isbn')
    text = models.CharField(max_length=140)
    id = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id')

    class Meta:
        managed = False
        db_table = 'comments'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Employee(models.Model):
    empno = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    office = models.CharField(max_length=50)
    age = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'employee'


class Libraries(models.Model):
    lname = models.CharField(unique=True, max_length=50)
    laddr = models.CharField(max_length=50)
    lno = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'libraries'


class Loans(models.Model):
    loan_date = models.DateField()
    due_date = models.DateField()
    renewed = models.IntegerField()
    stono = models.ForeignKey('Storages', models.DO_NOTHING, db_column='stono')
    id = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='id')
    return_date = models.DateField(blank=True, null=True)
    admin_id = models.IntegerField(blank=True, null=True)
    loanno = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'loans'


class Login(models.Model):
    email = models.CharField(primary_key=True, max_length=50)
    pwd = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'login'


class Reserves(models.Model):
    lno = models.ForeignKey('Libraries', models.DO_NOTHING, db_column='lno')
    stono = models.ForeignKey('Storages', models.DO_NOTHING, db_column='stono')
    id = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='id')
    reno = models.AutoField(primary_key=True)
    admin_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reserves'


class Storages(models.Model):
    stono = models.AutoField(primary_key=True)
    isbn = models.ForeignKey('Books', models.DO_NOTHING, db_column='isbn')
    lno = models.ForeignKey('Libraries', models.DO_NOTHING, db_column='lno')

    class Meta:
        managed = False
        db_table = 'storages'


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    uname = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    join_date = models.DateField()
    is_admin = models.IntegerField()

class Meta:
        managed = False
        db_table = 'users'
