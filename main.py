from flask import Flask, render_template, redirect, request, url_for, session, abort
from flask_bootstrap import Bootstrap
import os
from sup_media import SupMedia
from forms import SelectStock, ImageUploadForm, ImageUpdateForm
import datetime
from notification_manager import Notifications
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
Bootstrap(app)


# Connect to db
DB = os.environ.get("DB")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
oauth = OAuth(app)

# GOOGLE Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

sup_medtest = SupMedia("^GSPC")
notification = Notifications()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(100))


class Trades(db.Model):
    __tablename__ = "intraday_graphs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    tags = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(700), nullable=False)


db.create_all()

logged_user = False
email_acc_list = []
all_users = User.query.all()
for user in all_users:
    email_acc_list.append(user.email)
if not all_users:
    admin = User(email=os.environ.get("Admin"), role="Admin")
    db.session.add(admin)
    db.session.commit()

trades_dict = {'Ascen1.jpg': 'https://drive.google.com/uc?export=view&id=1byXd79kGxv9--D5B6rEFoDMbJbVSt-Zl', 'ABBajistaM.JPG': 'https://drive.google.com/uc?export=view&id=1GYuqFAT9Lft2kkYAThpnVpMLeyZeUCI4', 'ABAlcistaM.jpg': 'https://drive.google.com/uc?export=view&id=1heEK5Nd2CA_wu4cGRWPoUOat-aYfvm0n', 'ABBajistaL.jpg': 'https://drive.google.com/uc?export=view&id=1C43YFGN7_xURWCq9ZZVVdHorzftXz0Rw', 'ABAlcistaL.jpg': 'https://drive.google.com/uc?export=view&id=1yWrzEntwBu9nDUF_xJjhyDEbYfpczijD', 'ABBajistaK.jpg': 'https://drive.google.com/uc?export=view&id=1mdZSP0EQ_iflfmKSMkXq_wIakQv50Bq1', 'ABLateral2.jpg': 'https://drive.google.com/uc?export=view&id=125Iv7KTgBgvcShtGV4U6NwPrAEbEFVSw', 'ABBajistaJ.jpg': 'https://drive.google.com/uc?export=view&id=1XEWC-Db2bvRVIsq6MnolVVs4dXPcCRxv', 'ABBajistaI.jpg': 'https://drive.google.com/uc?export=view&id=18AeFpk_nSg2kj1YXN4vkrXAKvNviXjp6', 'ABBajistaH.jpg': 'https://drive.google.com/uc?export=view&id=1-co8HMgz9YYJq9pm0OkOaMdcyytQGg7r', 'ABBajistaF.jpg': 'https://drive.google.com/uc?export=view&id=1bdXeBxXnU8aiAd_OpUwilF2rsPhuxT9k', 'ABBajistaE.jpg': 'https://drive.google.com/uc?export=view&id=1caeFxnCQ22IozdjS6dZZX-d4nTuFmj6u', 'ABBajistaD.jpg': 'https://drive.google.com/uc?export=view&id=1nXK4LcYekMrsbqhMEAP1D_uuRVaizYDz', 'ABBajistaC.jpg': 'https://drive.google.com/uc?export=view&id=1WyOeFz34TS_WdFwDlfXlFodcu0PrEoZZ', 'ABBajistaB.jpg': 'https://drive.google.com/uc?export=view&id=1m3RLJ-tfZHQmsjFtWJlAKNA9FPRAGGKm', 'ABAlcistaK.jpg': 'https://drive.google.com/uc?export=view&id=1xxVdlnbbDAkqh3_Cgb9oG1RqJhQs_rwr', 'ABAlcistaJ.jpg': 'https://drive.google.com/uc?export=view&id=1kY0juk2-DSMSi8zBvFjjQn3iCvs2jBJH', 'ABBajistaA.jpg': 'https://drive.google.com/uc?export=view&id=1-aoHFTUm964WdJ3OA4CRsP5esAgWybYO', 'ABAlcistaI.jpg': 'https://drive.google.com/uc?export=view&id=1d45zmHdj6y666C-gKSqFcI55FawEyaMr', 'ABBajista0.jpg': 'https://drive.google.com/uc?export=view&id=1zaw1r3fTUhvNcBF-th4MvtDgnhXaiqCZ', 'ABAlcistaH.jpg': 'https://drive.google.com/uc?export=view&id=1BsE1nn9pQHRNdTCwUYw18dmh8yLoluSR', 'ABAlcistaG.jpg': 'https://drive.google.com/uc?export=view&id=1nl1kWdp-m5QPvNKP1g_ZdRVaY8OQlEKj', 'ABAlcistaE.jpg': 'https://drive.google.com/uc?export=view&id=1ULqmOPrqDo9DDjZE-Zz_JCEwEoO0c5nw', 'ABAlcistaF.jpg': 'https://drive.google.com/uc?export=view&id=1fqIfWwlxuVny_0VVg3aZrr1Itn8skKxo', 'ABBajista9.jpg': 'https://drive.google.com/uc?export=view&id=16z1ySD6HtyXa_LgYdEJOQbOJC3_qVa4z', 'ABBajista8.jpg': 'https://drive.google.com/uc?export=view&id=1rrIlueR7q-V62Dp5pGfPN-Gp_19iVAO_', 'ABLateral1.jpg': 'https://drive.google.com/uc?export=view&id=1JwDyXHYwqDJlGf7Cr1cFV1YwQ7p0ote3', 'ABAlcistaD.jpg': 'https://drive.google.com/uc?export=view&id=1wQd2pV4p49YP-lgMdWL4XiCpULz461f6', 'ABAlcistaC.jpg': 'https://drive.google.com/uc?export=view&id=1rTm8dIfctuxqd7bWpyiNa0LWsxPgoQuw', 'ABAlcistaB.jpg': 'https://drive.google.com/uc?export=view&id=1sJa5jrwsg7zAyWOHahrR7w7HM64QLePU', 'ABAlcistaA.jpg': 'https://drive.google.com/uc?export=view&id=1T4mpF08pBUUY02YHL0tO47F7TAIq849_', 'ABAlcista0.jpg': 'https://drive.google.com/uc?export=view&id=1DI6vc-t3vfed5HFXemUoeDoMa-R2Kjsx', 'ABAlcista9.jpg': 'https://drive.google.com/uc?export=view&id=1CT1OIHlQv4YaIcNKZx27_Ao34fBp413g', 'ABBajista7.jpg': 'https://drive.google.com/uc?export=view&id=1aPpK6Lgru6CzFs70STTBYEcyvuuQFgpQ', 'ABBajista6.jpg': 'https://drive.google.com/uc?export=view&id=1pHDK-TKgKBKtWvMDHfQDt41lN8OzCCyP', 'ABBajista5.jpg': 'https://drive.google.com/uc?export=view&id=1zYycszwybu05og05xl0MuwVO7q9Wd8UG', 'ABAlcista8.jpg': 'https://drive.google.com/uc?export=view&id=1bKw3yRATiTLSJS6SkdpWaqfWa9a89_li', 'AscenC.jpg': 'https://drive.google.com/uc?export=view&id=1qzizCDVJ-H1RwcONeHzfllsphGMmm_Z4', 'Ascen2.jpg': 'https://drive.google.com/uc?export=view&id=1sNul4s2GwdGdtNfcR6SqICrOEBgCYsJK', 'Ascen5.jpg': 'https://drive.google.com/uc?export=view&id=1NXzG_-OzRcIpCQ2x_Lz0FK6DC0bW0QG3', 'Ascen6.jpg': 'https://drive.google.com/uc?export=view&id=1ry-LUVZzFG_67g_vhe9e2xlY346UqhkP', 'Ascen4.jpg': 'https://drive.google.com/uc?export=view&id=1M2o-hhGfunN4MWfheZfq5tOcv-1nqXUW', 'Ascen8.jpg': 'https://drive.google.com/uc?export=view&id=10bwC7stKT_V2eTdOw_vQ4hm6ltqSfz7M', 'AscenB.jpg': 'https://drive.google.com/uc?export=view&id=1Mfi2BRyRw2740PHdMN-pNOKuhNu34ShJ', 'Ascen3.jpg': 'https://drive.google.com/uc?export=view&id=1XE7jHaOdfa7Fgqu12FBpCgA_ITfkMZCg', 'Ascen7.jpg': 'https://drive.google.com/uc?export=view&id=1XEDM-CPQwwL4zKa8M_AayjVVtJiBgoRQ', 'AscenA.jpg': 'https://drive.google.com/uc?export=view&id=1pYq7lZUGmPQqz2Jb9lNqhLSbOWZ9WTB3', 'Ascen9.jpg': 'https://drive.google.com/uc?export=view&id=1Urm-N72ds3s9J6ky0QyShz8e3Yx6BYeR', 'ABBajista4.jpg': 'https://drive.google.com/uc?export=view&id=1T_YUzJFz_azQPoxa0gXfL_gdPcfJRLdY', 'ABAlcista7.jpg': 'https://drive.google.com/uc?export=view&id=1spTDAlixNUux659APBee__1Y7AGZ89R6', 'ABAlcista6.jpg': 'https://drive.google.com/uc?export=view&id=18tjNacXJwG7HhHK4yUsAJ0UXNlQBxpcw', 'ABAlcista5.jpg': 'https://drive.google.com/uc?export=view&id=1WYGLeOEI0kIth3Z6ABgRGKdbur293enD', 'ABAlcista4.jpg': 'https://drive.google.com/uc?export=view&id=1YG2h9QprC2AcTGbnAW8gKWwC7TJKRnA7', 'ABAlcista3.jpg': 'https://drive.google.com/uc?export=view&id=1VrlHCKDZxCtnom7d7nOGYT83lZxNslmJ', 'ABAlcista2.jpg': 'https://drive.google.com/uc?export=view&id=1fypglBzfwZaXBkby0Uf0PBRfhgMawlRK', 'ABBajista3.jpg': 'https://drive.google.com/uc?export=view&id=1XXTFYYf_DXyJ8vbIIA-TiMMT1SdUD5oE', 'ABBajista2.jpg': 'https://drive.google.com/uc?export=view&id=1UCBWRlPIkhLncldjpZvM8fl3KekQj_jA', 'ABBajista1.jpg': 'https://drive.google.com/uc?export=view&id=1EWlAiA_eIKvH1uW5dEy_b099VX4Tz_Ml', 'ABAlcista1.jpg': 'https://drive.google.com/uc?export=view&id=12PAluBY-IaiATLERlYxgxECtcLGwbaPI', 'AAAlcistaI.JPG': 'https://drive.google.com/uc?export=view&id=1pk5RuFwf_BQ43jdGJv82wcBuB_QGrXam', 'BbajistaN.jpg': 'https://drive.google.com/uc?export=view&id=1UsqSUJgIy_dxQrxlSrIn_c557V3CFl0p', 'BLateral8.jpg': 'https://drive.google.com/uc?export=view&id=1i9uzuVViH7gSNhkBm-4gIacfuziCttb3', 'BLateral7.jpg': 'https://drive.google.com/uc?export=view&id=1cFwK4fcP17odcS3EZadIMcq5j5aXdUpA', 'DAlcista0.jpg': 'https://drive.google.com/uc?export=view&id=1hmYw2kgabecAdUKCILfnPE52ljqjJJ1i', 'DAlcista9.jpg': 'https://drive.google.com/uc?export=view&id=10czwPfJdXI-9jnZktLOnptD5DsEDWfdl', 'BLateral5.jpg': 'https://drive.google.com/uc?export=view&id=1NwhbOM2aXamNJHLCG2uQPMcvhd5ZRVId', 'BLateral6.jpg': 'https://drive.google.com/uc?export=view&id=1Z16vr8Gt1WzAwnDFpevE-qk_2m4K_X0Z', 'DAlcista8.jpg': 'https://drive.google.com/uc?export=view&id=1SF4ng39km8QbHYTGuXsVDtwplyqm9eEu', 'DAlcista7.jpg': 'https://drive.google.com/uc?export=view&id=1SUyZVBzZ-t0_Y0ujoNyof3cki1sCrAdi', 'DAlcista6.jpg': 'https://drive.google.com/uc?export=view&id=1TsTF50yRziYB43D7izwi1TwCIHPdRGB2', 'BbajistaL.jpg': 'https://drive.google.com/uc?export=view&id=1kxFXlDrImBfxVpOvKxfuhqsv75ro0mFB', 'BbajistaK.jpg': 'https://drive.google.com/uc?export=view&id=1uG_sS6AnBH8liCjL8iIVXADXILPj6HHL', 'BbajistaJ.jpg': 'https://drive.google.com/uc?export=view&id=1-5aBAOi4S-eWlJTfaIEa--MnJYXwpV8E', 'DAlcista5.jpg': 'https://drive.google.com/uc?export=view&id=1SXNHwPqWo741LrmMThVM2Rt0jdssLKtq', 'DAlcista4.jpg': 'https://drive.google.com/uc?export=view&id=1sGySIJI1Xr2qutyuSl_cq-cS6s4QAWsM', 'DAlcista3.jpg': 'https://drive.google.com/uc?export=view&id=1fOfiD3l0DSMTMzQnoyB9mgmJ6iQktttN', 'DAlcista2.jpg': 'https://drive.google.com/uc?export=view&id=1_7CXdg4BvufcW4k65bPQaDSEP6ZmWjlN', 'BbajistaI.jpg': 'https://drive.google.com/uc?export=view&id=1EYiF2VXEvMFPPNNXidZyej0XK7L5lbBE', 'BbajistaH.jpg': 'https://drive.google.com/uc?export=view&id=1W9Y3j4sB_6H-WPW5mQAD9O9CUwL_wMjv', 'BbajistaG.jpg': 'https://drive.google.com/uc?export=view&id=1FUf1DVG3dwm7QGyoCmHCVrd9CHikRjlp', 'BbajistaF.jpg': 'https://drive.google.com/uc?export=view&id=1g1D2yXtmrR7AO-DyzCzMedcErsPcDsF6', 'DAlcista1.jpg': 'https://drive.google.com/uc?export=view&id=19bOmIU6pmA8JGyqtsvLk6DBL2S7ZC4KR', 'BbajistaD.jpg': 'https://drive.google.com/uc?export=view&id=1bkeFmp_eHBkz4NB9kjUINbYHdyORiC4t', 'BbajistaE.jpg': 'https://drive.google.com/uc?export=view&id=1tJxjYSBkpncwMmH1mrs_wld_hJoobG7P', 'BbajistaC.jpg': 'https://drive.google.com/uc?export=view&id=1UAhx_3neApK_HHnf1HYEAL_pM8sbaL4h', 'BbajistaB.jpg': 'https://drive.google.com/uc?export=view&id=1h1OUcZP12i606hPHsvGpHMbkPjSz6r_x', 'BLateral2.jpg': 'https://drive.google.com/uc?export=view&id=1Iu90HDm3J-7CKcX_MEZsF9ybsnKB1S8f', 'BbajistaA.jpg': 'https://drive.google.com/uc?export=view&id=1Tp3TyfQlT6pXCOH7p-H7DjN-iyJDHywb', 'BLateral1.jpg': 'https://drive.google.com/uc?export=view&id=1ojBb4E2ZT74HGAYvba_BPzPQ8ZSefZnt', 'Bbajista0.jpg': 'https://drive.google.com/uc?export=view&id=1gAOAvbbFl2cO--aXJYAWevSXuA1gCjFu', 'Bbajista9.jpg': 'https://drive.google.com/uc?export=view&id=1UjL6qup41sFr7u41JmF0mio1E_2XwQxd', 'Bbajista8.jpg': 'https://drive.google.com/uc?export=view&id=1pDwqwXpxSp9EUVm6aGC1MdlzU2XkhFzO', 'Bbajista7.jpg': 'https://drive.google.com/uc?export=view&id=1Zb2AhFF3ufS5R4zkbY7SahmSk6VNZvf9', 'Bbajista6.jpg': 'https://drive.google.com/uc?export=view&id=1hLPJ37IgEAK_U368js71jmoFhcdR8PrC', 'Bbajista5.jpg': 'https://drive.google.com/uc?export=view&id=1WsjL3s6VL2_8X786ulUA0TzJmzOMAAeA', 'Bbajista4.jpg': 'https://drive.google.com/uc?export=view&id=1ixYnbOozl6icdxn8YOTKih8tt5-W-jbH', 'Bbajista3.jpg': 'https://drive.google.com/uc?export=view&id=1FJJQnrE4hZoe7pLp2zKXPlHFvp_UuSFE', 'Bbajista2.jpg': 'https://drive.google.com/uc?export=view&id=1CkYX_BrVypoWqBuhoLmvIwmYrNHIhKI-', 'Bbajista1.jpg': 'https://drive.google.com/uc?export=view&id=1W_AsuiMdT7dSSeVRTfXJX_nyUOiYpyS7', 'DABajistaB.jpg': 'https://drive.google.com/uc?export=view&id=1baicQWzIdBmmBXJDlQgr4MCV5Mvj96l8', 'DAAlcista8.jpg': 'https://drive.google.com/uc?export=view&id=1-es-OsgzgSll-tt2oTnI13z8eeQGZbUA', 'DAAlcista7.jpg': 'https://drive.google.com/uc?export=view&id=1bcWPpVq1tuegl4hgn__ExNZ86CYp6ZF5', 'DAAlcista6.jpg': 'https://drive.google.com/uc?export=view&id=1oyea1Dq4XUQVk5IFpLQDf1gcpFJe-acc', 'DAAlcista5.jpg': 'https://drive.google.com/uc?export=view&id=1Fjt1ifBtHr9Q2EOpvgyjU2iiIhkL-HyC', 'DAAlcista4.jpg': 'https://drive.google.com/uc?export=view&id=1zOy_5GjPTwVj4FashKROwXWTQdgGo_tX', 'DAAlcista1.jpg': 'https://drive.google.com/uc?export=view&id=1slIqr1GQ5TLLHdR3i1kGanzEsSm4TF2k', 'DAAlcista3.jpg': 'https://drive.google.com/uc?export=view&id=1Y409a0GoplT1KuCF08axJ6JXLnh8NjmM', 'DAAlcista2.jpg': 'https://drive.google.com/uc?export=view&id=1msDnhkq95QIYPCjzkO8qBG3e1bQOUfzx', 'DABajistaD.jpg': 'https://drive.google.com/uc?export=view&id=1wSiVaK4NqcDBRO3hRTd1Nhh0F7Df17_7', 'DABajistaC.jpg': 'https://drive.google.com/uc?export=view&id=1f9q6syl0-_5Cm6AzDtifAs9NK6TjP1vg', 'DABajistaA.jpg': 'https://drive.google.com/uc?export=view&id=1njur5kYFYUuKBQkXe3I2_M6siGufTb1n', 'DABajista0.jpg': 'https://drive.google.com/uc?export=view&id=17BxrhUrXgVeJoQPpN0q-JwT-5OL0PBau', 'DABajista7.jpg': 'https://drive.google.com/uc?export=view&id=1ZqywLYwybHF3ZSFJGXygDy7M9-r2QimL', 'DABajista8.jpg': 'https://drive.google.com/uc?export=view&id=1ZIwbA-jtYCCqvlsYJaBWbMJHy4hc6gSb', 'DABajista9.jpg': 'https://drive.google.com/uc?export=view&id=1oMA1UBarYL4cY6IXODnldfT5m4kwxVI4', 'BLateral4.jpg': 'https://drive.google.com/uc?export=view&id=1suPhQa0zTudRbjY5BFAzR6cYpBWx0rkG', 'DALateral3.jpg': 'https://drive.google.com/uc?export=view&id=1K5KaASAH2IPgdZZA_TCnRS_WRsuANGCw', 'DABajista6.jpg': 'https://drive.google.com/uc?export=view&id=1-omfPPFtnXzy3iamRQ34l8Fu5J14LqeW', 'DABajista5.jpg': 'https://drive.google.com/uc?export=view&id=1drRwo51hXmWPzeXBHA5JY5S0yl23KCHS', 'DABajista4.jpg': 'https://drive.google.com/uc?export=view&id=1IVCsYdWKaH5hI30g2bqwKJOAtpgRCG4X', 'DABajista3.jpg': 'https://drive.google.com/uc?export=view&id=1En9wWJqhZEoAnlW2_eAKvXz_S4NMJSBi', 'DALateral2.jpg': 'https://drive.google.com/uc?export=view&id=1cvtj0tGYftgktwQl-uHS0A64epitX-J2', 'DABajista2.jpg': 'https://drive.google.com/uc?export=view&id=1nG9_e49t4LunYf2fiTTU28fU4N2Un3H_', 'DABajista1.jpg': 'https://drive.google.com/uc?export=view&id=1MzDO5SgCoZoYD7qP5VXZklemgOJSr0bn', 'DALateral1.jpg': 'https://drive.google.com/uc?export=view&id=1ecu7rXpqlZ9S9DigSL66H1QMwJr6vXZD', 'AAAlcistaH.jpg': 'https://drive.google.com/uc?export=view&id=1WNqzSlanCzrzwF7Zeaa-I7-QYSnREzZD', 'AAAlcistaG.jpg': 'https://drive.google.com/uc?export=view&id=1lmsv9me-hUMOTKkJzRwyyeNjpjBgcT-F', 'AAAlcistaF.jpg': 'https://drive.google.com/uc?export=view&id=1_vlwEEvgdf9SUtHZowLIB1wnjCxKv3gR', 'AAAlcistaE.jpg': 'https://drive.google.com/uc?export=view&id=1R7G0pthpAhvCtB98azTLxEUn1rcEVGES', 'AAAlcistaD.jpg': 'https://drive.google.com/uc?export=view&id=12vTZ278KlNf-Qs7Q2utVF2Xl-Ray7O9U', 'AAAlcistaC.jpg': 'https://drive.google.com/uc?export=view&id=16yDurmDKh6d1M8zUoyODnLWF3MH_GpF8', 'AAAlcistaB.jpg': 'https://drive.google.com/uc?export=view&id=1XZfvg4BEjp3qnNf4yTWizVEHN79xf92e', 'AALateral7.jpg': 'https://drive.google.com/uc?export=view&id=1uv2Trb2F4OSNeStTo_xrg7rZ2Y6Til9o', 'AALateral6.jpg': 'https://drive.google.com/uc?export=view&id=1-a0-BdGIHrHPnJf8DUckLlNuh0QQ7HOE', 'AAAlcistaA.jpg': 'https://drive.google.com/uc?export=view&id=12Dq6f0HPDZOZv51zLcLojVOe8AZxy6Jw', 'Giro3.jpg': 'https://drive.google.com/uc?export=view&id=1RSEF-y2rEE2EckP8Yxlz3Ek5SroOxyaz', 'AABajistaI.jpg': 'https://drive.google.com/uc?export=view&id=1I-VaIUh0WyfJZVSL_JgPvKaJUWIiA74k', 'AABajistaH.jpg': 'https://drive.google.com/uc?export=view&id=1nE36rGnH6BcumkYO6ItfMqhEFXVYfVkS', 'AABajistaG.jpg': 'https://drive.google.com/uc?export=view&id=1nllZ5dxAWjstTCB_GIZLdEgpHn6Sbcps', 'AABajistaF.jpg': 'https://drive.google.com/uc?export=view&id=1f1tiHz8c5SM7jAyJA5mC5DDNAXJ7T0Ic', 'AABajistaE.jpg': 'https://drive.google.com/uc?export=view&id=1lixlz8aGoRI0avhhluhOFUXmTajTbYFI', 'AALateral5.jpg': 'https://drive.google.com/uc?export=view&id=1V69kFG3jdb7sra_Cu6hvy7NIsetGHh1t', 'AAAlcista9.jpg': 'https://drive.google.com/uc?export=view&id=1ISnAUHNPl4tEFD_Snen9Ndf5ICkGI1xQ', 'AAAlcista8.jpg': 'https://drive.google.com/uc?export=view&id=1WsC70eiUoB4YyV64e19uvEljfNyo4-nD', 'AAAlcista7.jpg': 'https://drive.google.com/uc?export=view&id=1RrhyU8r-9AggFf7mzOG--Yc0fmZ7HfgX', 'AAAlcista6.jpg': 'https://drive.google.com/uc?export=view&id=1r8JjNI-FzKb8KItCDRxTjpLDkA-JhJLv', 'AAAlcista5.jpg': 'https://drive.google.com/uc?export=view&id=1pjfV5-SjzMYaWilRQBO1ggF7wLPMhN8A', 'AABajistaD.jpg': 'https://drive.google.com/uc?export=view&id=1f8Z0YlGnKf-5R1S4c5LQu8qnHkFL1GF3', 'AABajistaC.jpg': 'https://drive.google.com/uc?export=view&id=18rRnHs9qz0KMPzspqGkOsTJtVZ6J0hiG', 'AABajistaB.jpg': 'https://drive.google.com/uc?export=view&id=1VHTneLhj4vMREjN_-4vDaKSiVAO7LP-u', 'AALateral4.jpg': 'https://drive.google.com/uc?export=view&id=1PlQSFOlvn6jORnh5QrmDbp20xln-8_OD', 'AALateral3.jpg': 'https://drive.google.com/uc?export=view&id=1GeoiSXIcGQkyyYAZbb8_cNulICmmyCE_', 'AAAlcista4.jpg': 'https://drive.google.com/uc?export=view&id=1CcQOFn79QVfeJn74X-GqVJVG96_Wn029', 'AAAlcista3.jpg': 'https://drive.google.com/uc?export=view&id=1yAd1og9WvcsmpMeiJgB4bfvHKhoLRohd', 'AABajistaA.jpg': 'https://drive.google.com/uc?export=view&id=1rVVTD6woAV-TNodfBiGf0gVZMVqqrhMg', 'Giro2.jpg': 'https://drive.google.com/uc?export=view&id=16yA5YqQQg6pQp-SSN40syy4iA6EgAeMH', 'AABajista9.jpg': 'https://drive.google.com/uc?export=view&id=1ZXCX1NBGDgtueOQWYqKrb350Zx5q6MFi', 'AABajista8.jpg': 'https://drive.google.com/uc?export=view&id=190szTP7PmPTlSXcK7XetsB7-s95NY2qe', 'AALateral2.jpg': 'https://drive.google.com/uc?export=view&id=1n4ZHEbPmp4fmFfxT7nDwmo3tTHMY52MV', 'AAAlcista2.jpg': 'https://drive.google.com/uc?export=view&id=147tzSd1djmR5vTg7lQsAdjNi-IlL1UIF', 'AABajista7.jpg': 'https://drive.google.com/uc?export=view&id=1oKAbec1tMwNNtrs7Ldw1BP1YmoqWZEc4', 'Giro1.jpg': 'https://drive.google.com/uc?export=view&id=1FcZFzWL5Qbh5gZ3ISO76Yf-mwSGTUh6R', 'AABajista6.jpg': 'https://drive.google.com/uc?export=view&id=1FSch5wUEi581W_f7PE9tw_EGbJcKMktT', 'AABajista5.jpg': 'https://drive.google.com/uc?export=view&id=1fDUMqk9P9i5RQWWbOuN-p71w7Ke0Wd6p', 'AABajista4.jpg': 'https://drive.google.com/uc?export=view&id=1CaWuYn6uZWbvuwD1_h_F43-tE6jru82A', 'AABajista3.jpg': 'https://drive.google.com/uc?export=view&id=1FExnw-NeI985ZZg44T-oKB-8oTa15ryn', 'AABajista2.jpg': 'https://drive.google.com/uc?export=view&id=15fc0soqExMgdnb9t07uVLTQ6E3PD5SLx', 'AALateral1.jpg': 'https://drive.google.com/uc?export=view&id=1P7ynvXh5BG_nSOyR9nrwQcM5WYPR1470', 'AAAlcista1.jpg': 'https://drive.google.com/uc?export=view&id=1OSAtiZtVVhhOZfOvSIzLzGwese_SnKyu', 'AABajista1.jpg': 'https://drive.google.com/uc?export=view&id=19SeWurXKXcaLgHhnyy5p7uSJDo77xhYC'}


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logged_user = session.get("user")["email"]
            logged_user_role = User.query.filter_by(email=logged_user).first()
        except TypeError:
            return abort(403, description="You have to be an Admin and login to access this site.")
        try:
            if logged_user_role.role != "Admin":
                return abort(403, description="Only Admins have access to this section.")
        except TypeError:
            return abort(403, description="You have to be an Admin and login to access this site.")
        return f(*args, **kwargs)

    return decorated_function


