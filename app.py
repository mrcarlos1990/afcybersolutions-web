import os
import secrets
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from extensions import db, login_manager
from models import ContactMessage, GalleryImage, Project, Service, SiteSettings, Testimonial, User

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-this-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'afcyber.db'}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

    (BASE_DIR / "instance").mkdir(exist_ok=True)
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    register_filters(app)
    register_security(app)
    register_routes(app)

    with app.app_context():
        db.create_all()
        seed_database()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def register_filters(app):
    @app.template_filter("asset")
    def asset(path):
        if not path:
            return ""
        if path.startswith("http"):
            return path
        return url_for("static", filename=f"uploads/{path}")


def register_security(app):
    @app.before_request
    def csrf_protect():
        session.setdefault("_csrf_token", secrets.token_urlsafe(32))
        if request.method == "POST":
            token = session.get("_csrf_token")
            form_token = request.form.get("_csrf_token")
            if not token or not form_token or not secrets.compare_digest(token, form_token):
                abort(400)

    @app.context_processor
    def inject_csrf():
        session.setdefault("_csrf_token", secrets.token_urlsafe(32))
        return {"csrf_token": session["_csrf_token"]}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        flash("Solo se permiten imágenes jpg, jpeg, png o webp.", "danger")
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(file.filename.rsplit(".", 1)[0])[:60] or "image"
    filename = f"{safe_name}-{uuid4().hex[:10]}.{ext}"
    file.save(UPLOAD_FOLDER / filename)
    return filename


def seed_database():
    if not SiteSettings.query.first():
        db.session.add(SiteSettings())

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin12345")
    if not User.query.filter_by(username=admin_username).first():
        user = User(username=admin_username)
        user.set_password(admin_password)
        db.session.add(user)

    if Service.query.count() == 0:
        services = [
            ("Desarrollo de páginas web", "Diseño y desarrollo de sitios corporativos, landing pages y plataformas web rápidas, seguras y responsivas.", "monitor-smartphone"),
            ("Sistemas POS", "Soluciones de punto de venta para facturación, inventario, usuarios, reportes y control operativo.", "scan-barcode"),
            ("Sistemas CMMS", "Gestión digital de mantenimiento, activos, órdenes de trabajo, técnicos, historial y planificación preventiva.", "settings"),
            ("Soporte técnico", "Asistencia presencial y remota para equipos, software, redes, usuarios y continuidad operativa.", "headphones"),
            ("Ciberseguridad", "Evaluación, hardening, protección, monitoreo y buenas prácticas para reducir riesgos digitales.", "shield-check"),
            ("Cámaras de seguridad", "Instalación y configuración de CCTV, cámaras IP, acceso remoto, almacenamiento y monitoreo.", "cctv"),
            ("Redes empresariales", "Diseño, cableado, configuración y optimización de redes confiables para negocios.", "network"),
            ("Correos corporativos", "Implementación de correos profesionales, dominios, seguridad, firmas y configuración multiplataforma.", "mail-check"),
            ("Automatización de procesos", "Digitalización de tareas repetitivas, flujos internos, reportes y herramientas a medida.", "workflow"),
            ("Asesoría tecnológica", "Acompañamiento estratégico para elegir, implementar y mejorar soluciones tecnológicas.", "lightbulb"),
        ]
        for index, (title, description, icon) in enumerate(services, start=1):
            db.session.add(Service(title=title, description=description, icon=icon, position=index))

    if Project.query.count() == 0:
        db.session.add(Project(name="Implementación tecnológica empresarial", description="Proyecto integral de infraestructura, soporte y presencia web para una operación en crecimiento.", category="Infraestructura"))
        db.session.add(Project(name="Sistema de gestión operativa", description="Solución personalizada para controlar procesos, usuarios, reportes y seguimiento interno.", category="Software"))

    if Testimonial.query.count() == 0:
        db.session.add(Testimonial(client_name="Cliente corporativo", company="Empresa local", comment="AFCyber SOLUTIONS nos ayudó a ordenar nuestra tecnología con una atención clara, rápida y profesional."))

    db.session.commit()


def get_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    return settings


def checkbox_value(name):
    return request.form.get(name) == "on"


