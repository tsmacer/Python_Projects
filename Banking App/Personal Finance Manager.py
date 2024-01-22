from datetime import datetime  # Extracts current date and time
import uuid  # Generates unique user IDs
import bcrypt #  Hashes passwords
from utility import UserAlreadyExistsError, AuthenticationError, InvalidTransactionError, InsufficientFundsError, \
    UnauthorizedError, hash_password


# Defining a class named "AuthenticationService" which functions have been initiated to handle user authentication
# including registration, login, and logout
class AuthenticationService:
    def __init__(self):
        self.users = {}  # Key: username, Value: User

    # Registers new user and adds to user dictionary
    def register_user(self, username, password):
        if username in self.users:
            # Imported from utility, raising an exception if user exists already
            raise UserAlreadyExistsError(f"Username '{username}' already exists")
        # Hashing password before storing it for security
        hashed_password = hash_password(password)
        self.users[username] = User(username, hashed_password)

    # Defining login function for authenticating the user by checking username & password, then authenticate (if correct).
    def login(self, username, password):
        user = self.users.get(username)
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash):
            raise AuthenticationError("Invalid username or password")
        user.is_authenticated = True
        return True

    # Defining log out function if the authentication function is False.
    def logout(self, username):
        user = self.users.get(username)
        if user:
            user.is_authenticated = False


# Basic user class with username, hashed password and authentication status
class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.is_authenticated = False


# Define the class to manage the transactions and retrieve based on date
class TransactionManager:
    def __init__(self):
        # Stores transactions for each account
        self.transactions = {}  # Key: account_id, Value: list of transactions

    # Adding new transaction to the account's transaction list
    def add_transaction(self, account_id, amount, type, current_balance):
        transaction = {
            'id': uuid.uuid4(),
            'date': datetime.now(),
            'type': type,
            'amount': amount,
            'account_id': account_id,
            'balance': current_balance
        }
        if account_id not in self.transactions:
            self.transactions[account_id] = []
        self.transactions[account_id].append(transaction)

    # Retrieving the transaction with specific date range
    def get_transactions_for_account(self, account_id, start_date, end_date):
        account_transactions = self.transactions.get(account_id, [])
        return [transaction for transaction in account_transactions
                if start_date <= transaction['date'] <= end_date]


# Defining the account class with banking functions such as account initialisation, add transaction, deposit,
# get balance (balance enquiry) withdrawal, applying interest rates, withdraw for expense, and print statement
class Account:
    # Account initialisation
    def __init__(self, user, name, transaction_manager, account_type='checking', balance=0, interest_rate=0):
        self.user = user
        self.id = uuid.uuid4()
        self.name = name
        self.account_type = account_type
        self.balance = balance
        self.interest_rate = float(interest_rate)
        self.budget = Budget(user)
        self.transaction_manager = transaction_manager

    def _add_transaction(self, amount, type):
        self.transaction_manager.add_transaction(self.id, amount, type, self.balance)

    # Deposit money and records it
    def deposit(self, amount):
        if amount <= 0:
            raise InvalidTransactionError("Amount must be greater than 0")
        self.balance += amount
        self._add_transaction(amount, "deposit")
        return self.balance

    # Withdraw money and records it
    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidTransactionError("Amount must be greater than 0")
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds")
        self.balance -= amount
        self._add_transaction(-amount, "withdrawal")
        return self.balance

    def get_balance(self):
        return self.balance

    # Applying interest if saving account
    def apply_interest(self):
        if self.account_type == 'savings':
            interest = self.balance * (self.interest_rate / 100)
            self.deposit(interest)

    # Expense withdraw and record it in budgets and specific category
    def withdraw_for_expense(self, amount, category):
        if not self.user.is_authenticated:
            raise PermissionError("User not authenticated")
        try:
            self.withdraw(amount)
            self.budget.record_expense(category, amount)
        except ValueError as e:
            print(f"Transaction failed: {e}")

    def generate_statement(self, start_date, end_date):
        # Retrieving all transactions related to the account's ID between a specific date
        statement_transactions = self.transaction_manager.get_transactions_for_account(self.id, start_date, end_date)

        # Format the statement for printing
        formatted_statement = "Account Statement for {}: {}\n".format(self.name, self.id)
        formatted_statement += "Period: {} to {}\n".format(start_date.strftime("%Y-%m-%d"),
                                                           end_date.strftime("%Y-%m-%d"))
        formatted_statement += "--------------------------------------\n"
        # Headers and alignment (left alignment)
        formatted_statement += "{:<20} {:<10} {:<15} {:<10}\n".format("Date", "Type", "Amount", "Balance")
        formatted_statement += "--------------------------------------\n"

        # Iteration through transactions and adding them to the print statement
        for transaction in statement_transactions:
            # Left alignment and 2 d.p. floats
            formatted_statement += "{:<20} {:<10} {:<15.2f} {:<10.2f}\n".format(
                transaction['date'].strftime("%Y-%m-%d %H:%M:%S"),
                transaction['type'],
                transaction['amount'],
                transaction['balance']
            )

        return formatted_statement