def users_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_user = session.get("user")
        try:
            if logged_user["email"] not in email_acc_list:
                return abort(403, description="Only registered users have access to this section.")
        except TypeError:
            return abort(403, description="You have to be a registered user and login to access this site.")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/superacion-media", methods=["POST", "GET"])
@users_only
def superacion_media():
    global sup_medtest
    global logged_user
    current_user_email = session.get("user")["email"]
    current_user_role = User.query.filter_by(email=current_user_email).first()
    if session.get("user"):
        logged_user = True
    form = SelectStock()
    try:
        action = sup_medtest.take_action()
        last_date = sup_medtest.last_date()
        tendency_change_date = sup_medtest.get_tendency_change_date()
        tendency_months = sup_medtest.get_tendency_months()
        profit = sup_medtest.get_profit()
        graph = sup_medtest.display_graph()
        ticker_name = sup_medtest.get_ticker_name()
    except KeyError:
        action = "Try again later."
        last_date = "Try again later."
        tendency_change_date = "Try again later."
        tendency_months = "Try again later."
        profit = "Try again later."
        graph = "Try again later."
    if request.method == "POST":
        if form.validate():
            stock = form.stock.data
            sup_medtest = SupMedia(stock)
            return redirect("/superacion-media")

    return render_template("index.html", form=form, action=action, date=last_date, tendency_months=tendency_months,
                           tendency_change_date=tendency_change_date, graph=graph, profit=profit, role=current_user_role.role,
                           stock_name=ticker_name, logged_user=logged_user)


