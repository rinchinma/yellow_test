from create_bot import bot
from models import db, CustomUser


class FunctionModule:

    def createLink(self, user_id):
        link = 'https://t.me/pissa_testus_bot?start={user_id}'.format(user_id=user_id)
        return link

    def startReferral(self, message):
        user_id = int(message.from_user.id)
        # ��������� ������� ���� �����-�� �������������� ���������� �� ������
        if " " in message.text:
            invited_id = message.text.split(' ')[1]
            # ������� ������������� ������ � �����
            try:
                invited_id = int(invited_id)
                # ��������� �� �������������� TG ID ������������ TG ID ��������
                if user_id != invited_id:
                    # ���������, ���� �� ����� ������� � ���� ������
                    query = CustomUser.get(user_id=invited_id)
                    invited_user = CustomUser.get(id=query)
                    invited_user.followed_ref_link += ' ' + message.from_user.username
                    invited_user.save()

                    referrer_name = message.from_user.username
                    text = 'A new user has followed your link - {}!'.format(referrer_name)
                    bot.send_message(invited_user.user_id, text)

                    with db:
                        CustomUser.get_or_create(
                            user_id=user_id,
                            name=message.from_user.username,
                            referral_link=self.createLink(user_id),
                            invited_id=int(invited_id),
                        )
            except:
                return False
        else:
            with db:
                CustomUser.get_or_create(
                    user_id=user_id,
                    name=message.from_user.username,
                    referral_link=self.createLink(user_id),
                )

    def referral_append(self, from_list):
        result_str = ''
        for partner in from_list:
            if partner.followed_ref_link != '':
                names = partner.followed_ref_link.split(' ')
                for name in names:
                    if name != '':
                        query = CustomUser.get(name=name)
                        referrer = CustomUser.get(id=query)
                        result_str += referrer.name + '\n'
        return result_str

    def getMyReferrals(self, followed_referrals):
        # ���������� ������ �������������, ������� ������ �� ����� ������
        first_level_referrals_holder = list()
        first_level_referrals_holder_str = ''

        for name in followed_referrals.split(' '):
            if name != '':
                query = CustomUser.get(name=name)
                referrer = CustomUser.get(id=query)
                first_level_referrals_holder.append(referrer)
                first_level_referrals_holder_str += referrer.name + '\n'

        second_level_referrals_holder = self.referral_append(first_level_referrals_holder)
        third_level_referrals_holder = self.referral_append(second_level_referrals_holder)
        fourth_level_referrals_holder = self.referral_append(third_level_referrals_holder)
        fifth_level_referrals_holder = self.referral_append(fourth_level_referrals_holder)

        return first_level_referrals_holder_str, second_level_referrals_holder, \
            third_level_referrals_holder, fourth_level_referrals_holder, fifth_level_referrals_holder

    def implement_payment(self, referer_id, money):
        print(money)
        if referer_id != 0:
            query_old_user = CustomUser.get(user_id=referer_id)
            old_user = CustomUser.get(id=query_old_user)
            old_user.balance += money
            old_user.save()
            return old_user.invited_id
        else:
            return 0

    def payReferrer(self, referer_id, price):
        first_level_user_money = (price / 100) / 4
        second_level_user_money = (price / 100) / 10
        other_levels_user_money = (price / 100) / 20

        first_level_referrer_id = referer_id
        second_level_referrer_id = self.implement_payment(first_level_referrer_id, first_level_user_money)
        third_level_referrer_id = self.implement_payment(second_level_referrer_id, second_level_user_money)
        fourth_level_referrer_id = self.implement_payment(third_level_referrer_id, other_levels_user_money)
        fifth_level_referrer_id = self.implement_payment(fourth_level_referrer_id, other_levels_user_money)
        self.implement_payment(fifth_level_referrer_id, other_levels_user_money)

        return [first_level_referrer_id, second_level_referrer_id,
                third_level_referrer_id, fourth_level_referrer_id, fifth_level_referrer_id]
