from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(160), default="AFCyber SOLUTIONS")
    domain = db.Column(db.String(160), default="afcybersolutions.com.do")
    slogan = db.Column(db.String(255), default="Soluciones tecnológicas seguras, modernas y profesionales para empresas y emprendedores")
    hero_title = db.Column(db.String(255), default="Tecnología segura para empresas que crecen")
    hero_text = db.Column(db.Text, default="Soluciones tecnológicas seguras, modernas y profesionales para empresas y emprendedores")
    about_text = db.Column(db.Text, default="AFCyber SOLUTIONS nace para ayudar a empresas y emprendedores a operar con tecnología confiable, segura y bien diseñada. Integramos ciberseguridad, desarrollo de software, infraestructura, soporte y automatización con una visión práctica: resolver problemas reales y acompañar el crecimiento digital de nuestros clientes.")
    mission = db.Column(db.Text, default="Ofrecer soluciones tecnológicas profesionales, seguras y medibles que impulsen la productividad, continuidad y presencia digital de nuestros clientes.")
    vision = db.Column(db.Text, default="Ser una empresa tecnológica referente en República Dominicana por la calidad, seguridad y cercanía de nuestras soluciones.")
    values = db.Column(db.Text, default="Seguridad, innovación, responsabilidad, transparencia, servicio, mejora continua.")
    logo = db.Column(db.String(255))
    favicon = db.Column(db.String(255))
    hero_image = db.Column(db.String(255))
    about_image = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default="#0B5FFF")
    secondary_color = db.Column(db.String(20), default="#00C2A8")
    button_color = db.Column(db.String(20), default="#0B5FFF")
    background_color = db.Column(db.String(20), default="#F6F9FC")
    text_color = db.Column(db.String(20), default="#102033")
    font_family = db.Column(db.String(120), default="Inter")
    dark_mode = db.Column(db.Boolean, default=False)
    whatsapp = db.Column(db.String(40), default="18090000000")
    phone = db.Column(db.String(40), default="+1 (809) 000-0000")
    main_email = db.Column(db.String(160), default="info@afcybersolutions.com.do")
    corporate_email = db.Column(db.String(160), default="soporte@afcybersolutions.com.do")
    address = db.Column(db.String(255), default="República Dominicana")
    business_hours = db.Column(db.String(160), default="Lunes a viernes, 8:00 AM - 6:00 PM")
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    tiktok = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    maps_embed = db.Column(db.Text)
    show_about = db.Column(db.Boolean, default=True)
    show_services = db.Column(db.Boolean, default=True)
    show_projects = db.Column(db.Boolean, default=True)
    show_gallery = db.Column(db.Boolean, default=True)
    show_testimonials = db.Column(db.Boolean, default=True)
    show_contact = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(80), default="shield-check")
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    link = db.Column(db.String(255))
    category = db.Column(db.String(120), default="Tecnología")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(120), default="Trabajo")
    image = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(160), nullable=False)
    company = db.Column(db.String(160))
    comment = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(60))
    subject = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