def register_routes(app):
    @app.context_processor
    def inject_settings():
        return {"settings": get_settings()}

    @app.route("/")
    def index():
        settings = get_settings()
        return render_template(
            "public/index.html",
            services=Service.query.filter_by(is_active=True).order_by(Service.position, Service.id).all(),
            projects=Project.query.filter_by(is_active=True).order_by(Project.created_at.desc()).all(),
            gallery=GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.created_at.desc()).all(),
            testimonials=Testimonial.query.filter_by(is_active=True).order_by(Testimonial.created_at.desc()).all(),
            settings=settings,
        )

    @app.post("/contact")
    def contact():
        required = ["name", "email", "subject", "message"]
        if any(not request.form.get(field, "").strip() for field in required):
            flash("Completa los campos requeridos del formulario.", "danger")
            return redirect(url_for("index") + "#contacto")
        msg = ContactMessage(
            name=request.form["name"].strip(),
            email=request.form["email"].strip(),
            phone=request.form.get("phone", "").strip(),
            subject=request.form["subject"].strip(),
            message=request.form["message"].strip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash("Mensaje enviado correctamente. Te contactaremos pronto.", "success")
        return redirect(url_for("index") + "#contacto")

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            user = User.query.filter_by(username=request.form.get("username", "").strip()).first()
            if user and user.check_password(request.form.get("password", "")):
                login_user(user)
                return redirect(url_for("admin_dashboard"))
            flash("Usuario o contraseña incorrectos.", "danger")
        return render_template("admin/login.html")

    @app.get("/admin/logout")
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for("admin_login"))

    @app.get("/admin")
    @login_required
    def admin_dashboard():
        return render_template(
            "admin/dashboard.html",
            totals={
                "services": Service.query.count(),
                "projects": Project.query.count(),
                "gallery": GalleryImage.query.count(),
                "testimonials": Testimonial.query.count(),
                "messages": ContactMessage.query.filter_by(is_read=False).count(),
            },
            messages=ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all(),
        )

    @app.route("/admin/settings", methods=["GET", "POST"])
    @login_required
    def admin_settings():
        settings = get_settings()
        if request.method == "POST":
            fields = [
                "company_name", "domain", "slogan", "hero_title", "hero_text", "about_text", "mission", "vision", "values",
                "primary_color", "secondary_color", "button_color", "background_color", "text_color", "font_family",
                "whatsapp", "phone", "main_email", "corporate_email", "address", "business_hours",
                "facebook", "instagram", "tiktok", "youtube", "linkedin", "maps_embed",
            ]
            for field in fields:
                setattr(settings, field, request.form.get(field, "").strip())
            for field in ["logo", "favicon", "hero_image", "about_image"]:
                uploaded = save_upload(request.files.get(field))
                if uploaded:
                    setattr(settings, field, uploaded)
            settings.dark_mode = checkbox_value("dark_mode")
            for section in ["show_about", "show_services", "show_projects", "show_gallery", "show_testimonials", "show_contact"]:
                setattr(settings, section, checkbox_value(section))
            db.session.commit()
            flash("Configuración actualizada.", "success")
            return redirect(url_for("admin_settings"))
        return render_template("admin/settings.html", settings=settings)

    @app.post("/admin/settings/reset-colors")
    @login_required
    def reset_colors():
        settings = get_settings()
        settings.primary_color = "#0B5FFF"
        settings.secondary_color = "#00C2A8"
        settings.button_color = "#0B5FFF"
        settings.background_color = "#F6F9FC"
        settings.text_color = "#102033"
        settings.dark_mode = False
        db.session.commit()
        flash("Colores restaurados.", "success")
        return redirect(url_for("admin_settings"))

    register_crud_routes(app)