@app.route("/intraday", methods=["POST", "GET"])
@users_only
def intraday():
    global logged_user
    current_user_email = session.get("user")["email"]
    current_user_role = User.query.filter_by(email=current_user_email).first()
    if session.get("user"):
        logged_user = True
    all_trades = Trades.query.all()
    if not all_trades:
        for key in trades_dict:
            new_trade = Trades(name=key, tags="", img_url=trades_dict[key])
            db.session.add(new_trade)
        db.session.commit()
    total = len(all_trades)
    list_tags = []
    for trade in all_trades:
        if trade.tags:
            trade_tags = trade.tags.split(",")
            for tag in trade_tags:
                if tag not in list_tags:
                    list_tags.append(tag)

    return render_template("intraday.html", trades=all_trades, tags=list_tags, total=total, logged_user=logged_user,
                           role=current_user_role.role)


@app.route("/add-graph", methods=["POST", "GET"])
@admin_only
def add_graph():
    global logged_user
    if session.get("user"):
        logged_user = True
    form = ImageUploadForm()
    if form.validate_on_submit():
        name = form.trade_name.data
        string_of_tags = form.trade_tags.data
        url_to_modify = form.trade_url.data
        split_url = url_to_modify.split("/")
        url = f"https://drive.google.com/uc?export=view&id={split_url[5]}"
        new_trade = Trades(name=name, tags=string_of_tags, img_url=url)
        db.session.add(new_trade)
        db.session.commit()
        return redirect(url_for("intraday"))

    return render_template("addGraphs.html", form=form, logged_user=logged_user)


