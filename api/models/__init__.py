# Because our models are in a folder we need this import
# https://www.webforefront.com/django/modelsoutsidemodels.html
# "the __init__ file inside this new models folder does require additional attention. While __init__ files are typically left empty, in this case, the __init__ file must make a relative import for each of the models -- inside .py files -- to make them visible to the app."

from .user import User
