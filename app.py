#!/usr/bin/env python3
import models, forms, sys, codecs, re
from flask import Flask, flash, redirect, url_for, render_template, g, abort, request, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import check_password_hash
from flask_sslify import SSLify


app = Flask(__name__)
app.secret_key = 'gb5;w85uigb4hp89g 5ubg8959gb5g9p891234567gfvhytrdgfjdfgd5c56d566576tyvyfyftfyttytyftfÿ'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sign_in'

@login_manager.user_loader
def load_user(id):
    try:
        return models.User.get(models.User.id == id)
    except models.DoesNotExist:
        return None


@app.route('/', methods=('GET', 'POST'))
@app.route('/<int:page>', methods=('GET', 'POST'))
def index(page=1):
    if current_user.is_authenticated:
        if request.method == 'POST':
            if request.form['pposts'] == 'everyone':
                posts = models.Post.select().paginate(page, 20)
                g.user._get_current_object().default_view = 'everyone'
                g.user._get_current_object().save()
            elif request.form['pposts'] == 'following':
                posts = g.user._get_current_object().get_following().paginate(page, 20)
                g.user._get_current_object().default_view = 'following'
                g.user._get_current_object().save()
            elif request.form['pposts'] == 'followers':
                posts = g.user._get_current_object().get_followers().paginate(page, 20)
                g.user._get_current_object().default_view = 'followers'
                g.user._get_current_object().save()
        else:
            if g.user._get_current_object().default_view == 'following':
                posts = g.user._get_current_object().get_following().paginate(page, 20)
            elif g.user._get_current_object().default_view == 'followers':
                posts = g.user._get_current_object().get_followers().paginate(page, 20)
            else:
                posts = models.Post.select().paginate(page, 20)
    else:
        posts = None
    return render_template('index.html', posts=posts, options=True, page=page)


@app.route('/comment/<int:id>', methods=['POST'])
@login_required
def comment(id):
    try:
        post = models.Post.get(models.Post.id == id)
        data = request.form['comment']
    except models.DoesNotExist:
        abort(404)
    except:
        abort(400)
    else:
        if len(request.form['comment']) <= 140:
            models.Comment.create(user=g.user._get_current_object(), post=post, data=data)
            post.user.sendmail_to(name=g.user._get_current_object().username,
            subject="TDIC Comment",
            msg_text='{} commented on your post: "{}".'
            .format(g.user._get_current_object().username, data))
        else:
            flash('Comment too long (140 characters).')
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=form.password.data
        )
        flash('You signed up! Remember to login!')
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
@app.route('/signin/<action>', methods=['GET', 'POST'])
def sign_in(action=None):
    form = forms.SignInForm()
    other_text = action
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username ** form.name_email.data)
        except models.DoesNotExist:
            try:
                user = models.User.get(models.User.email ** form.name_email.data)
            except models.DoesNotExist:
                flash('Could not find a user with that username/email and password combination')
                return render_template('signin.html', form=form)
            else:
                user_exists = True
        else:
            user_exists = True
        if user_exists:
            if check_password_hash(user.password, form.password.data):
                if action:
                    try:
                        return redirect(url_for(action))
                    except:
                        flash('Could not find the action to verify')
                        return redirect(url_for('index')), 404
                login_user(user, remember=form.remember.data)
                flash('You have been logged in! Go ahead, explore!')
                return redirect(url_for('index'))
            else:
                flash('Could not find a user with that username/email and password combination')
    return render_template('signin.html', form=form, text=other_text)


@app.route('/signout')
@login_required
def sign_out():
    logout_user()
    flash('You have been signed out. Make sure to come back! Your friends will be waiting!')
    return redirect(url_for('index'))


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(), data=form.content.data)
        for rel in models.Relationship.select():
            if rel.to_user == g.user._get_current_object():
                rel.from_user.sendmail_to(name=g.user._get_current_object().username,
                subject="TDIC Post",
                msg_text='{} posted: "{}".'
                .format(g.user._get_current_object().username, form.content.data))

        flash('Posted!')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/user')
