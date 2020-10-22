import random
import sqlite3



class BankingSystem:
    IIN = '400000'  # Issuer Identification Number

    def __init__(self):
        self.user_input = 0
        self.cur, self.conn = self.create_table_of_cards()

    def create_table_of_cards(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0
                        )""")
        self.conn.commit()
        return self.cur, self.conn

    def show_main_menu(self):
        is_last_action = False
        print("1. Create an account\n2. Log into account\n0. Exit")
        self.user_input = int(input())
        if self.user_input == 1:
            self.create_account()
        elif self.user_input == 2:
            users_number, users_pin = self.get_credentials()
            is_logged_in = self.log_in(users_number, users_pin)
            if is_logged_in:
                is_last_action = self.show_logged_in_menu(users_number)
        else:
            print("Bye!")
            is_last_action = True
        return is_last_action

    def create_account(self):
        is_existing = True
        while is_existing:
            acc_number = BankingSystem.IIN + str(random.randint(0, 999999999)).rjust(9, "0")
            acc_number = self.add_checksum(acc_number)
            pin = str(random.randint(0, 9999))
            pin = pin.rjust(4, "0")
            is_existing = bool(self.check_if_exists(acc_number))
            if not is_existing:
                print("Your card has been created")
                print(f"Your card number:\n{acc_number}\nYour card PIN:\n{pin}")
                self.cur.execute("INSERT INTO card VALUES (:id, :account_number, :pin, :balance)",
                        {"id": None, "account_number": acc_number, "pin": pin, "balance": 0})
                self.conn.commit()

    def add_checksum(self, account_number):  # Account Identifier
        sum_of_digits = self.sum_of_digits(account_number)
        checksum = 10 - (sum_of_digits % 10)
        if checksum == 10:
            checksum = 0
        account_number = account_number + str(checksum)
        return account_number

    @staticmethod
    def sum_of_digits(account_number):
        sum_of_digits = 0
        for i in range(len(account_number)):
            digit = int(account_number[i])
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum_of_digits += digit
        return sum_of_digits

    def check_if_exists(self, acc_number):
        return self.get_acc_data(acc_number)

    def get_acc_data(self, acc_number):
        self.cur.execute("SELECT * FROM card WHERE number = :acc_number", {"acc_number": acc_number})
        acc_data = self.cur.fetchone()
        return acc_data

    @staticmethod
    def get_credentials():
        print("Enter your card number:")
        users_number = input()
        print("Enter your PIN")
        users_pin = input()
        return users_number, users_pin

    def log_in(self, users_number, users_pin):
        self.cur.execute("SELECT * FROM card WHERE number = :num AND pin = :pin",
                    {"num": users_number, "pin": users_pin})
        acc_data = self.cur.fetchone()
        self.conn.commit()
        if acc_data is not None and self.is_account_num_valid(users_number):
            print("You have successfully logged in!")
            is_logged_in = True
        else:
            print("Wrong card number or PIN!")
            is_logged_in = False
        return is_logged_in

    def is_account_num_valid(self, account_number):
        is_number_valid = False
        sum_of_digits = self.sum_of_digits(account_number)
        if sum_of_digits % 10 == 0:
            is_number_valid = True
        return is_number_valid

    def show_logged_in_menu(self, acc_number):
        is_last_action = False
        is_logged_in = True
        while is_logged_in:
            acc_data = self.get_acc_data(acc_number)
            print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
            self.user_input = int(input())
            if self.user_input == 1:
                print(f"Balance: {acc_data[3]}")
            elif self.user_input == 2:
                income_value = int(input("Enter income:"))
                self.update_data(acc_data, income_value, "add")
                print("Income was added!")
            elif self.user_input == 3:
                self.transfer_money(acc_data)
            elif self.user_input == 4:
                self.close_account(acc_data[0])
                print("The account has been closed!")
                is_logged_in = False
            elif self.user_input == 5:
                print("You have successfully logged out!")
                is_logged_in = False
            else:
                print("Bye!")
                is_logged_in = False
                is_last_action = True
        return is_last_action

    def validate_transfer(self, senders_acc_data, receivers_card_number):
        is_card_num_correct = False
        if receivers_card_number == senders_acc_data[1]:
            print("You can't transfer money to the same account!")
        elif not self.is_account_num_valid(receivers_card_number):
            print("Probably you made mistake in the card number. Please try again!")
        receivers_acc_data = self.get_acc_data(receivers_card_number)
        if receivers_acc_data is None:
            print("Such a card does not exist.")
        else:
            is_card_num_correct = True
        return is_card_num_correct

    def transfer_money(self, senders_acc_data):
        print("Transfer")
        receivers_card_num = input("Enter card number:\n")
        is_card_num_correct = self.validate_transfer(senders_acc_data, receivers_card_num)
        receivers_acc_data = self.get_acc_data(receivers_card_num)
        if is_card_num_correct:
            money_to_transfer = int(input("Enter how much money you want to transfer:\n"))
            if money_to_transfer > senders_acc_data[3]:
                print("Not enough money!")
            else:
                self.update_data(receivers_acc_data, money_to_transfer, "add")
                self.update_data(senders_acc_data, money_to_transfer, "subtract")
                print("Success")

    def update_data(self, acc_data, money, operation):
        balance = acc_data[3]
        if operation == "add":
            balance += money
        elif operation == "subtract":
            balance -= money
        self.cur.execute("UPDATE card SET balance = :balance WHERE id = :id",
                    {"balance": balance, "id": acc_data[0]})
        self.conn.commit()

    def close_account(self, acc_id):
        self.cur.execute("DELETE FROM card WHERE id = :id",
                    {"id": acc_id})
        self.conn.commit()


def main():
    ing = BankingSystem()
    while not ing.show_main_menu():
        pass


if __name__ == "__main__":
    main()
