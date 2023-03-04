import peewee

db = peewee.SqliteDatabase('database.db')  # Создали объект базы данных


class BaseModel(peewee.Model):

    class Meta:
        database = db


class CustomUser(BaseModel):
    user_id = peewee.IntegerField(null=True)
    name = peewee.CharField()
    balance = peewee.FloatField(default=0)

    referral_link = peewee.CharField()
    followed_ref_link = peewee.CharField(default='')

    invited_id = peewee.IntegerField(default=0)
