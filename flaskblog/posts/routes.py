from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)    # argument 'users' is the name of this blueprint


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user) # used backref of author to refer to user.id
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title = 'New Post', form = form, legend = 'New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:     # a post should be updated only by it's author
        abort(403)      # show "Forbidden" error
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()     # no need for .add() because both post.title and post.content are already in the database
        flash('Your post has been successfully updated!', 'success')
        return redirect(url_for('posts.post', post_id = post.id))
    elif request.method == 'GET':       # to populate the current user's data in the form by default on GET
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title = 'Update Post', form = form, legend = 'Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:     # a post should be deleted only by it's author
        abort(403)      # show "Forbidden" error
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been successfully deleted!', 'success')
    return redirect(url_for('main.home'))
