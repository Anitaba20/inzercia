from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt
import re
import os

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

db = SQLAlchemy(app)
mail = Mail(app)


google_blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="google_prihlasenie"
)

app.register_blueprint(google_blueprint, url_prefix="/login")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Inzerat(db.Model):
    __tablename__ = "inzeraty"

    id = db.Column(db.Integer, primary_key=True)
    nazov = db.Column(db.String(200), nullable=False)
    kategoria = db.Column(db.String(100), nullable=False)
    cena = db.Column(db.String(100))
    lokalita = db.Column(db.String(100), nullable=False)
    popis = db.Column(db.Text, nullable=False)
    datum_pridania = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )


with app.app_context():
    db.create_all()


def vytvor_reset_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token


def over_reset_token(token):
    try:
        data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return data["user_id"]

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def posli_reset_email(email, reset_link):
    sprava = Message(
        subject="Reset hesla - služby.sk",
        recipients=[email]
    )

    sprava.body = f"""
Dobrý deň,

požiadali ste o reset hesla na stránke služby.sk.

Kliknite na tento odkaz:
{reset_link}

Odkaz je platný 30 minút.

Ak ste o reset hesla nežiadali, tento e-mail ignorujte.

služby.sk
"""

    mail.send(sprava)


@app.route("/")
def index():
    return render_template("stranky/index.html")


@app.route("/remeselne-a-stavebne-prace")
def remeselne_stavebne_prace():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Remeselné a stavebné práce"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/remeselne_stavebne_prace.html",
        inzeraty=inzeraty
    )


@app.route("/stahovanie-a-doprava")
def stahovanie_doprava():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Sťahovanie a doprava"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/stahovanie_doprava.html",
        inzeraty=inzeraty
    )


@app.route("/pomoc-v-domacnosti")
def pomoc_v_domacnosti():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Pomoc v domácnosti"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/pomoc_v_domacnosti.html",
        inzeraty=inzeraty
    )


@app.route("/krasa-a-starostlivost")
def krasa_starostlivost():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Krása a starostlivosť"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/krasa_starostlivost.html",
        inzeraty=inzeraty
    )


@app.route("/doucovanie-a-vzdelavanie")
def doucovanie_vzdelavanie():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Doučovanie a vzdelávanie"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/doucovanie_vzdelavanie.html",
        inzeraty=inzeraty
    )


@app.route("/preklady")
def preklady():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Preklady"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/preklady.html",
        inzeraty=inzeraty
    )


@app.route("/it-a-online-sluzby")
def it_online_sluzby():
    inzeraty = Inzerat.query.filter_by(
        kategoria="IT a online služby"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/it_online_sluzby.html",
        inzeraty=inzeraty
    )


@app.route("/foto-video-a-podujatia")
def foto_video_podujatia():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Foto, video a podujatia"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/foto_video_podujatia.html",
        inzeraty=inzeraty
    )


@app.route("/oslavy-a-catering")
def oslavy_catering():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Oslavy a catering"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/oslavy_catering.html",
        inzeraty=inzeraty
    )


@app.route("/ostatne")
def ostatne():
    inzeraty = Inzerat.query.filter_by(
        kategoria="Ostatné"
    ).order_by(
        Inzerat.datum_pridania.desc()
    ).all()

    return render_template(
        "kategorie/ostatne.html",
        inzeraty=inzeraty
    )


@app.route("/detail-inzeratu/<int:inzerat_id>")
def detail_inzeratu(inzerat_id):
    inzerat = Inzerat.query.get_or_404(inzerat_id)

    poskytovatel = User.query.get(inzerat.user_id)

    pocet_inzeratov = Inzerat.query.filter_by(
        user_id=inzerat.user_id
    ).count()

    dalsie_inzeraty = Inzerat.query.filter(
        Inzerat.user_id == inzerat.user_id,
        Inzerat.id != inzerat.id
    ).limit(3).all()

    return render_template(
        "inzeraty/detail_inzeratu.html",
        inzerat=inzerat,
        poskytovatel=poskytovatel,
        pocet_inzeratov=pocet_inzeratov,
        dalsie_inzeraty=dalsie_inzeraty
    )


@app.route("/kontaktovat-poskytovatela/<int:inzerat_id>", methods=["GET", "POST"])
def kontaktovat_poskytovatela(inzerat_id):
    chyba = ""
    uspech = ""

    inzerat = Inzerat.query.get_or_404(inzerat_id)
    poskytovatel = User.query.get(inzerat.user_id)

    if request.method == "POST":
        meno = request.form.get("meno", "").strip()
        email = request.form.get("email", "").strip().lower()
        text = request.form.get("sprava", "").strip()

        if not meno or not email or not text:
            chyba = "Vyplňte všetky povinné polia."

        elif not poskytovatel:
            chyba = "Poskytovateľ neexistuje."

        else:
            sprava = Message(
                subject=f"Nová správa k inzerátu: {inzerat.nazov}",
                recipients=[poskytovatel.email],
                reply_to=email
            )

            sprava.body = f"""
Dobrý deň,

niekto vás kontaktoval cez stránku služby.sk.

Inzerát:
{inzerat.nazov}

Meno záujemcu:
{meno}

E-mail záujemcu:
{email}

Správa:
{text}

Na túto správu môžete odpovedať priamo na e-mail záujemcu:
{email}

služby.sk
"""

            mail.send(sprava)

            uspech = "Správa bola úspešne odoslaná poskytovateľovi."

    return render_template(
        "inzeraty/kontaktovat_poskytovatela.html",
        chyba=chyba,
        uspech=uspech,
        inzerat=inzerat,
        poskytovatel=poskytovatel
    )


