from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

# there's also a method called .errorhandler() and that will be active for only this blueprint but we want to use these handlers
# throughout our app hence we use .app_errorhandler()
@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404  # in flask we return a second value which is the status code which has a default value of 200


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403  # in flask we return a second value which is the status code which has a default value of 200


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500  # in flask we return a second value which is the status code which has a default value of 200