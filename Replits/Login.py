import sys
from replit import db

# Makes all the keys easier to access
all_users = db.keys()

def cont(cont):
  if cont == "r":
    print()
    main()
  elif cont == "e":
    print()
    print("Ok. Bye!")
    sys.exit()

def inpass(user):
  passw = input("Password Incorrect. Try again or cancel (c): ")
  if passw == db[user]:
    print("Password Correct! Welcome", user)
    sys.exit()
  elif passw == "c":
    print("Canceling")
    sys.exit()
  else:
    inpass(user)

def Login(): 
  user = input("Username: ")
  if user in all_users:
    passw = input("Account found, input password: ")
    if passw == db[user]:
      print("Password is Correct! Welcome", user)
    else:
     inpass(user)
      
      
  else:
    print("Account not found, try again")
    Login()

def Create():
  user = input("What would you like your username to be?: ")
  if user in all_users:
    print("Username taken. Resetting...")
    Create()
  else:
    passw = input("What do you want your password to be?: ")
    db[user] = passw
    if db[user] == passw:
      print("Account created succsessfully!")
      
    else:
      print("Error creating account.")

def Delete():
  sure = input("Are you sure you want to delete your account? (y/n): ")
  if sure.lower() == "y":
    user = input("Ok! What is your username (Case sensitive currently): ")
    if user in all_users:
      passw = input("What is your password?: ")
      if passw == db[user]:
        del db[user]
        print("Account Successfully Deleted.")
        
      else:
        print("Incorrrect Password. Reseting...")
        Delete()
        
    else:
      print("User not found. Resetting...")
      Delete()
  else:
    print("Ok! Ending program now...")
    sys.exit()

def Update():
  user = input("What is your username?: ")
  if user in all_users:
    cpass = input("Account Found! What is your current password?: ")
    if cpass == db[user]:
      npass = input("Correct. What is your new password?: ")
      db[user] = npass
      if db[user] == npass:
        print("Password Updated!")
        sys.exit()
      else:
        print("Error updating password. Either try again or contact the developer (ME!). ")
        sys.exit()
    else:
      inpass(user)
  else:
    print("Account not found. Try again.")
    Update()

def dev():
  print()
  print("Welcome to the developer console.")
   # Num 84 is Acess all acounts and passwords
   # Num 28 is Delete an account w/o password
   # Num 1 is exit dev console
  num = input("Number: ")
  if num == "1":
    print("Exiting...")
    sys.exit()
  elif num == "84":
    print(all_users)
    u = input("What user's password do you want?: ")
    if u in all_users:
      print(f"The password for {u} is {db[u]}")
    else:
      print("Not a valid account.")
    print()
    dev()
  elif num == "28":
    u = input("Which user do you want to delete?: ")
    del db[u]
    print("Account Deleted Succesfully")
    print()
    dev()
  elif num == "e":
    print("Goodbye")
    sys.exit()
  else:
    print("Not a valid number")
    sys.exit()

def main():
  choice = input("""Would you like to 
  1. Login
  2. Create Account
  3. Delete Account
  4. Update Password
  :  """)

  if choice == "1":
    Login()
    print()
    cont(input("Would you like to restart the process or end the program? (r/e): "))
  elif choice == "2":
    Create()
    print()
    cont(input("Would you like to restart the process or end the program? (r/e): "))
  elif choice == "3":
    Delete()
    print()
    cont(input("Would you like to restart the process or end the program? (r/e): "))
  elif choice == "4":
    Update()
    print()
    cont(input("Would you like to restart the process or end the program? (r/e): "))
  elif choice == "752":
    dev()
    print()
  else:
    print("Not a choice")
    print()
    cont(input("Would you like to restart the process or end the program? (r/e): "))

main()
