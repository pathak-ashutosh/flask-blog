from flask import render_template, request, Blueprint
from flaskblog.models import Post


main = Blueprint('main', __name__)    # argument 'users' is the name of this blueprint

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type = int)  # get an integer argument from address bar as the page no. which defaults to 1
    posts = Post.query\
            .order_by(Post.date_posted.desc())\
            .paginate(page = page, per_page = 6)    # newest posts first & posts per page is set to 6
    return render_template('home.html', posts = posts)

@main.route("/about")
def about():
    return render_template('about.html', title = 'About')