def register_crud_routes(app):
    @app.route("/admin/services", methods=["GET", "POST"])
    @login_required
    def admin_services():
        if request.method == "POST":
            service = Service(
                title=request.form["title"].strip(),
                description=request.form["description"].strip(),
                icon=request.form.get("icon", "shield-check").strip(),
                position=int(request.form.get("position") or 0),
                is_active=checkbox_value("is_active"),
                image=save_upload(request.files.get("image")),
            )
            db.session.add(service)
            db.session.commit()
            flash("Servicio agregado.", "success")
            return redirect(url_for("admin_services"))
        return render_template("admin/services.html", services=Service.query.order_by(Service.position, Service.id).all())

    @app.route("/admin/services/<int:item_id>", methods=["POST"])
    @login_required
    def update_service(item_id):
        item = Service.query.get_or_404(item_id)
        item.title = request.form["title"].strip()
        item.description = request.form["description"].strip()
        item.icon = request.form.get("icon", "shield-check").strip()
        item.position = int(request.form.get("position") or 0)
        item.is_active = checkbox_value("is_active")
        uploaded = save_upload(request.files.get("image"))
        if uploaded:
            item.image = uploaded
        db.session.commit()
        flash("Servicio actualizado.", "success")
        return redirect(url_for("admin_services"))

    @app.post("/admin/services/<int:item_id>/delete")
    @login_required
    def delete_service(item_id):
        db.session.delete(Service.query.get_or_404(item_id))
        db.session.commit()
        flash("Servicio eliminado.", "success")
        return redirect(url_for("admin_services"))

    @app.route("/admin/projects", methods=["GET", "POST"])
    @login_required
    def admin_projects():
        if request.method == "POST":
            db.session.add(Project(name=request.form["name"].strip(), description=request.form["description"].strip(), category=request.form.get("category", "").strip(), link=request.form.get("link", "").strip(), is_active=checkbox_value("is_active"), image=save_upload(request.files.get("image"))))
            db.session.commit()
            flash("Proyecto agregado.", "success")
            return redirect(url_for("admin_projects"))
        return render_template("admin/projects.html", projects=Project.query.order_by(Project.created_at.desc()).all())

    @app.route("/admin/projects/<int:item_id>", methods=["POST"])
    @login_required
    def update_project(item_id):
        item = Project.query.get_or_404(item_id)
        item.name = request.form["name"].strip()
        item.description = request.form["description"].strip()
        item.category = request.form.get("category", "").strip()
        item.link = request.form.get("link", "").strip()
        item.is_active = checkbox_value("is_active")
        uploaded = save_upload(request.files.get("image"))
        if uploaded:
            item.image = uploaded
        db.session.commit()
        flash("Proyecto actualizado.", "success")
        return redirect(url_for("admin_projects"))

    @app.post("/admin/projects/<int:item_id>/delete")
    @login_required
    def delete_project(item_id):
        db.session.delete(Project.query.get_or_404(item_id))
        db.session.commit()
        flash("Proyecto eliminado.", "success")
        return redirect(url_for("admin_projects"))

    @app.route("/admin/gallery", methods=["GET", "POST"])
    @login_required
    def admin_gallery():
        if request.method == "POST":
            image = save_upload(request.files.get("image"))
            if image:
                db.session.add(GalleryImage(title=request.form["title"].strip(), category=request.form.get("category", "").strip(), image=image, is_active=checkbox_value("is_active")))
                db.session.commit()
                flash("Imagen agregada.", "success")
            return redirect(url_for("admin_gallery"))
        return render_template("admin/gallery.html", gallery=GalleryImage.query.order_by(GalleryImage.created_at.desc()).all())

    @app.post("/admin/gallery/<int:item_id>/delete")
    @login_required
    def delete_gallery(item_id):
        db.session.delete(GalleryImage.query.get_or_404(item_id))
        db.session.commit()
        flash("Imagen eliminada.", "success")
        return redirect(url_for("admin_gallery"))

    @app.route("/admin/testimonials", methods=["GET", "POST"])
    @login_required
    def admin_testimonials():
        if request.method == "POST":
            db.session.add(Testimonial(client_name=request.form["client_name"].strip(), company=request.form.get("company", "").strip(), comment=request.form["comment"].strip(), photo=save_upload(request.files.get("photo")), is_active=checkbox_value("is_active")))
            db.session.commit()
            flash("Testimonio agregado.", "success")
            return redirect(url_for("admin_testimonials"))
        return render_template("admin/testimonials.html", testimonials=Testimonial.query.order_by(Testimonial.created_at.desc()).all())

    @app.route("/admin/testimonials/<int:item_id>", methods=["POST"])
    @login_required
    def update_testimonial(item_id):
        item = Testimonial.query.get_or_404(item_id)
        item.client_name = request.form["client_name"].strip()
        item.company = request.form.get("company", "").strip()
        item.comment = request.form["comment"].strip()
        item.is_active = checkbox_value("is_active")
        uploaded = save_upload(request.files.get("photo"))
        if uploaded:
            item.photo = uploaded
        db.session.commit()
        flash("Testimonio actualizado.", "success")
        return redirect(url_for("admin_testimonials"))

    @app.post("/admin/testimonials/<int:item_id>/delete")
    @login_required
    def delete_testimonial(item_id):
        db.session.delete(Testimonial.query.get_or_404(item_id))
        db.session.commit()
        flash("Testimonio eliminado.", "success")
        return redirect(url_for("admin_testimonials"))

    @app.get("/admin/messages")
    @login_required
    def admin_messages():
        return render_template("admin/messages.html", messages=ContactMessage.query.order_by(ContactMessage.created_at.desc()).all())

    @app.post("/admin/messages/<int:item_id>/read")
    @login_required
    def mark_message_read(item_id):
        item = ContactMessage.query.get_or_404(item_id)
        item.is_read = True
        db.session.commit()
        return redirect(url_for("admin_messages"))

    @app.post("/admin/messages/<int:item_id>/delete")
    @login_required
    def delete_message(item_id):
        db.session.delete(ContactMessage.query.get_or_404(item_id))
        db.session.commit()
        flash("Mensaje eliminado.", "success")
        return redirect(url_for("admin_messages"))


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