@app.route("/select", methods=["POST", "GET"])
@users_only
def select():
    global logged_user
    current_user_email = session.get("user")["email"]
    current_user_role = User.query.filter_by(email=current_user_email).first()
    if session.get("user"):
        logged_user = True
    trade_id = request.args.get("trade_id")
    selected_trade = Trades.query.get(trade_id)
    selected_trade_tags = selected_trade.tags.split(",")

    return render_template("select.html", selected_trade=selected_trade,
                           trade_tags=selected_trade_tags,
                           logged_user=logged_user,
                           role=current_user_role.role)


@app.route("/delete", methods=["POST", "GET"])
@admin_only
def delete_trade():
    trade_id = request.args.get("trade_id")
    trade_to_delete = Trades.query.get(trade_id)
    db.session.delete(trade_to_delete)
    db.session.commit()
    return redirect(url_for("intraday"))


@app.route("/edit-trade", methods=["POST", "GET"])
@admin_only
def edit_trade():
    global logged_user
    current_user_email = session.get("user")["email"]
    current_user_role = User.query.filter_by(email=current_user_email).first()
    if session.get("user"):
        logged_user = True
    trade_id = request.args.get("trade_id")
    selected_trade = Trades.query.get(trade_id)
    form = ImageUpdateForm(
        trade_name=selected_trade.name,
        trade_tags=selected_trade.tags,
        trade_url=selected_trade.img_url
    )
    if form.validate_on_submit():
        trade_id = request.args.get("trade_id")
        selected_trade = Trades.query.get(trade_id)
        selected_trade.name = form.trade_name.data
        selected_trade.tags = form.trade_tags.data
        selected_trade.img_url = form.trade_url.data
        db.session.commit()
        return redirect(url_for("intraday"))
    return render_template("editTrade.html", form=form, selected_trade=selected_trade, logged_user=logged_user,
                           role=current_user_role.role)