# Defining budget class for different categories
class Budget:
    def __init__(self, user):
        self.user = user
        self.categories = {}  # Budget categories

    def add_category(self, name, budget):
        if not self.user.is_authenticated:
            raise UnauthorizedError("User not authenticated")
        self.categories[name] = {'budget': budget, 'expenses': 0}

    def remove_category(self, name):
        if name in self.categories:
            del self.categories[name]

    def update_budget(self, name, budget):
        if name in self.categories:
            self.categories[name]['budget'] = budget

    # Records an expense against a specific category's budget
    def record_expense(self, category, amount):
        if category in self.categories and amount <= self.categories[category]['budget'] - self.categories[category][
            'expenses']:
            self.categories[category]['expenses'] += amount
        else:
            raise ValueError("Expense exceeds budget limit or category not found")

    # Get summary for a specific budget category
    def get_category_summary(self, category):
        if category in self.categories:
            budget = self.categories[category]['budget']
            expenses = self.categories[category]['expenses']
            remaining = budget - expenses
            return f"Category: {category}, Budget: {budget}, Expenses: {expenses}, Remaining: {remaining}"
        else:
            return "Category not found"

    # Get overall summary of all budget categories
    def get_overall_summary(self):
        summary = "Budget Summary:\n"
        for category, details in self.categories.items():
            summary += f"{category} - Budget: {details['budget']}, Spent: {details['expenses']}, Remaining: {details['budget'] - details['expenses']}\n"
        return summary


# Function for running the application.
def main():
    auth_service = AuthenticationService()

    # Registering new user
    try:
        auth_service.register_user("kin", "password123")
    except UserAlreadyExistsError as e:
        print(f"Registration failed: {e}")

    # Input for login
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Login operation
    try:
        if auth_service.login(username, password):
            print("Login successful")

            # Account and user setup
            user = auth_service.users[username]
            transaction_manager = TransactionManager()
            account = Account(user, "My Savings Account", transaction_manager, account_type='savings', balance=1000,
                              interest_rate=1.5)
            budget = Budget(user)

            # Operations utilising different methods
            account.budget.add_category("Groceries", 300)
            account.budget.add_category("Utilities", 200)
            account.deposit(500)
            account.withdraw(200)
            account.withdraw_for_expense(150, "Groceries")  # Expense for Groceries
            account.apply_interest()
            print(account.generate_statement(datetime(2024, 1, 1), datetime(2025, 1, 1)))

            # Print account balance and budget summary
            print(f"Account Balance: {account.get_balance()}")
            print(account.budget.get_overall_summary())
        else:
            print("Login failed")
    except AuthenticationError as e:
        print(f"Login failed: {e}")


if __name__ == "__main__":
    main()