@app.route("/pridat-inzerat", methods=["GET", "POST"])
def pridat_inzerat():
    chyba = ""
    uspech = ""

    if request.method == "POST":

        if not session.get("user_id"):
            chyba = "Pridať inzerát môže iba prihlásený používateľ."

        else:
            nazov = request.form.get("title", "").strip()
            kategoria = request.form.get("category", "").strip()
            cena = request.form.get("price", "").strip()
            lokalita = request.form.get("location", "").strip()
            popis = request.form.get("description", "").strip()

            if not nazov or not kategoria or not lokalita or not popis:
                chyba = "Vyplňte všetky povinné polia."

            else:
                novy_inzerat = Inzerat(
                    nazov=nazov,
                    kategoria=kategoria,
                    cena=cena,
                    lokalita=lokalita,
                    popis=popis,
                    user_id=session["user_id"]
                )

                db.session.add(novy_inzerat)
                db.session.commit()

                uspech = "Inzerát bol úspešne pridaný."

    return render_template(
        "inzeraty/pridat_inzerat.html",
        chyba=chyba,
        uspech=uspech
    )


@app.route("/registracia", methods=["GET", "POST"])
def registracia():
    chyba = ""
    uspech = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        terms = request.form.get("terms")

        if not username or not email or not password or not password2:
            chyba = "Vyplňte všetky povinné polia."

        elif not terms:
            chyba = "Musíte súhlasiť s podmienkami používania."

        elif password != password2:
            chyba = "Heslá sa nezhodujú."

        elif not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", password):
            chyba = "Heslo musí mať minimálne 8 znakov, jedno veľké písmeno, jedno malé písmeno a jednu číslicu."

        else:
            existujuci_user = User.query.filter_by(email=email).first()

            if existujuci_user:
                chyba = "Používateľ s týmto e-mailom už existuje."
            else:
                hash_hesla = generate_password_hash(password)

                novy_user = User(
                    username=username,
                    email=email,
                    password=hash_hesla
                )

                db.session.add(novy_user)
                db.session.commit()

                uspech = "Registrácia bola úspešná. Teraz sa môžete prihlásiť."

    return render_template("auth/registracia.html", chyba=chyba, uspech=uspech)


@app.route("/prihlasenie", methods=["GET", "POST"])
def prihlasenie():
    chyba = ""
    email = ""
    sprava = request.args.get("sprava", "")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user:
            chyba = "Používateľ s týmto e-mailom neexistuje."

        elif not check_password_hash(user.password, password):
            chyba = "Nesprávne heslo."

        else:
            session["user_id"] = user.id
            session["user_name"] = user.username
            return redirect(url_for("index"))

    return render_template("auth/prihlasenie.html", chyba=chyba, email=email, sprava=sprava)


@app.route("/google-prihlasenie")
def google_prihlasenie():
    if not google.authorized:
        return redirect(url_for("google.login"))

    response = google.get("/oauth2/v2/userinfo")

    if not response.ok:
        return redirect(url_for(
            "prihlasenie",
            sprava="Prihlásenie cez Google sa nepodarilo."
        ))

    google_data = response.json()

    email = google_data.get("email", "").strip().lower()
    google_name = google_data.get("name", "")

    user = User.query.filter_by(email=email).first()

    if not user:
        nahodne_heslo = generate_password_hash(os.urandom(24).hex())

        user = User(
            username=google_name,
            email=email,
            password=nahodne_heslo
        )

        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["user_name"] = user.username

    return redirect(url_for("index"))


@app.route("/odhlasenie")
def odhlasenie():
    session.clear()
    return redirect(url_for("index"))


@app.route("/zabudnute-heslo", methods=["GET", "POST"])
def zabudnute_heslo():
    chyba = ""
    sprava = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:
            chyba = "Používateľ s týmto e-mailom neexistuje."
        else:
            token = vytvor_reset_token(user.id)
            reset_link = url_for("reset_hesla", token=token, _external=True)

            posli_reset_email(email, reset_link)

            sprava = "Resetovací odkaz bol odoslaný na váš e-mail."

    return render_template(
        "auth/zabudnute_heslo.html",
        chyba=chyba,
        sprava=sprava
    )


@app.route("/reset-hesla/<token>", methods=["GET", "POST"])
def reset_hesla(token):
    chyba = ""
    sprava = ""

    user_id = over_reset_token(token)

    if not user_id:
        return redirect(url_for(
            "prihlasenie",
            sprava="Resetovací odkaz je neplatný alebo expiroval."
        ))

    user = User.query.get(user_id)

    if not user:
        return redirect(url_for(
            "prihlasenie",
            sprava="Používateľ neexistuje."
        ))

    if request.method == "POST":
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not password or not password2:
            chyba = "Vyplňte obe polia."

        elif password != password2:
            chyba = "Heslá sa nezhodujú."

        elif not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", password):
            chyba = "Heslo musí mať minimálne 8 znakov, jedno veľké písmeno, jedno malé písmeno a jednu číslicu."

        else:
            user.password = generate_password_hash(password)
            db.session.commit()

            return redirect(url_for(
                "prihlasenie",
                sprava="Heslo bolo úspešne zmenené. Prihláste sa."
            ))

    return render_template("auth/reset_hesla.html", chyba=chyba, sprava=sprava)


if __name__ == "__main__":
    app.run(debug=True)