@app.route("/signup", methods=["POST", "GET"])
@admin_only
def signup():
    global logged_user
    if session.get("user"):
        logged_user = True
    if request.method == "POST":
        user_name = request.form.get("name")
        user_email = request.form.get("email")
        user_role = request.form.get("role")
        new_user = User(name=user_name.title(), email=user_email, role=user_role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("users"))
    return render_template("signup.html", logged_user=logged_user)


@app.route("/users", methods=["POST", "GET"])
@admin_only
def users():
    global logged_user
    user_info = User.query.all()
    if session.get("user"):
        logged_user = True;
    return render_template("users.html", users=user_info, logged_user=logged_user)


@app.route("/edit-user", methods=["POST", "GET"])
@admin_only
def edit_user():
    global logged_user
    if session.get("user"):
        logged_user = True
    user_id = request.args.get("user_id")
    user_to_update = User.query.get(user_id)

    if request.method == "POST":
        user_to_update.id = request.args.get("user_id")
        user_to_update.name = request.form.get("update_name")
        user_to_update.email = request.form.get("update_email")
        user_to_update.role = request.form.get("update_role")
        db.session.commit()
        return redirect(url_for("users"))

    return render_template("edit.html", user=user_to_update, logged_user=logged_user)


@app.route("/delete-user/<user_id>", methods=["POST", "GET"])
@admin_only
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("users"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            oauth.register(
                name="google",
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                server_metadata_url=GOOGLE_DISCOVERY_URL,
                client_kwargs={
                    "scope": "openid email profile"
                }
            )
            # Redirect to google_auth function
            redirect_uri = url_for("callback", _external=True)
            return oauth.google.authorize_redirect(redirect_uri)
        except ConnectionError:
            return abort(503, description="There was a problem connecting with Google, try again later.")

    return render_template("login.html")


@app.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user = token.get("userinfo")
    if user:
        session["user"] = user

    return redirect(url_for('superacion_media'))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user", None)
    if request.method == "POST":
        session.pop("user", None)
        return redirect(url_for("login"))
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
