[![General Assembly Logo](https://camo.githubusercontent.com/1a91b05b8f4d44b5bbfb83abac2b0996d8e26c92/687474703a2f2f692e696d6775722e636f6d2f6b6538555354712e706e67)](https://generalassemb.ly/education/web-development-immersive)

# Django Auth

So far we have looked at making Django APIs that do not include any user
ownership or even a way for a user to sign in! Time to change that.

This repository contains a basic API for `mangos` and `users`, but no resource
ownership included.

## Prerequisites

- [django-relationships](https://git.generalassemb.ly/ga-wdi-boston/django-relationships)

## Objectives

By the end of this, developers should be able to:

- Explain how Django handles authentication
- Manage view permissions
- Manage resource "ownership"

## Preparation

1. Fork and clone this repository **into the `django-env` folder**.
 [FAQ](https://git.generalassemb.ly/ga-wdi-boston/meta/wiki/ForkAndClone)
1. Create and checkout to a new branch, `training`, for your work.
1. Run `pipenv shell` to start up your virtual environment **in the `django-env` folder**.
1. Run `pipenv install django-rest-auth django-cors-headers python-dotenv dj-database-url` **in the `django-env` folder**.
3. Create a psql database for the project
    1. Type `psql` to get into interactive shell
    2. Run `CREATE DATABASE "django_mangos_auth";`
    3. Exit shell
    OR:
    1. Run `createdb "django_mangos_auth"`
4. Do not run your migrations yet.
1. Open the repository in VS Code with `code .`

## The Template

This project is based on the [`django-auth-template`](https://git.generalassemb.ly/ga-wdi-boston/django-auth-template), with a little code
removed for our purposes.

### Code Along: Creating the `.env` File

Create a file named `.env` in the root of this repository.

Inside, we will define environment variables the template needs. For now, copy
the following example into the `.env` file and save.

```sh
ENV=development
DB_NAME_DEV="django_mangos_auth"
SECRET=cp8pxf+@r5obja0pvaare6e@grv1bzn+xytlo+2uwy
```

Once you have these environment variables set up, run the migrations with 
`python manage.py migrate`.

## Defining Authentication and Permissions Classes

We can set up what kind of authentication we want to use by either declaring
global defaults for our project or by attaching individual authentication
classes to individual views. These authentication classes are provided by
Django and give us different abilities.

The `settings.py` file of the project can be used to define defaults to our
project, including defaults pertaining to the Django Rest Framework. Below,
the `REST_FRAMEWORK` variable is assigned a dictionary with some defaults for
authenticatiton and permissions. This code is telling the project to
use `TokenAuthentication` and to require authentication (a valid token) for all
requests by default.

```py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}
```

If some views have unique permissions or authentication, the
`authentication_classes` and `permission_classes` class variables can be
overriden on class-based views.

```py
class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated,]
```

There are a lot of these classes and can all be found in the
[DRF authentication documentation](https://www.django-rest-framework.org/api-guide/authentication/).

Setting up our authentication and permissions either globally or on individual
viewsets will set up those routes to either allow or prevent access without
proper authentication. This will also give us some extra information on our
`request` object inside our routes. In our case with `TokenAuthentication`, we
will be given a `request.user` and `request.auth`. These objects will be what
allow us to implement user ownership.

### TokenAuthentication

Remember how we used tokens in our JavaScript clients and Express APIs? Token
authentication works by having the client request a token on something like a
user login. The client stores the token, then sends it in requests so the API
knows who is making that request. Then, the API can use the token to check if
the user has the correct permissions to do what they're doing.

By using the [`TokenAuthentication` class](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) from the Django
Rest Framework, we will be able to authenticate users based on the token they
send in their requests. Then, we will be able to set permission classes on our
views, such as `IsAuthenticated` to ensure we get a proper token in the
request. If we do, we will have access to a `user` object and `auth` token on
the `request` object.

## The Built-In User

You might remember when we used our admin CMS that Django provides for us, we
created a "super" user and used that to log in to that view.

That "super" user wasn't really that "super" - it was actually just a regular
user given access to that admin side of our application! Django provides a
built-in `User` model that you can use to get going with your project.

- [Use the Django Authentication System](https://docs.djangoproject.com/en/3.1/topics/auth/default/)

### Custom Users

While Django's built-in user is super awesome, it is **highly recommended** by
both the Django community and the [Django documentation itself](https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project) to build a custom user, even if the built-in
user suits your needs.

The `django-auth-template` will come with a provided custom user, exended to
use an email in place of a username.

## User Ownership

In order to implement "user ownership" we will really be using a combination
of a one-to-many relationship and some Python logic to manage that relationship.

### Code-Along: The Mango Model

To complete user ownership, we will have to set up a relationship between our
`Mango`s and our `User`s.

1. Add a `ForeignKey` to the `Mango` model
3. Run migrations

### Code-Along: `Create`

Let's update the `post` method in the `Mangos` view.

We will use the token the user sends us to know who the "owner" is, and thanks
to the `TokenAuthentication` class we will have access to the user on the
request object as the key `user`.

1. Set the `owner` on the incoming request data to the `request.user.id`
2. Add reference to the `'owner'` field in the `MangoSerializer`

### Code-Along: `Show`

For the `show` method, we need to make sure the user owns the mango they want
to see. To do this, we can compare the `owner` of the mango against the
`request.user.id` value. If they don't have permission, we can throw a
permissions error.

### Lab: `Index`, `Update`, and `Delete`

**Index**

The index method is the `get` method in the `Mangos` class. This method should
[`filter`](https://docs.djangoproject.com/en/3.2/topics/db/queries/#retrieving-specific-objects-with-filters) out only the mangos that the signed-in user owns and return that list.

**Update**

The update method is the `partial_update` method in the `MangosDetail` class.
This method should locate the mango and check that the user owns it. Then, override
the `owner` of the request data so that it is set to the `request.user.id`. 
Finally, [use the serializer to perform an update](https://www.django-rest-framework.org/api-guide/serializers/#saving-instances) on the mango object, save it, 
and return it to the client.

**Delete**

The `delete` method lives in the `MangosDetail` class. Ensure the user owns the
mango they are trying to delete, then [`delete()`](https://docs.djangoproject.com/en/3.2/topics/db/queries/#topics-db-queries-delete) it.

## Bonus: The Custom User

The `django-auth-template` will include a custom user.

### Custom User Model

There is a file in the `models` folder for our user model called `user.py`.
Here, the user model inherits from the `AbstractBaseUser` and will use an
email field in place of the username. The string version of our users will
return their email.

#### Custom User Model Manager

In addition to a model, we will need to override the class of the `UserManager`
for that model. This is recommended by Django in the case that we change any of
the fields on our model.

This "manager" of our User model contains two important methods for
creating users and superusers.

#### Custom User Model Registration

Finally, to tell our project about this new `User` model the `AUTH_USER_MODEL`
needs to be overridden in `settings.py`.

### Custom `User` Admin Forms

If you look at the `admin.py` file in this repo, you'll see some extra code
that we don't normally need for our custom resources. This code is specifically
modifying the already baked-in forms for the admin content management system.
These forms assume the user has certain data. When we change that data, we also
need to change the forms.

### User Routes

Let's take a look at the user routes included with the `django-auth-template`:
signing up, signing in, changing password, and signing out.

#### Sign Up

For sign up we need to create a user and save it to the database. We also want
to require a `password_confirmation` field in addition to an  `email` and
`password`. The `SignUp` view class inherits from `generics.CreateAPIView` and
will only support a `post` method.

This view class uses two serializers: `UserRegisterSerializer` and `UserSerializer`.

The `UserSerializer` inherits from the `ModelSerializer` class, so it can be
used for creating and updating as well as validating data. It is used to create
the user after we use the `UserRegisterSerializer` to validate that the incoming
`password` and `password_confirmation` exist and match.

Once the incoming data has been validated (`UserRegisterSerializer`) and the
user has been created (`UserSerializer`), the user is saved and a response
is sent back to the client.

#### Sign In

Signing in requires us to start working with tokens. This class view also
inherits from `generics.CreateAPIView` and supports a POST request.

For any routes that create data, Django requires the definition of a
`serializer_class` on the class view. The sign in route uses the
`UserSerializer` class for this.

The `django.contrib.auth` library that is included with Django gives us two
important functions for sign in: `authenticate` and `login`. The `authenticate`
method will take our request as well as the user's email and password
combination. Then, as long as our user exists and is active, we will use
`login` to log them in!

- [`login()`](https://docs.djangoproject.com/en/3.1/topics/auth/default/#how-to-log-a-user-in)
- [`authenticate()`](https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.authenticate)

The response should include a token, so the `User` model includes some methods
to handle tokens. For signing in, the `get_auth_token` method clears out the
previous token and creates a new one, saving it on the user.

#### SignOut

The `SignOut` class view inherits from `generics.DestroyAPIView`, and will only
support DELETE requests.

This method calls the `delete_token` method on the user, which will delete the
token on that user instance in the database.

We then use the [`logout`](https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.logout) method to clear out any session data.

#### Change Password

The `ChangePassword` class is going to inherit from `generics.UpdateAPIView`
and use the `partial_update` method to allow for a partial user update. The
`ChangePasswordSerializer` validates the incoming request data to require a
`new` and `old` password.

The [`check_password`](https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.User.check_password) method on the
user object is used to compare the `old` password provided with the actual
password stored on the user. Then, the [`set_password`](https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.User.set_password)
method can be used to update the password itself. Finally, the updated user is saved with the new password.

## Additional Resources

- [Django Rest Framework Tutorial: Authentication](https://www.django-rest-framework.org/api-guide/authentication)
- [What are ** and * in Python](https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters)

## [License](LICENSE)

1. All content is licensed under a CC­BY­NC­SA 4.0 license.
1. All software code is licensed under GNU GPLv3. For commercial use or
    alternative licensing, please contact legal@ga.co.
