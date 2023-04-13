from flask import Blueprint, session, render_template, flash, redirect, url_for, request
from slugify import slugify
import uuid
import os
from PIL import Image

from application import db
from blog.models import Post, Category, Tag, Comment
from blog.forms import PostForm, CommentForm
from author.models import Author
from author.decorators import login_required
from settings import BLOG_POST_IMAGES_PATH

blog_app = Blueprint('blog_app', __name__)

POSTS_PER_PAGE = 5

@blog_app.route('/')
def index():
    page = int(request.values.get('page', '1'))
    #posts = Post.query.filter_by(live=True).order_by(Post.publish_date.desc())\
        #.paginate(page, POSTS_PER_PAGE, False)
    #as of Flask-SQLAlchemy 3.0, all arguments to paginate are keyword-only
    posts = Post.query.filter_by(live=True).order_by(Post.publish_date.desc())\
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/index.html',
        posts=posts
    )

@blog_app.route('/post', methods=('GET', 'POST'))
@login_required
def post():
    form = PostForm()
    tags_field = request.values.get('tags_field', '')

    if form.validate_on_submit():
        image_id = None

        if form.image.data:
            f = form.image.data
            image_id = str(uuid.uuid4())
            file_name = image_id + '.png'
            file_path = os.path.join(
                BLOG_POST_IMAGES_PATH, file_name
            )
            Image.open(f).save(file_path)

            _image_resize(BLOG_POST_IMAGES_PATH, image_id, 600, 'lg')
            _image_resize(BLOG_POST_IMAGES_PATH, image_id, 300, 'sm')

        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            category = new_category
        else:
            category = form.category.data

        author = Author.query.get(session['id'])
        title = form.title.data.strip()
        body = form.body.data.strip()
        post = Post(
            author=author,
            title=title,
            body=body,
            image=image_id,
            category=category,
        )

        _save_tags(post, tags_field)

        db.session.add(post)
        db.session.commit()

        slug = slugify(str(post.id) + '-' + post.title)
        post.slug = slug
        db.session.commit()

        flash('Article posted')
        return redirect(url_for('.article', slug=slug))

    return render_template('blog/post.html',
        form=form,
        action="new",
        tags_field=tags_field          
    )

@blog_app.route('/posts/<slug>')
def article(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('blog/article.html', post=post)

@blog_app.route('/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=post)
    tags_field = request.values.get('tags_field', _load_tags_field(post))

    if form.validate_on_submit():
        original_image = post.image
        original_title = post.title
        form.populate_obj(post)

        if form.image.data:
            f = form.image.data
            image_id = str(uuid.uuid4())
            file_name = image_id + '.png'
            file_path = os.path.join(
                BLOG_POST_IMAGES_PATH, file_name
            )
            Image.open(f).save(file_path)

            _image_resize(BLOG_POST_IMAGES_PATH, image_id, 600, 'lg')
            _image_resize(BLOG_POST_IMAGES_PATH, image_id, 300, 'sm')

            post.image = image_id
        else:
            post.image = original_image

        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            post.category = new_category

        if form.title.data != original_title:
            post.slug = slugify(str(post.id) + '-' + form.title.data)

        _save_tags(post, tags_field)
        
        db.session.commit()
        flash('Article edited')
        return redirect(url_for('.article', slug=post.slug))

    return render_template('blog/post.html',
        form=form,
        post=post,
        action="edit",
        tags_field=tags_field
    )

@blog_app.route('/delete/<slug>')
@login_required
def delete(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    post.live = False
    db.session.commit()
    flash("Article deleted")
    return redirect(url_for('.index'))

@blog_app.route('/categories/<category_id>')
def categories(category_id):
    category = Category.query.filter_by(id=category_id).first_or_404()
    page = int(request.values.get('page', '1'))
    #posts = Post.query.filter_by(category=category, live=True)\
        #.order_by(Post.publish_date.desc())\
        #.paginate(page, POSTS_PER_PAGE, False)
    #as of Flask-SQLAlchemy 3.0, all arguments to paginate are keyword-only
    posts = Post.query.filter_by(category=category, live=True)\
        .order_by(Post.publish_date.desc())\
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/category_posts.html',
        posts=posts,
        title=category,
        category_id=category_id
    )

@blog_app.route('/tags/<tag>')
def tags(tag):
    tag = Tag.query.filter_by(name=tag).first_or_404()
    page = int(request.values.get('page', '1'))
    #posts = tag.posts.filter_by(live=True)\
        #.order_by(Post.publish_date.desc())\
        #.paginate(page, POSTS_PER_PAGE, False)
     #as of Flask-SQLAlchemy 3.0, all arguments to paginate are keyword-only
    posts = tag.posts.filter_by(live=True)\
        .order_by(Post.publish_date.desc())\
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/tag_posts.html',
        posts=posts,
        title="Tag: " + str(tag),
        tag=str(tag)
    )    

def _image_resize(original_file_path,image_id, image_base, extension):
    file_path = os.path.join(
        original_file_path, image_id + '.png'
    )
    image = Image.open(file_path)
    wpercent = (image_base / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((image_base, hsize), Image.ANTIALIAS)
    modified_file_path = os.path.join(
        original_file_path, image_id + '.' + extension + '.png'
    )
    image.save(modified_file_path)
    #return

def _save_tags(post, tags_field):
    post.tags.clear()
    for tag_item in tags_field.split(','):
        tag = Tag.query.filter_by(name=slugify(tag_item)).first()
        if not tag:
            tag = Tag(name=slugify(tag_item))
            db.session.add(tag)
        post.tags.append(tag)
    return post

def _load_tags_field(post):
    tags_field = ''
    for tag in post.tags:
        tags_field += tag.name + ', '
    return tags_field[:-2]

@blog_app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post_id=post.id)
        page = int(request.values.get('page', '1'))
        posts = Post.query.filter_by(comment=comment, live=True)\
            .order_by(Post.publish_date.desc())\
            .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
        db.session.add(comment)
        db.session.commit()
        flash("Comment added")
    return render_template('blog/comment_post.html',
            posts=posts,
            comment_post=comment_post
        )

def save_comment(self):
        db.session.add(self)
        db.session.commit()

def get_comments(id):
    comments = Comment.query.filter_by(post_id = id).all()
    return comments