@app.route('/user/<username>')
@login_required
def user_view(username=None):
    try:
        if username:
            user = models.User.get(models.User.username ** username)
        else:
            user = models.User.get(models.User.username ** request.values['user'])
    except models.DoesNotExist:
        abort(406)
    except KeyError:
        abort(400)
    else:
        posts = models.Post.select().where(models.Post.user == user)
        return render_template('index.html', user=user, posts=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        user = models.User.get(models.User.username ** username)
    except models.DoesNotExist:
        abort(406)
    else:
        try:
            models.Relationship.get(models.Relationship.from_user == g.user._get_current_object(), models.Relationship.to_user == user)
        except models.DoesNotExist:
            models.Relationship.create(from_user=g.user._get_current_object(), to_user=user)
            flash('Followed {}!'.format(user.username))
            return redirect(url_for('user_view', username=user.username))
        else:
            flash('You already followed {}.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        user = models.User.get(models.User.username ** username)
    except models.DoesNotExist:
        abort(406)
    else:
        try:
            relation = models.Relationship.get(models.Relationship.from_user == g.user._get_current_object(), models.Relationship.to_user == user)
        except models.DoesNotExist:
            flash('You haven\'t followed {} yet.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))
        else:
            relation.delete_instance()
            flash('Unfollowed {}.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        user = g.user._get_current_object()
        if request.form['bio'] != '':
            if len(request.form['bio']) <= 255:
                user.bio = request.form['bio']
                user.save()
                flash('Bio is set!')
            else:
                flash('Bio is too long.')
        if request.files['avatar']:
            if 'image' in request.files['avatar'].content_type:
                file_u = request.files['avatar'].read()
                if sys.getsizeof(file_u) <= 3000000:
                    file_a = 'data:{};base64,{}'.format(request.files['avatar'].content_type, codecs.encode(file_u, 'base64').decode('utf-8'))
                    g.user._get_current_object().avatar = file_a
                    g.user._get_current_object().save()
                    flash('Avatar set!')
                else:
                    flash('Avatar is bigger than 3 mb.')
            else:
                flash('Avatar is not an image.')
    return render_template('settings.html')


@app.route('/delete_account')
@login_required
def delete_account():
    g.user._get_current_object().delete_instance()
    logout_user()
    flash('User deleted. We are sorry to see you go!')
    return redirect(url_for('index'))


@app.route('/view_post/<int:id>')
@login_required
def view_post(id):
    try:
        post = models.Post.get(models.Post.id == id)
    except models.DoesNotExist:
        abort(404)
    else:
        return render_template('index.html', posts=[post])



@app.errorhandler(404)
def e404(error):
    return render_template('layout.html', error_head='404',
                            error_message='You have landed in the wrong spot.',
                            error_link='/', error_link_m='Return to homepage'), 404

@app.errorhandler(406)
def e406(error):
    return render_template('layout.html', error_head='406',
                            error_message='Dude, that user does not exist.',
                            error_link='/', error_link_m='Back to safety'), 406


@app.errorhandler(500)
def e500(error):
    return render_template('layout.html', error_head='500',
                            error_message='Holy smokes! You just crashed the server!',
                            error_link='https://i.ytimg.com/vi/tntOCGkgt98/maxresdefault.jpg', error_link_m='Cat picture'), 500

@app.before_request
def before():
    g.user = current_user
    g.db = models.DB
    g.db.connect()
    try:
        g.db.create_tables([User, Post, Comment, Relationship], safe=True)
    except:
        pass

    url = re.sub("http://", "https://", request.url)
    if 'http://' in request.url:
        return redirect(url)

@app.after_request
def after(response):
    g.db.close()
    return response


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
    # app.run(debug=False, host='0.0.0.0', port=80)
