from comunidadeimpressionadora import app, bcript
from comunidadeimpressionadora.forms import FormCriarConta, FormFazerLogin, FormEditarPerfil, CriarPost
from comunidadeimpressionadora.models import Usuario, database, Post
from flask import request, render_template, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
import os
import secrets
from PIL import Image


@app.route("/")
def home_page():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route("/contato")
def contact_page():
    return render_template('contato.html')

@app.route("/lista-usuarios")
@login_required
def users_page():
    usuarios = Usuario()
    return render_template('usuarios.html', list_users=list_users,usuarios=usuarios)

@app.route('/login', methods=['GET','POST'])
def login_criarconta():
    fazer_login = FormFazerLogin()
    criar_conta = FormCriarConta()

    if fazer_login.validate_on_submit() and 'botao_submit' in request.form:
        usuario = Usuario.query.filter_by(email=fazer_login.email.data).first()
        if usuario and bcript.check_password_hash(usuario.senha, fazer_login.senha.data):
            login_user(usuario, remember=fazer_login.lembrar_dados.data)
            flash(f'login feito com sucesso no e-mail: {fazer_login.email.data}.', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home_page'))
        else:
            flash(f'Dados incorretos.', 'alert-danger')

    if criar_conta.validate_on_submit() and  'botao_submit_criarconta' in request.form:
        senha_cript = bcript.generate_password_hash(criar_conta.senha.data).decode("utf-8")
        usuario = Usuario(username=criar_conta.username.data, email=criar_conta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso no e-mail: {criar_conta.email.data}.', 'alert-success')

        return redirect(url_for('home_page'))
    return render_template('login.html', fazer_login=fazer_login, criar_conta=criar_conta)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route('/posts/criar', methods=['GET','POST'])
@login_required
def criar_post():
    form = CriarPost()
    post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
    if form.validate_on_submit():
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso!', 'alert-success')
        return redirect(url_for('home_page'))
    return render_template('criar_post.html', form=form)

def salvar_image(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ";".join(lista_cursos)

@app.route('/perfil/editar', methods=['GET','POST'] )
@login_required
def editar_perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    form = FormEditarPerfil()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.foto_perfil.data:
            nome_image = salvar_image(form.foto_perfil.data)
            current_user.foto_perfil = nome_image
        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash(f'Perfil editado.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('editar-perfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = CriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post editado com sucesso!', 'alert-success')
            return redirect(url_for('home_page'))
    else:
        form = None

    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def exluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluitdo com sucesso.', 'alert-danger')
        return redirect(url_for('home_page'))
    else:
        abort(403)
