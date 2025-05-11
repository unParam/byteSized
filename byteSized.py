import mysql.connector
import webbrowser
from decimal import Decimal

# Connect to the MySQL database
def connect_to_database():
    try:
        conn = mysql.connector.connect(host="localhost", user="", password="", database="bytesized")
        print("Connected to the database")
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to the database:", e)
        return None


def login(conn):
    try:
        print("-" * 60)
        print("Login")
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if user:
            if user["Status"] == 'Blocked':
                print("Your account is currently blocked. Please contact support for assistance.")
            elif user["Status"] == 'Active' and user["Password"] == password:
                print("Login successful!")
                cursor.close()
                user_home(conn, user["User_ID"])
            else:
                print("Invalid email or password. Please try again.")
        else:
            print("Invalid email or password. Please try again.")

    except mysql.connector.Error as e:
        print("Error logging in:", e)

    finally:
        cursor.close()

def signup(conn):
    try:
        print("-"*60)
        print("Sign Up")
        name = input("Enter your name: ").strip()
        phone_number = input("Enter your phone number: ").strip()
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()

        cursor = conn.cursor()

        # Check if a transaction is already in progress
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Check if the email already exists in the database
        cursor.execute("SELECT COUNT(*) FROM users WHERE Email = %s", (email,))
        result = cursor.fetchone()

        if result[0] > 0:
            print("User with this email already exists. Please try again.")
            return

        # Insert the user into the Users table
        cursor.execute("INSERT INTO Users (Name, Phone_No, Email, Password) VALUES (%s, %s, %s, %s)",
                       (name, phone_number, email, password))

        # Commit the transaction
        conn.commit()
        print("User successfully registered.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error registering user:", e)

    finally:
        cursor.close()

def login_as_admin(conn):
    try:
        print("-"*60)
        print("Admin Login")
        admin_username = "admin"
        admin_password = "root"

        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        if username == admin_username and password == admin_password:
            print("Admin login successful!")
            admin_home(conn)
        else:
            print("Invalid username or password. Please try again.")

    except Exception as e:
        print("Error logging in as admin:", e)

def admin_home(conn):
    try:
        while True:
            print("-" * 60)
            print("Admin Home\n")
            print("1 Manage Users")
            print("2 Manage Content")
            print("3 Report and Analytics")
            print("X Logout")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "1":
                admin_manage_users(conn)
            elif choice == "2":
                admin_manage_content(conn)
            elif choice == "3":
                report_and_analytics(conn)
            elif choice == "X":
                print("Logging out from admin account.")
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except Exception as e:
        print("Error in admin home:", e)

def admin_manage_users(conn):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Display all users
            cursor.execute("SELECT User_ID, Name, Email FROM Users")
            users = cursor.fetchall()

            print("-" * 60)
            print("Users\n")
            for user in users:
                print(f"{user['User_ID']:<5} {user['Name']:<20} {user['Email']}")

            print("\nS Search User")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == 'S':
                while True:
                    search_query = input("Enter username or email or phone to search: ").strip()
                    cursor.execute("SELECT User_ID, Name, Email FROM Users WHERE Name LIKE %s OR Email LIKE %s or Phone_No LIKE %s", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
                    search_results = cursor.fetchall()

                    if search_results:
                        print("-" * 60)
                        print("Search Results\n")
                        for user in search_results:
                            print(f"{user['User_ID']:<5} {user['Name']:<20} {user['Email']}")
                        print("\nX Back")

                        subchoice = input("Enter your choice: ").strip().upper()
                        if subchoice.isdigit():
                            userID = int(subchoice)
                            cursor.execute("SELECT COUNT(*) FROM Users WHERE User_ID = %s AND (Name LIKE %s OR Email LIKE %s or Phone_No LIKE %s)", (userID, f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
                            user_exists = cursor.fetchone()['COUNT(*)']
                            if user_exists:
                                admin_view_user(conn, userID)
                                break
                            else:
                                print("Invalid choice. Please enter a valid option.")           
                        elif subchoice == 'X':
                            break
                        else:
                            print("Invalid choice. Please enter a valid option.")

                    else:
                        print("No users found matching the search criteria.")
            elif choice.isdigit():
                userID = int(choice)
                cursor.execute("SELECT COUNT(*) FROM Users WHERE User_ID = %s", (userID,))
                user_exists = cursor.fetchone()['COUNT(*)']
                # print("user_exists: ",user_exists)
                if user_exists:
                    admin_view_user(conn, userID)
                else:
                    print("User not found.")
                            
            elif choice == 'X':
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing users:", e)
    finally:
        cursor.close()

def admin_view_user(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        while True:
            # Retrieve user information from the database
            cursor.execute("SELECT * FROM Users WHERE User_ID = %s", (userID,))
            user = cursor.fetchone()

            if user:
                print("-" * 60)
                print("User Information\n")
                print(f"Name: {user['Name']}")
                print(f"Phone Number: {user['Phone_No']}")
                print(f"Email: {user['Email']}")
                print(f"Password: {user['Password']}")
                print(f"Balance: ${user['Balance']:.2f}")
                print(f"Status: {user['Status']}")

                print("\n1 Modify user information")
                print("2 View user library")
                print("3 View user cart")
                print("4 Block user")
                print("5 Unblock user")
                print("6 Delete user")
                print("X Back")

                choice = input("Enter your choice: ").strip().upper()

                if choice == "1":
                    # Modify user information
                    admin_modify_user_info(conn, userID)
                elif choice == "2":
                    # View user library
                    admin_view_user_library(conn, userID)
                elif choice == "3":
                    # View user cart
                    admin_view_user_cart(conn, userID)
                elif choice == "4":
                    # Block user
                    admin_block_user(conn, userID)
                elif choice == "5":
                    # Unblock user
                    admin_unblock_user(conn, userID)
                elif choice == "6":
                    # Delete user
                    admin_delete_user(conn, userID)
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("User not found.")
                break

    except mysql.connector.Error as e:
        print("Error viewing user information:", e)

    finally:
        cursor.close()

def admin_modify_user_info(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            cursor.execute("SELECT * FROM Users WHERE User_ID = %s", (userID,))
            user = cursor.fetchone()

            if user:
                print("-" * 60)
                print("User Information\n")
                print(f"1 Name: {user['Name']}")
                print(f"2 Phone Number: {user['Phone_No']}")
                print(f"3 Email: {user['Email']}")
                print(f"4 Password: {user['Password']}")
                print(f"5 Balance: ${user['Balance']:.2f}")
                print(f"6 Status: {user['Status']}")
                print("X Back")
            
                print("Select the field you want to modify (1-6) or X to go back: ")
                choice = input("Enter your choice: ").strip().upper()
                
                if choice in ["1", "2", "3", "4", "5", "6"]:
                    field_index = int(choice)
                    new_value = input(f"Enter the new value for field: ").strip()
                    # Update the user information
                    update_field = ["Name", "Phone_No", "Email", "Password", "Balance", "Status"][field_index - 1]
                    if not conn.in_transaction:
                        # Start a transaction
                        conn.start_transaction()
                    cursor.execute(f"UPDATE Users SET {update_field} = %s WHERE User_ID = %s", (new_value, userID))
                    conn.commit()

                    print("User information updated successfully.")
                    break
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("User not found.")

    except mysql.connector.Error as e:
        print("Error modifying user information:", e)

    finally:
        cursor.close()

def admin_view_user_library(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve purchased games
            cursor.execute("SELECT Games.Game_ID, Title FROM Games INNER JOIN Library_Games ON Games.Game_ID = Library_Games.Game_ID WHERE User_ID = %s", (userID,))
            games = cursor.fetchall()
            game_list = list(enumerate(games))

            # Retrieve purchased movies
            cursor.execute("SELECT Movies.Movie_ID, Title FROM Movies INNER JOIN Library_Movies ON Movies.Movie_ID = Library_Movies.Movie_ID WHERE User_ID = %s", (userID,))
            movies = cursor.fetchall()
            movie_list = list(enumerate(movies))

            # Retrieve purchased web series
            cursor.execute("SELECT Series.Series_ID, Title FROM Series INNER JOIN Library_WebSeries ON Series.Series_ID = Library_WebSeries.Series_ID WHERE User_ID = %s", (userID,))
            webseries = cursor.fetchall()
            series_list = list(enumerate(webseries))
            
        
            print("-" * 60)
            print("Library")
            if((game_list + movie_list + series_list) == []):
                print("\nLibrary is empty")
                return
            print("\nGames:")
            for game in game_list:
                print(f"{game[0]+1:<5}{game[1]['Title']:<50}")

            print("\nMovies:")
            for movie in movie_list:
                print(f"{movie[0]+1:<5} {movie[1]['Title']:<50}")

            print("\nWeb Series:")
            for series in series_list:
                print(f"{series[0]+1:<5} {series[1]['Title']:<50}")
            
            print("\nC Clear Library")
            print("X Back")
            choice = input("Enter your choice: ").strip().upper()
            if choice == "C":
                clear_library(conn, userID)
            elif choice == "X":
                    break
            else:
                print("Invalid choice. Please enter a valid option.")
    except mysql.connector.Error as e:
        print("Error retrieving library:", e)

    finally:
        cursor.close() 

def admin_view_user_cart(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        while True:
            # Retrieve games in the cart
            cursor.execute("SELECT Games.Game_ID, Title, Price FROM Games INNER JOIN Cart_Games ON Games.Game_ID = Cart_Games.Game_ID WHERE User_ID = %s", (userID,))
            games = cursor.fetchall()
            game_list = list(enumerate(games))

            # Retrieve movies in the cart
            cursor.execute("SELECT Movies.Movie_ID, Title, Price FROM Movies INNER JOIN Cart_Movies ON Movies.Movie_ID = Cart_Movies.Movie_ID WHERE User_ID = %s", (userID,))
            movies = cursor.fetchall()
            movie_list = list(enumerate(movies))

            # Retrieve web series in the cart
            cursor.execute("SELECT Series.Series_ID, Title, Price FROM Series INNER JOIN Cart_WebSeries ON Series.Series_ID = Cart_WebSeries.Series_ID WHERE User_ID = %s", (userID,))
            webseries = cursor.fetchall()
            series_list = list(enumerate(webseries))

            print("-" * 60)
            print("Cart")
            total_price = 0
            if((game_list + movie_list + series_list) == []):
                print("\nCart is empty")
                return

            # Print games in cart
            if games:
                print("\nGames:")
                for game in game_list:
                    print(f"{game[0]+1:<5}{game[1]['Title']:<50} ${game[1]['Price']:.2f}")
                    total_price += game[1]['Price']

            # Print movies in cart
            if movies:
                print("\nMovies:")
                for movie in movie_list:
                    print(f"{movie[0]+1:<5} {movie[1]['Title']:<50} ${movie[1]['Price']:.2f}")
                    total_price += movie[1]['Price']

            # Print web series in cart
            if webseries:
                print("\nWeb Series:")
                for series in series_list:
                    print(f"{series[0]+1:<5} {series[1]['Title']:<50} ${series[1]['Price']:.2f}")
                    total_price += series[1]['Price']

            print(f"\nTotal Price: ${total_price:.2f}\n")

            print("R Remove Items")
            print("D Clear Cart")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "R":
                print("Item code: G for Games, M for Movies, W for Webseries, followed by serial number of the item e.g. 'M3'")
                query = input("Enter code of the item to be removed: ").strip().upper()
                if not isValidItemID(query):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G" and int(query[1:]) > len(game_list)) or (query[0] == "M" and int(query[1:]) > len(movie_list)) or (query[0] == "W" and int(query[1:]) > len(series_list)):
                    print("Invalid item ID.")
                    continue
                itemID = query[0]
                if(query[0] == "G"): itemID += str(game_list[int(query[1:]) - 1][1]["Game_ID"])
                elif(query[0] == "M"): itemID += str(movie_list[int(query[1:]) - 1][1]["Movie_ID"])
                elif(query[0] == "W"): itemID += str(series_list[int(query[1:]) - 1][1]["Series_ID"])
                remove_items(conn, userID, itemID)
            elif choice == "D":
                clear_cart(conn, userID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")
                
    except mysql.connector.Error as e:
        print("Error retrieving cart:", e)

    finally:
        cursor.close()

def admin_block_user(conn, userID):
    try:
        cursor = conn.cursor()

        # Check if a transaction is already in progress
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Check if the user is already blocked
        cursor.execute("SELECT Status FROM Users WHERE User_ID = %s", (userID,))
        status = cursor.fetchone()[0]
        if status == "Blocked":
            print("User is already Blocked.")
            return

        # Block the user
        cursor.execute("UPDATE Users SET Status = 'Blocked' WHERE User_ID = %s", (userID,))
        conn.commit()
        print("User blocked successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error blocking user:", e)

    finally:
        cursor.close()

def admin_unblock_user(conn, userID):
    try:
        cursor = conn.cursor()

        # Check if the user is already unblocked
        cursor.execute("SELECT Status FROM Users WHERE User_ID = %s", (userID,))
        status = cursor.fetchone()[0]
        if status == "Active":
            print("User is already Unblocked.")
            return

        # Start a transaction
        if not conn.in_transaction:
            conn.start_transaction()

        # Update the user's status to "Active"
        cursor.execute("UPDATE Users SET Status = 'Active' WHERE User_ID = %s", (userID,))

        # Commit the transaction
        conn.commit()
        print("User successfully Unblocked.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error unblocking user:", e)

    finally:
        cursor.close()

def admin_delete_user(conn, userID):
    try:
        cursor = conn.cursor()

        # Confirm deletion
        confirmation = input("Are you sure you want to delete this user? (y/Y for Yes) : ").strip().upper()
        if confirmation != "Y":
            print("Deletion cancelled.")
            return

        # Start a transaction
        if not conn.in_transaction:
            conn.start_transaction()

        # Empty user's cart
        cursor.execute("DELETE FROM Cart_Games WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Cart_Movies WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Cart_WebSeries WHERE User_ID = %s", (userID,))

        # Empty user's library
        cursor.execute("DELETE FROM Library_Games WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Library_Movies WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Library_WebSeries WHERE User_ID = %s", (userID,))

        # Delete user record
        cursor.execute("DELETE FROM Users WHERE User_ID = %s", (userID,))

        # Commit the transaction
        conn.commit()
        print("User successfully deleted.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting user:", e)

    finally:
        cursor.close()


def admin_manage_content(conn):
    try:
        while True:
            print("-" * 60)
            print("Manage Content\n")
            print("1 Games")
            print("2 Movies")
            print("3 Web Series")
            print("4 Episodes")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "1":
                admin_manage_games(conn)
            elif choice == "2":
                admin_manage_movies(conn)
            elif choice == "3":
                admin_manage_webseries(conn)
            elif choice == "4":
                admin_manage_episodes(conn)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing content:", e)

def admin_manage_games(conn):
    try:
        while True:
            print("-" * 60)
            print("Manage Games\n")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Game_ID, Title, Price FROM Games")
            games = cursor.fetchall()
            cursor.close()

            if games:
                for game in games:
                    print(f"{game['Game_ID']:<5} {game['Title']:<50} ${game['Price']}")
            else:
                print("No games found.")
                break

            print("\nA Add Game")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "A":
                admin_add_game(conn)
            elif choice.isdigit():
                gameID = int(choice)
                admin_view_game(conn, gameID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing games:", e)
    
def admin_add_game(conn):
    try:
        print("-" * 60)
        print("Add New Game\n")

        title = input("Enter game title: ").strip()
        category = input("Enter game category: ").strip()
        release_date = input("Enter release date (YYYY-MM-DD): ").strip()
        game_file = input("Enter game file path: ").strip()
        trailer_video = input("Enter trailer video URL: ").strip()
        description = input("Enter game description: ").strip()
        price = float(input("Enter game price: "))
        age_rating = input("Enter age rating (E, E10+, T, M, AO): ").strip().upper()
        download_size = float(input("Enter download size (MB): "))
        system_requirements = input("Enter system requirements: ").strip()
        rating = float(input("Enter game rating: "))

        cursor = conn.cursor()
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        cursor.execute("""
            INSERT INTO Games (Title, Category, Release_Date, Game_File, Trailer_Video, Description,
            Price, Age_Rating, Download_Size, System_Requirements, Rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, category, release_date, game_file, trailer_video, description, price,
              age_rating, download_size, system_requirements, rating))

        conn.commit()
        print("Game added successfully.")

    except mysql.connector.Error as e:
        print("Error adding game:", e)

    finally:
        cursor.close()

def admin_view_game(conn, gameID):
    try:
        cursor = conn.cursor(dictionary=True)
        while True:
            cursor.execute("SELECT * FROM Games WHERE Game_ID = %s", (gameID,))
            game = cursor.fetchone()

            if game:
                print("-" * 60)
                print("Game Details\n")
                print(f"Game ID: {game['Game_ID']}")
                print(f"Title: {game['Title']}")
                print(f"Category: {game['Category']}")
                print(f"Release Date: {game['Release_Date']}")
                print(f"Game File: {game['Game_File']}")
                print(f"Trailer Video: {game['Trailer_Video']}")
                print(f"Description: {game['Description']}")
                print(f"Price: ${game['Price']:.2f}")
                print(f"Age Rating: {game['Age_Rating']}")
                print(f"Download Size: {game['Download_Size']} MB")
                print(f"System Requirements: {game['System_Requirements']}")
                print(f"Rating: {game['Rating']}")

                print("\n1 Modify Game Info")
                print("2 Delete Game")
                print("X Back")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    admin_modify_game_info(conn, gameID)
                elif choice == "2":
                    admin_delete_game(conn, gameID)
                    break
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("Game not found.")

    except mysql.connector.Error as e:
        print("Error viewing game details:", e)

    finally:
        cursor.close()

def admin_modify_game_info(conn, gameID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve current game information
            cursor.execute("SELECT * FROM Games WHERE Game_ID = %s", (gameID,))
            game = cursor.fetchone()

            if game:
                print("-" * 60)
                print("Game Information\n")
                print(f"1. Title: {game['Title']}")
                print(f"2. Category: {game['Category']}")
                print(f"3. Release Date: {game['Release_Date']}")
                print(f"4. Game File: {game['Game_File']}")
                print(f"5. Trailer Video: {game['Trailer_Video']}")
                print(f"6. Description: {game['Description']}")
                print(f"7. Price: ${game['Price']:.2f}")
                print(f"8. Age Rating: {game['Age_Rating']}")
                print(f"9. Download Size: {game['Download_Size']} MB")
                print(f"10. System Requirements: {game['System_Requirements']}")
                print(f"11. Rating: {game['Rating']}")
                print("X Back")
            
                choice = input("Enter the number of the field you want to modify (or 'X' to go back): ").strip()

                if choice.upper() == "X":
                    break

                if choice.isdigit():
                    field_num = int(choice)
                    if 1 <= field_num <= 11:
                        new_value = input(f"Enter new value for field: ").strip()

                        # Update the selected field in the database
                        field_names = ["Title", "Category", "Release_Date", "Game_File", "Trailer_Video",
                                       "Description", "Price", "Age_Rating", "Download_Size", "System_Requirements", "Rating"]
                        field_name = field_names[field_num - 1]
                        if not conn.in_transaction:
                            # Start a transaction
                            conn.start_transaction()
                        cursor.execute(f"UPDATE Games SET {field_name} = %s WHERE Game_ID = %s", (new_value, gameID))
                        conn.commit()
                        print("Game information updated successfully.")
                        break
                    else:
                        print("Invalid field number. Please enter a number between 1 and 11.")
                else:
                    print("Invalid input. Please enter a number or 'X' to go back.")

            else:
                print("Game not found.")

    except mysql.connector.Error as e:
        print("Error modifying game information:", e)

    finally:
        cursor.close()

def admin_delete_game(conn, gameID):
    try:
        cursor = conn.cursor()

        confirmation = input("Are you sure you want to delete this game? (y/Y for yes): ").strip().upper()

        if confirmation != "Y":
            print("Deletion cancelled.")
            return
        
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Delete the game from the carts
        cursor.execute("DELETE FROM Cart_Games WHERE Game_ID = %s", (gameID,))

        # Delete the game from the library
        cursor.execute("DELETE FROM Library_Games WHERE Game_ID = %s", (gameID,))

        # Delete the game from the Games table
        cursor.execute("DELETE FROM Games WHERE Game_ID = %s", (gameID,))

        # Commit the transaction
        conn.commit()

        print("Game deleted successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting game:", e)

    finally:
        cursor.close()


def admin_manage_movies(conn):
    try:
        while True:
            print("-" * 60)
            print("Manage Movies\n")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Movie_ID, Title, Price FROM Movies")
            movies = cursor.fetchall()
            cursor.close()

            if movies:
                for movie in movies:
                    print(f"{movie['Movie_ID']: <5} {movie['Title']: <50} ${movie['Price']}")
            else:
                print("No movies found.")
                break

            print("\nA Add Movie")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "A":
                admin_add_movie(conn)
            elif choice.isdigit():
                movieID = int(choice)
                admin_view_movie(conn, movieID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing movies:", e)

def admin_add_movie(conn):
    try:
        print("-" * 60)
        print("Add New Movie\n")

        title = input("Enter movie title: ").strip()
        production_studio = input("Enter production studio: ").strip()
        age_rating = input("Enter age rating (G, PG, PG-13, R, NC-17): ").strip().upper()
        trailer_video = input("Enter trailer video URL: ").strip()
        release_date = input("Enter release date (YYYY-MM-DD): ").strip()
        genre = input("Enter genre: ").strip()
        download_size = float(input("Enter download size (MB): "))
        rating = float(input("Enter movie rating: "))
        movie_file = input("Enter movie file path: ").strip()
        description = input("Enter movie description: ").strip()
        cast_crew = input("Enter cast and crew: ").strip()
        price = float(input("Enter movie price: "))
        runtime = int(input("Enter movie runtime (minutes): "))
        languages = input("Enter languages: ").strip()

        cursor = conn.cursor()
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        cursor.execute("""
            INSERT INTO Movies (Title, Production_Studio, Age_Rating, Trailer_Video, Release_Date, Genre,
            Download_Size, Rating, Movie_File, Description, Cast_Crew, Price, Runtime, Languages)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, production_studio, age_rating, trailer_video, release_date, genre,
              download_size, rating, movie_file, description, cast_crew, price, runtime, languages))

        conn.commit()
        print("Movie added successfully.")

    except mysql.connector.Error as e:
        print("Error adding movie:", e)

    finally:
        cursor.close()

def admin_view_movie(conn, movieID):
    try:
        cursor = conn.cursor(dictionary=True)
        while True:
            cursor.execute("SELECT * FROM Movies WHERE Movie_ID = %s", (movieID,))
            movie = cursor.fetchone()

            if movie:
                print("-" * 60)
                print("Movie Details\n")
                print(f"Movie ID: {movie['Movie_ID']}")
                print(f"Title: {movie['Title']}")
                print(f"Production Studio: {movie['Production_Studio']}")
                print(f"Age Rating: {movie['Age_Rating']}")
                print(f"Trailer Video: {movie['Trailer_Video']}")
                print(f"Release Date: {movie['Release_Date']}")
                print(f"Genre: {movie['Genre']}")
                print(f"Download Size: {movie['Download_Size']} MB")
                print(f"Rating: {movie['Rating']}")
                print(f"Movie File: {movie['Movie_File']}")
                print(f"Description: {movie['Description']}")
                print(f"Cast/Crew: {movie['Cast_Crew']}")
                print(f"Price: ${movie['Price']:.2f}")
                print(f"Runtime: {movie['Runtime']} minutes")
                print(f"Languages: {movie['Languages']}")

                print("\n1 Modify Movie Info")
                print("2 Delete Movie")
                print("X Back")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    admin_modify_movie_info(conn, movieID)
                elif choice == "2":
                    admin_delete_movie(conn, movieID)
                    break
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("Movie not found.")

    except mysql.connector.Error as e:
        print("Error viewing movie details:", e)

    finally:
        cursor.close()

def admin_modify_movie_info(conn, movieID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve current movie information
            cursor.execute("SELECT * FROM Movies WHERE Movie_ID = %s", (movieID,))
            movie = cursor.fetchone()

            if movie:
                print("-" * 60)
                print("Movie Information\n")
                print(f"1. Title: {movie['Title']}")
                print(f"2. Production Studio: {movie['Production_Studio']}")
                print(f"3. Age Rating: {movie['Age_Rating']}")
                print(f"4. Trailer Video: {movie['Trailer_Video']}")
                print(f"5. Release Date: {movie['Release_Date']}")
                print(f"6. Genre: {movie['Genre']}")
                print(f"7. Download Size: {movie['Download_Size']} MB")
                print(f"8. Rating: {movie['Rating']}")
                print(f"9. Movie File: {movie['Movie_File']}")
                print(f"10. Description: {movie['Description']}")
                print(f"11. Cast/Crew: {movie['Cast_Crew']}")
                print(f"12. Price: ${movie['Price']:.2f}")
                print(f"13. Runtime: {movie['Runtime']} minutes")
                print(f"14. Languages: {movie['Languages']}")
                print("X Back")

                choice = input("Enter the number of the field you want to modify (or 'X' to go back): ").strip()

                if choice.upper() == "X":
                    break

                if choice.isdigit():
                    field_num = int(choice)
                    if 1 <= field_num <= 14:
                        new_value = input(f"Enter new value for field: ").strip()

                        # Update the selected field in the database
                        field_names = ["Title", "Production_Studio", "Age_Rating", "Trailer_Video",
                                       "Release_Date", "Genre", "Download_Size", "Rating", "Movie_File",
                                       "Description", "Cast_Crew", "Price", "Runtime", "Languages"]
                        field_name = field_names[field_num - 1]
                        if not conn.in_transaction:
                            # Start a transaction
                            conn.start_transaction()
                        cursor.execute(f"UPDATE Movies SET {field_name} = %s WHERE Movie_ID = %s", (new_value, movieID))
                        conn.commit()
                        print("Movie information updated successfully.")
                        break
                    else:
                        print("Invalid field number. Please enter a number between 1 and 14.")
                else:
                    print("Invalid input. Please enter a number or 'X' to go back.")

            else:
                print("Movie not found.")

    except mysql.connector.Error as e:
        print("Error modifying movie information:", e)

    finally:
        cursor.close()

def admin_delete_movie(conn, movieID):
    try:
        cursor = conn.cursor()

        confirmation = input("Are you sure you want to delete this movie? (y/Y for yes): ").strip().upper()

        if confirmation != "Y":
            print("Deletion cancelled.")
            return
        
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Delete the movie from the carts
        cursor.execute("DELETE FROM Cart_Movies WHERE Movie_ID = %s", (movieID,))

        # Delete the movie from the library
        cursor.execute("DELETE FROM Library_Movies WHERE Movie_ID = %s", (movieID,))

        # Delete the movie from the Movies table
        cursor.execute("DELETE FROM Movies WHERE Movie_ID = %s", (movieID,))

        # Commit the transaction
        conn.commit()

        print("Movie deleted successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting movie:", e)

    finally:
        cursor.close()


def admin_manage_webseries(conn):
    try:
        while True:
            print("-" * 60)
            print("Manage Web Series\n")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Series_ID, Title, Price FROM Series")
            series = cursor.fetchall()
            cursor.close()

            if series:
                for webseries in series:
                    print(f"{webseries['Series_ID']: <5} {webseries['Title']: <50} ${webseries['Price']}")
            else:
                print("No web series found.")
                break

            print("\nA Add Web Series")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "A":
                admin_add_webseries(conn)
            elif choice.isdigit():
                seriesID = int(choice)
                admin_view_webseries(conn, seriesID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing web series:", e)

def admin_add_webseries(conn):
    try:
        print("-" * 60)
        print("Add New Web Series\n")

        title = input("Enter web series title: ").strip()
        production_studio = input("Enter production studio: ").strip()
        age_rating = input("Enter age rating (G, PG, PG-13, R): ").strip().upper()
        trailer_video = input("Enter trailer video URL: ").strip()
        release_date = input("Enter release date (YYYY-MM-DD): ").strip()
        genre = input("Enter genre: ").strip()
        download_size = float(input("Enter download size (MB): "))
        rating = float(input("Enter web series rating: "))
        description = input("Enter web series description: ").strip()
        cast_crew = input("Enter cast and crew: ").strip()
        price = float(input("Enter web series price: "))
        languages = input("Enter languages: ").strip()

        cursor = conn.cursor()
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        cursor.execute("""
            INSERT INTO Series (Title, Production_Studio, Age_Rating, Trailer_Video, Release_Date, Genre,
            Download_Size, Rating, Description, Cast_Crew, Price, Languages)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, production_studio, age_rating, trailer_video, release_date, genre,
              download_size, rating, description, cast_crew, price, languages))

        conn.commit()
        print("Web series added successfully.")

    except mysql.connector.Error as e:
        print("Error adding web series:", e)

    finally:
        cursor.close()

def admin_view_webseries(conn, seriesID):
    try:
        cursor = conn.cursor(dictionary=True)
        while True:
            cursor.execute("SELECT * FROM Series WHERE Series_ID = %s", (seriesID,))
            webseries = cursor.fetchone()

            if webseries:
                print("-" * 60)
                print("Web Series Details\n")
                print(f"Series ID: {webseries['Series_ID']}")
                print(f"Title: {webseries['Title']}")
                print(f"Production Studio: {webseries['Production_Studio']}")
                print(f"Age Rating: {webseries['Age_Rating']}")
                print(f"Trailer Video: {webseries['Trailer_Video']}")
                print(f"Release Date: {webseries['Release_Date']}")
                print(f"Genre: {webseries['Genre']}")
                print(f"Download Size: {webseries['Download_Size']} MB")
                print(f"Rating: {webseries['Rating']}")
                print(f"Description: {webseries['Description']}")
                print(f"Cast/Crew: {webseries['Cast_Crew']}")
                print(f"Price: ${webseries['Price']:.2f}")
                print(f"Languages: {webseries['Languages']}")

                print("\n1 Modify Web Series Info")
                print("2 Delete Web Series")
                print("X Back")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    admin_modify_webseries_info(conn, seriesID)
                elif choice == "2":
                    admin_delete_webseries(conn, seriesID)
                    break
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("Web series not found.")

    except mysql.connector.Error as e:
        print("Error viewing web series details:", e)

    finally:
        cursor.close()

def admin_modify_webseries_info(conn, seriesID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve current web series information
            cursor.execute("SELECT * FROM Series WHERE Series_ID = %s", (seriesID,))
            webseries = cursor.fetchone()

            if webseries:
                print("-" * 60)
                print("Web Series Information\n")
                print(f"1. Title: {webseries['Title']}")
                print(f"2. Production Studio: {webseries['Production_Studio']}")
                print(f"3. Age Rating: {webseries['Age_Rating']}")
                print(f"4. Trailer Video: {webseries['Trailer_Video']}")
                print(f"5. Release Date: {webseries['Release_Date']}")
                print(f"6. Genre: {webseries['Genre']}")
                print(f"7. Download Size: {webseries['Download_Size']} MB")
                print(f"8. Rating: {webseries['Rating']}")
                print(f"9. Description: {webseries['Description']}")
                print(f"10. Cast/Crew: {webseries['Cast_Crew']}")
                print(f"11. Price: ${webseries['Price']:.2f}")
                print(f"12. Languages: {webseries['Languages']}")
                print("X Back")
            
                choice = input("Enter the number of the field you want to modify (or 'X' to go back): ").strip()

                if choice.upper() == "X":
                    break

                if choice.isdigit():
                    field_num = int(choice)
                    if 1 <= field_num <= 12:
                        new_value = input(f"Enter new value for field: ").strip()

                        # Update the selected field in the database
                        field_names = ["Title", "Production_Studio", "Age_Rating", "Trailer_Video",
                                       "Release_Date", "Genre", "Download_Size", "Rating", "Description",
                                       "Cast_Crew", "Price", "Languages"]
                        field_name = field_names[field_num - 1]
                        if not conn.in_transaction:
                            # Start a transaction
                            conn.start_transaction()
                        cursor.execute(f"UPDATE Series SET {field_name} = %s WHERE Series_ID = %s", (new_value, seriesID))
                        conn.commit()
                        print("Web series information updated successfully.")
                        break
                    else:
                        print("Invalid field number. Please enter a number between 1 and 12.")
                else:
                    print("Invalid input. Please enter a number or 'X' to go back.")

            else:
                print("Web series not found.")

    except mysql.connector.Error as e:
        print("Error modifying web series information:", e)

    finally:
        cursor.close()

def admin_delete_webseries(conn, seriesID):
    try:
        cursor = conn.cursor()

        confirmation = input("Are you sure you want to delete this web series? (y/Y for yes): ").strip().upper()

        if confirmation != "Y":
            print("Deletion cancelled.")
            return
        
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Delete the web series from the carts
        cursor.execute("DELETE FROM Cart_WebSeries WHERE Series_ID = %s", (seriesID,))

        # Delete the web series from the library
        cursor.execute("DELETE FROM Library_WebSeries WHERE Series_ID = %s", (seriesID,))

        # Delete the web series from the Series table
        cursor.execute("DELETE FROM Series WHERE Series_ID = %s", (seriesID,))

        # Commit the transaction
        conn.commit()

        print("Web series deleted successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting web series:", e)

    finally:
        cursor.close()


def admin_manage_episodes(conn):
    try:
        while True:
            print("-" * 60)
            print("Manage Episodes\n")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Episode_ID, Title, Episode_number FROM Episodes")
            episodes = cursor.fetchall()
            cursor.close()

            if episodes:
                for episode in episodes:
                    print(f"{episode['Episode_ID']: <5} {episode['Title']: <50} Episode Number: {episode['Episode_number']}")
            else:
                print("No episodes found.")
                break

            print("\nA Add Episode")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "A":
                admin_add_episode(conn)
            elif choice.isdigit():
                episodeID = int(choice)
                admin_view_episode(conn, episodeID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error managing episodes:", e)

def admin_add_episode(conn):
    try:
        print("-" * 60)
        print("Add New Episode\n")
        
        ep_ID = int(input("Enter episode ID: ").strip())
        series_id = int(input("Enter series ID: ").strip())
        title = input("Enter episode title: ").strip()
        episode_number = int(input("Enter episode number: ").strip())
        duration_minutes = int(input("Enter episode duration (minutes): ").strip())
        release_date = input("Enter release date (YYYY-MM-DD): ").strip()

        cursor = conn.cursor()
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        cursor.execute("""
            INSERT INTO Episodes (Episode_ID, Series_ID, Title, Episode_number, Duration_minutes, Release_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ep_ID, series_id, title, episode_number, duration_minutes, release_date))

        conn.commit()
        print("Episode added successfully.")

    except mysql.connector.Error as e:
        print("Error adding episode:", e)

    finally:
        cursor.close()

def admin_view_episode(conn, episodeID):
    try:
        cursor = conn.cursor(dictionary=True)
        while True:
            cursor.execute("SELECT * FROM Episodes WHERE Episode_ID = %s", (episodeID,))
            episode = cursor.fetchone()

            if episode:
                print("-" * 60)
                print("Episode Details\n")
                print(f"Episode ID: {episode['Episode_ID']}")
                print(f"Series ID: {episode['Series_ID']}")
                print(f"Title: {episode['Title']}")
                print(f"Episode Number: {episode['Episode_number']}")
                print(f"Duration (minutes): {episode['Duration_minutes']}")
                print(f"Release Date: {episode['Release_date']}")

                print("\n1 Modify Episode Info")
                print("2 Delete Episode")
                print("X Back")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    admin_modify_episode_info(conn, episodeID)
                elif choice == "2":
                    admin_delete_episode(conn, episodeID)
                    break
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

            else:
                print("Episode not found.")

    except mysql.connector.Error as e:
        print("Error viewing episode details:", e)

    finally:
        cursor.close()

def admin_modify_episode_info(conn, episodeID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve current episode information
            cursor.execute("SELECT * FROM Episodes WHERE Episode_ID = %s", (episodeID,))
            episode = cursor.fetchone()

            if episode:
                print("-" * 60)
                print("Episode Information\n")
                print(f"1. Series ID: {episode['Series_ID']}")
                print(f"2. Title: {episode['Title']}")
                print(f"3. Episode Number: {episode['Episode_number']}")
                print(f"4. Duration (minutes): {episode['Duration_minutes']}")
                print(f"5. Release Date: {episode['Release_date']}")
                print("X Back")
            
                choice = input("Enter the number of the field you want to modify (or 'X' to go back): ").strip()

                if choice.upper() == "X":
                    break

                if choice.isdigit():
                    field_num = int(choice)
                    if 1 <= field_num <= 5:
                        new_value = input(f"Enter new value for field: ").strip()

                        # Update the selected field in the database
                        field_names = ["Series_ID", "Title", "Episode_number", "Duration_minutes", "Release_date"]
                        field_name = field_names[field_num - 1]
                        if not conn.in_transaction:
                            # Start a transaction
                            conn.start_transaction()
                        cursor.execute(f"UPDATE Episodes SET {field_name} = %s WHERE Episode_ID = %s", (new_value, episodeID))
                        conn.commit()
                        print("Episode information updated successfully.")
                        break
                    else:
                        print("Invalid field number. Please enter a number between 1 and 5.")
                else:
                    print("Invalid input. Please enter a number or 'X' to go back.")

            else:
                print("Episode not found.")

    except mysql.connector.Error as e:
        print("Error modifying episode information:", e)

    finally:
        cursor.close()

def admin_delete_episode(conn, episodeID):
    try:
        cursor = conn.cursor()

        confirmation = input("Are you sure you want to delete this episode? (y/Y for yes): ").strip().upper()

        if confirmation != "Y":
            print("Deletion cancelled.")
            return
        
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Delete the episode from the Episodes table
        cursor.execute("DELETE FROM Episodes WHERE Episode_ID = %s", (episodeID,))

        # Commit the transaction
        conn.commit()

        print("Episode deleted successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting episode:", e)

    finally:
        cursor.close()


def report_and_analytics(conn):
    try:
        cursor = conn.cursor()

        # Total number of games bought
        cursor.execute("SELECT COUNT(*) FROM Library_Games")
        total_games = cursor.fetchone()[0]

        # Total number of movies bought
        cursor.execute("SELECT COUNT(*) FROM Library_Movies")
        total_movies = cursor.fetchone()[0]

        # Total number of web series bought
        cursor.execute("SELECT COUNT(*) FROM Library_WebSeries")
        total_web_series = cursor.fetchone()[0]

        # Most purchased games
        cursor.execute("""
            SELECT Title
            FROM Games
            WHERE Game_ID IN (
                SELECT Game_ID
                FROM Library_Games
                GROUP BY Game_ID
                HAVING COUNT(*) = (
                    SELECT COUNT(*)
                    FROM Library_Games
                    GROUP BY Game_ID
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                )
            )
        """)
        most_purchased_games = cursor.fetchall()

        # Most purchased movies
        cursor.execute("""
            SELECT Title
            FROM Movies
            WHERE Movie_ID IN (
                SELECT Movie_ID
                FROM Library_Movies
                GROUP BY Movie_ID
                HAVING COUNT(*) = (
                    SELECT COUNT(*)
                    FROM Library_Movies
                    GROUP BY Movie_ID
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                )
            )
        """)
        most_purchased_movies = cursor.fetchall()

        # Most purchased web series
        cursor.execute("""
            SELECT Title
            FROM Series
            WHERE Series_ID IN (
                SELECT Series_ID
                FROM Library_WebSeries
                GROUP BY Series_ID
                HAVING COUNT(*) = (
                    SELECT COUNT(*)
                    FROM Library_WebSeries
                    GROUP BY Series_ID
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                )
            )
        """)
        most_purchased_web_series = cursor.fetchall()

        # Total sale
        cursor.execute("""
            SELECT SUM(Price)
            FROM (
                SELECT G.Price 
                FROM Games G
                JOIN Library_Games LG ON G.Game_ID = LG.Game_ID
                UNION ALL
                SELECT M.Price 
                FROM Movies M
                JOIN Library_Movies LM ON M.Movie_ID = LM.Movie_ID
                UNION ALL
                SELECT S.Price 
                FROM Series S
                JOIN Library_WebSeries LW ON S.Series_ID = LW.Series_ID
            ) AS TotalSale
        """)
        total_sale = cursor.fetchone()[0]

        cursor.close()

        # Print the results
        print("-" * 60)
        print("Report and Analytics\n")
        print("Total items bought: ", (total_games + total_movies + total_web_series))
        print("Total number of games bought:", total_games)
        print("Total number of movies bought:", total_movies)
        print("Total number of web series bought:", total_web_series)
        print("\nMost purchased -")
        print("Games:", ", ".join([game[0] for game in most_purchased_games]))
        print("Movies:", ", ".join([movie[0] for movie in most_purchased_movies]))
        print("WebSeries:", ", ".join([web_series[0] for web_series in most_purchased_web_series]))
        print("\nTotal sale: $", total_sale)

    except mysql.connector.Error as e:
        print("Error in report and analytics:", e)


def welcome_page(conn):
    while True:
        print("-"*60)
        print("Welcome to byteSized Entertainment\n")
        print("1 Login")
        print("2 Sign Up")
        print("3 Enter as Admin")
        print("X Back")
        choice = input("Enter your choice: ").strip().upper()

        if choice == "1":
            login(conn)
        elif choice == "2":
            signup(conn)
        elif choice == "3":
            login_as_admin(conn)
        elif choice == "X":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3 or 'X' to go back.")


def user_home(conn, userID):
    while True:
        print("-" * 60)
        print("Home\n")
        print("1 Browse Store")
        print("2 Library")
        print("3 Cart")
        print("4 My Account")
        print("X Log Out")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "1":
            browse_store(conn, userID)
        elif choice == "2":
            library(conn, userID)
        elif choice == "3":
            view_cart(conn, userID)
        elif choice == "4":
            my_account(conn, userID)
        elif choice == "X":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def browse_store(conn, userID):
    while True:
        print("-" * 60)
        print("Store\n")
        print("1 Games")
        print("2 Movies")
        print("3 Webseries")
        print("4 Recommendations")
        print("X Back")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "1":
            view_games(conn, userID)
        elif choice == "2":
            view_movies(conn, userID)
        elif choice == "3":
            view_series(conn, userID)
        elif choice == "4":
            view_recommendations(conn, userID)
        elif choice == "X":
            print("Going back...")
            break
        else:
            print("Invalid choice. Please enter a valid option.")


def view_games(conn, userID):
    preferences = {"Sort": "Game_ID", "Desc": False, "Token": "", "maxPrice": -1, "Genres": {"Action": True, "Adventure": True, "Battle": True, "FPS": True, "Party": True, "Racing": True, "Royale": True, "RPG": True, "Sports": True, "Sandbox": True, "Simulation": True}, "ageRating": {"E": True, "E10+": True, "T": True, "M": True, "AO": True}} 
    while True:
        print("-" * 60)
        print("Games\n")
        print("S Search")
        print("D Sort")
        print("F Filters")

        game_list = game_results(conn, preferences)
        n = len(game_list)
        if(len(game_list)):
            for i in range(n):
                print(f"{i+1:<5} {game_list[i][1]:<50} ${game_list[i][2]}")
        else:
            print("No items to show")

        print("X Back")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "S":
            search_query = input("Enter search query: ").strip()
            preferences["Token"] = search_query
        elif choice == "D":
            print("-" * 60)
            print("Sort by:")
            print("0 Default")
            print("1 Name: A-Z")
            print("2 Name: Z-A")
            print("3 Price: Low to High")
            print("4 Price: High to Low")
            print("5 Rating: High to Low")
            print("6 Date Released: Newest")
            print("7 Date Released: Oldest")
            print("X Back")

            sort_choice = input("Enter your choice: ").strip().upper()
            if sort_choice == "0":
                preferences["Sort"] = "Game_ID"

            elif sort_choice == "1":
                preferences["Sort"] = "Title" 

            elif sort_choice == "2":
                preferences["Sort"] = "Title"
                preferences["Desc"] = True

            elif sort_choice == "3":
                preferences["Sort"] = "Price"

            elif sort_choice == "4":
                preferences["Sort"] = "Price"
                preferences["Desc"] = True

            elif sort_choice == "5":
                preferences["Sort"] = "Rating"
                preferences["Desc"] = True

            elif sort_choice == "6":
                preferences["Sort"] = "Release_Date"
                preferences["Desc"] = True

            elif sort_choice == "7":
                preferences["Sort"] = "Release_Date" 
            
            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "F":
            print("-" * 60)
            print("Select filter:")
            print("1 Set Maximum Price")
            print("2 Genres")
            print("3 Age Ratings")
            print("4 Remove Filters")
            print("X Back")

            filter_choice = input("Enter your choice: ").strip().upper()
            if filter_choice == "1":
                print("-" * 60)
                print("Select Max Price")
                print("0 Max Price = No limit")
                print("1 Max Price = $15")
                print("2 Max Price = $30")
                print("3 Max Price = $45")
                print("4 Max Price = $60")
                print("X Back")

                max_price_choice = input("Enter your choice: ").strip().upper()

                if max_price_choice == "0":
                    preferences["maxPrice"] = -1
                elif max_price_choice == "1":
                    preferences["maxPrice"] = 15
                elif max_price_choice == "2":
                    preferences["maxPrice"] = 30
                elif max_price_choice == "3":
                    preferences["maxPrice"] = 45
                elif max_price_choice == "4":
                    preferences["maxPrice"] = 60
                elif choice == "X":
                    pass
                else:
                    print("Invalid choice. Please enter a valid option.")

            elif filter_choice == "2":
                print("Select which Genres to include: (Press ENTER to include and n/N to exclude)")
                for genre in preferences["Genres"].keys():
                    answer = input(f"{genre}: ").strip().upper()
                    if answer == "N":
                        preferences["Genres"][genre] = False
                    else:
                        preferences["Genres"][genre] = True
            elif filter_choice == "3":
                print("Select which Age-ratings to include: (Press ENTER to include and n/N to exclude)")
                for ageRating in preferences["ageRating"].keys():
                    answer = input(f"{ageRating}: ").strip().upper()
                    if answer == "N":
                        preferences["ageRating"][ageRating] = False
                    else:
                        preferences["ageRating"][ageRating] = True
            elif filter_choice == "4":
                preferences = {"Sort": "Game_ID", "Desc": False, "Token": "", "maxPrice": -1, "Genres": {"Action": True, "Adventure": True, "Racing": True, "Sports": True, "Party": True, "Battle": True, "Royale": True, "RPG": True, "FPS": True, "Sandbox": True, "Simulation": True}, "ageRating": {"E": True, "E10+": True, "T": True, "M": True, "AO": True}}
            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "X":
            print("Going back...")
            break
        elif choice.isnumeric():
            choice_num = int(choice)
            if choice_num >= 1 and choice_num <= n:
                # print(game_list[choice_num - 1])
                game_page(conn, game_list[choice_num-1][0], userID)
        else:
            print("Invalid choice. Please enter a valid option.")

def game_results(conn, preferences):
    try:
        cursor = conn.cursor()

        # Construct the base query
        query = "SELECT Game_ID, Title, Price FROM Games WHERE"

        if preferences["Token"]:
            token = preferences["Token"]
            query += f" Title like '%{token}%' AND"

        # Apply filters based on preferences
        if preferences["maxPrice"] > 0:
            maxPrice = preferences["maxPrice"]
            query += f" Price <= {maxPrice} AND"

        if preferences["Genres"]:
            genres = [genre for genre, enabled in preferences["Genres"].items() if enabled]
            if genres:
                genre_conditions = " OR ".join([f"Category LIKE '%{genre}%'" for genre in genres])
                query += f" ({genre_conditions}) AND"

        if preferences["ageRating"]:
            age_ratings = [rating for rating, enabled in preferences["ageRating"].items() if enabled]
            # print("age_ratings", age_ratings)
            if age_ratings:
                placeholders = ",".join([f"'{age_rating}'" for age_rating in age_ratings])
                query += f" Age_Rating IN ({placeholders}) AND"

        # Remove the trailing "AND"
        query = query.rstrip()
        query = query.rstrip("AND")
        query = query.rstrip("WHERE")

        # Apply sorting
        query += f" ORDER BY {preferences['Sort']}"
        if preferences['Desc']:
            query += " DESC"

        # print(query)
        cursor.execute(query)
        games = cursor.fetchall()
        cursor.close()
        return games

    except mysql.connector.Error as e:
        print("Error retrieving game results:", e)
        return []
    finally:
        cursor.close()

def game_page(conn, gameID, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Retrieve game information from the database
        cursor.execute("SELECT * FROM Games WHERE Game_ID = %s", (gameID,))
        game = cursor.fetchone()

        if game:
            print("-" * 60)
            print(f"Title: {game['Title']}")
            print(f"Category: {game['Category']}")
            print(f"Release Date: {game['Release_Date']}")
            print(f"Description: {game['Description']}")
            print(f"Price: ${game['Price']:.2f}")
            print(f"Age Rating: {game['Age_Rating']}")
            print(f"Download Size: {game['Download_Size']} MB")
            print(f"System Requirements: {game['System_Requirements']}")
            print(f"Rating: {game['Rating']}")

            while True:
                print("A Add to Cart")
                print("T View Trailer")
                print("X Back")

                choice = input("Enter your choice: ").strip().upper()

                if choice == "A":
                    add_game_to_cart(conn, gameID, userID)
                elif choice == "T":
                    view_trailer(game["Trailer_Video"])
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

        else:
            print("Game not found.")
    
    except mysql.connector.Error as e:
        print("Error retrieving game details:", e)
    
    finally:
        cursor.close()

def add_game_to_cart(conn, gameID, userID):
    try:
        cursor = conn.cursor()

        # Check if the game is already in the user's library
        cursor.execute("SELECT COUNT(*) FROM Library_Games WHERE User_ID = %s AND Game_ID = %s", (userID, gameID))
        library_count = cursor.fetchone()[0]

        if library_count > 0:
            print("You already own this game.")
            cursor.close()
            return
        
        # Check if the pair already exists in the Cart_Games table
        cursor.execute("SELECT COUNT(*) FROM Cart_Games WHERE User_ID = %s AND Game_ID = %s", (userID, gameID))
        count = cursor.fetchone()[0]

        if count > 0:
            print("This game is already in your cart.")
            cursor.close()
            return

        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        # Insert the pair into the Cart_Games table
        cursor.execute("INSERT INTO Cart_Games (User_ID, Game_ID) VALUES (%s, %s)", (userID, gameID))

        # Commit the transaction
        conn.commit()
        print("Game successfully added to cart.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error adding game to cart:", e)

    finally:
        cursor.close()


def view_movies(conn, userID):
    preferences = {"Sort": "Movie_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": True, "Adventure": True, "Animation": True, "Biography": True, "Crime": True, "Drama": True, "Fantasy": True, "History": True, "Romance": True, "Sci-Fi": True, "War": True}, "ageRating": {"G": True, "PG": True, "PG-13": True, "R": True, "NC-17": True}} 
    while True:
        print("-" * 60)
        print("Movies\n")
        print("S Search")
        print("D Sort")
        print("F Filters")

        movie_list = movie_results(conn, preferences)
        n = len(movie_list)
        if(len(movie_list)):
            for i in range(n):
                print(f"{i+1:<5} {movie_list[i][1]:<50} ${movie_list[i][2]}")
        else:
            print("No items to show")

        print("X Back")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "S":
            search_query = input("Enter search query: ").strip()
            preferences["Token"] = search_query
        elif choice == "D":
            print("-" * 60)
            print("Sort by:")
            print("0 Default")
            print("1 Name: A-Z")
            print("2 Name: Z-A")
            print("3 Price: Low to High")
            print("4 Price: High to Low")
            print("5 Rating: High to Low")
            print("6 Date Released: Newest")
            print("7 Date Released: Oldest")
            print("8 Runtime: Shortest to Longest")
            print("9 Runtime: Longest to Shortest")
            print("X Back")

            sort_choice = input("Enter your choice: ").strip().upper()
            if sort_choice == "0":
                preferences["Sort"] = "Movie_ID"

            elif sort_choice == "1":
                preferences["Sort"] = "Title" 

            elif sort_choice == "2":
                preferences["Sort"] = "Title"
                preferences["Desc"] = True

            elif sort_choice == "3":
                preferences["Sort"] = "Price"

            elif sort_choice == "4":
                preferences["Sort"] = "Price"
                preferences["Desc"] = True

            elif sort_choice == "5":
                preferences["Sort"] = "Rating"
                preferences["Desc"] = True

            elif sort_choice == "6":
                preferences["Sort"] = "Release_Date"
                preferences["Desc"] = True

            elif sort_choice == "7":
                preferences["Sort"] = "Release_Date" 
            
            elif sort_choice == "8":
                preferences["Sort"] = "Runtime" 
            
            elif sort_choice == "9":
                preferences["Sort"] = "Runtime" 
                preferences["Desc"] = True
            

            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "F":
            print("-" * 60)
            print("Select filter:")
            print("1 Set Maximum Price")
            print("2 Genres")
            print("3 Age Ratings")
            print("4 Cast")
            print("5 Remove Filters")
            print("X Back")

            filter_choice = input("Enter your choice: ").strip().upper()
            if filter_choice == "1":
                print("-" * 60)
                print("Select Max Price")
                print("0 Max Price = No limit")
                print("1 Max Price = $5")
                print("2 Max Price = $7")
                print("3 Max Price = $9")
                print("4 Max Price = $12")
                print("X Back")

                max_price_choice = input("Enter your choice: ").strip().upper()

                if max_price_choice == "0":
                    preferences["maxPrice"] = -1
                elif max_price_choice == "1":
                    preferences["maxPrice"] = 5
                elif max_price_choice == "2":
                    preferences["maxPrice"] = 7
                elif max_price_choice == "3":
                    preferences["maxPrice"] = 9
                elif max_price_choice == "4":
                    preferences["maxPrice"] = 12
                elif choice == "X":
                    pass
                else:
                    print("Invalid choice. Please enter a valid option.")

            elif filter_choice == "2":
                print("Select which Genres to include: (Press ENTER to include and n/N to exclude)")
                for genre in preferences["Genres"].keys():
                    answer = input(f"{genre}: ").strip().upper()
                    if answer == "N":
                        preferences["Genres"][genre] = False
                    else:
                        preferences["Genres"][genre] = True
            elif filter_choice == "3":
                print("Select which Age-ratings to include: (Press ENTER to include and n/N to exclude)")
                for ageRating in preferences["ageRating"].keys():
                    answer = input(f"{ageRating}: ").strip().upper()
                    if answer == "N":
                        preferences["ageRating"][ageRating] = False
                    else:
                        preferences["ageRating"][ageRating] = True
            elif filter_choice == "4":
                cast_names = input("Enter cast name(s): ").strip()
                preferences["Cast"] += cast_names.split()
            elif filter_choice == "5":
                preferences = {"Sort": "Movie_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": True, "Adventure": True, "Animation": True, "Biography": True, "Crime": True, "Drama": True, "Fantasy": True, "History": True, "Romance": True, "Sci-Fi": True, "War": True}, "ageRating": {"G": True, "PG": True, "PG-13": True, "R": True, "NC-17": True}} 
            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "X":
            print("Going back...")
            break
        elif choice.isnumeric():
            choice_num = int(choice)
            if choice_num >= 1 and choice_num <= n:
                # print(movie_list[choice_num - 1])
                movie_page(conn, movie_list[choice_num-1][0], userID)
        else:
            print("Invalid choice. Please enter a valid option.")

def movie_results(conn, preferences):
    try:
        cursor = conn.cursor()

        # Construct the base query
        query = "SELECT Movie_ID, Title, Price FROM Movies WHERE"

        if preferences["Token"]:
            token = preferences["Token"]
            query += f" Title like '%{token}%' AND"

        # Apply filters based on preferences
        if preferences["maxPrice"] > 0:
            maxPrice = preferences["maxPrice"]
            query += f" Price <= {maxPrice} AND"

        if preferences["Genres"]:
            genres = [genre for genre, enabled in preferences["Genres"].items() if enabled]
            if genres:
                genre_conditions = " OR ".join([f"Genre LIKE '%{genre}%'" for genre in genres])
                query += f" ({genre_conditions}) AND "

        if preferences["Cast"]:
            casts = preferences["Cast"]
            if casts:
                cast_names = " OR ".join([f"Cast_Crew LIKE '%{cast}%'" for cast in casts])
                query += f" ({cast_names}) AND"

        if preferences["ageRating"]:
            age_ratings = [rating for rating, enabled in preferences["ageRating"].items() if enabled]
            # print("age_ratings", age_ratings)
            if age_ratings:
                placeholders = ",".join([f"'{age_rating}'" for age_rating in age_ratings])
                query += f" Age_Rating IN ({placeholders}) AND"

        # Remove the trailing "AND"
        query = query.rstrip()
        query = query.rstrip("AND")
        query = query.rstrip("WHERE")

        # Apply sorting
        query += f" ORDER BY {preferences['Sort']}"
        if preferences['Desc']:
            query += " DESC"

        # print(query)
        cursor.execute(query)
        movies = cursor.fetchall()
        cursor.close()
        return movies

    except mysql.connector.Error as e:
        print("Error retrieving movie results:", e)
        print(query)
        return []
    finally:
        cursor.close()

def movie_page(conn, movieID, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Retrieve movie information from the database
        cursor.execute("SELECT * FROM Movies WHERE Movie_ID = %s", (movieID,))
        movie = cursor.fetchone()

        if movie:
            print("-" * 60)
            print(f"Title: {movie['Title']}")
            print(f"Production Studio: {movie['Production_Studio']}")
            print(f"Release Date: {movie['Release_Date']}")
            print(f"Genres: {movie['Genre']}")
            print(f"Description: {movie['Description']}")
            print(f"Cast & Crew: {movie['Cast_Crew']}")
            print(f"Runtime: {movie['Runtime']} minutes")
            print(f"Age Rating: {movie['Age_Rating']}")
            print(f"Rating: {movie['Rating']}")
            print(f"Price: ${movie['Price']:.2f}")
            print(f"Download Size: {movie['Download_Size']} MB")
            print(f"Languages: {movie['Languages']}")

            while True:
                print("A Add to Cart")
                print("T View Trailer")
                print("X Back")

                choice = input("Enter your choice: ").strip().upper()

                if choice == "A":
                    add_movie_to_cart(conn, movieID, userID)
                elif choice == "T":
                    view_trailer(movie["Trailer_Video"])
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error:", e)

    finally:
        cursor.close()

def add_movie_to_cart(conn, movieID, userID):
    try:
        cursor = conn.cursor()
        # Check if the movie is already in the user's library
        cursor.execute("SELECT COUNT(*) FROM Library_Movies WHERE User_ID = %s AND Movie_ID = %s", (userID, movieID))
        library_count = cursor.fetchone()[0]

        if library_count > 0:
            print("You already own this movie.")
            cursor.close()
            return
        
        # Check if the pair already exists in the Cart_Movies table
        cursor.execute("SELECT COUNT(*) FROM Cart_Movies WHERE User_ID = %s AND Movie_ID = %s", (userID, movieID))
        count = cursor.fetchone()[0]

        if count > 0:
            print("This movie is already in your cart.")
            cursor.close()
            return

        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        
        # Insert the pair into the Cart_Movies table
        cursor.execute("INSERT INTO Cart_Movies (User_ID, Movie_ID) VALUES (%s, %s)", (userID, movieID))

        # Commit the transaction
        conn.commit()
        print("Movie successfully added to cart.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error adding movie to cart:", e)

    finally:
        cursor.close()


def view_series(conn, userID):
    preferences = {"Sort": "Series_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": True, "Adventure": True, "Animation": True, "Biography": True, "Comedy": True, "Crime": True, "Drama": True, "Fantasy": True, "History": True, "Horror": True, "Mystery": True, "Romance": True, "Sci-Fi": True, "Thriller": True, "War": True}, "ageRating": {"G": True, "PG": True, "PG-13": True, "R": True, "NC-17": True}} 
    while True:
        print("-" * 60)
        print("Series\n")
        print("S Search")
        print("D Sort")
        print("F Filters")

        series_list = series_results(conn, preferences)
        n = len(series_list)
        if(len(series_list)):
            for i in range(n):
                print(f"{i+1:<5} {series_list[i][1]:<50} ${series_list[i][2]}")
        else:
            print("No items to show")

        print("X Back")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "S":
            search_query = input("Enter search query: ").strip()
            preferences["Token"] = search_query
        elif choice == "D":
            print("-" * 60)
            print("Sort by:")
            print("0 Default")
            print("1 Name: A-Z")
            print("2 Name: Z-A")
            print("3 Price: Low to High")
            print("4 Price: High to Low")
            print("5 Rating: High to Low")
            print("6 Date Released: Newest")
            print("7 Date Released: Oldest")
            print("8 Production Studio")
            print("X Back")

            sort_choice = input("Enter your choice: ").strip().upper()
            if sort_choice == "0":
                preferences["Sort"] = "Series_ID"

            elif sort_choice == "1":
                preferences["Sort"] = "Title" 

            elif sort_choice == "2":
                preferences["Sort"] = "Title"
                preferences["Desc"] = True

            elif sort_choice == "3":
                preferences["Sort"] = "Price"

            elif sort_choice == "4":
                preferences["Sort"] = "Price"
                preferences["Desc"] = True

            elif sort_choice == "5":
                preferences["Sort"] = "Rating"
                preferences["Desc"] = True

            elif sort_choice == "6":
                preferences["Sort"] = "Release_Date"
                preferences["Desc"] = True

            elif sort_choice == "7":
                preferences["Sort"] = "Release_Date" 
            
            elif sort_choice == "8":
                preferences["Sort"] = "Production_Studio" 
                        
            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "F":
            print("-" * 60)
            print("Select filter:")
            print("1 Set Maximum Price")
            print("2 Genres")
            print("3 Age Ratings")
            print("4 Cast")
            print("5 Remove Filters")
            print("X Back")

            filter_choice = input("Enter your choice: ").strip().upper()
            if filter_choice == "1":
                print("-" * 60)
                print("Select Max Price")
                print("0 Max Price = No limit")
                print("1 Max Price = $5")
                print("2 Max Price = $7")
                print("3 Max Price = $9")
                print("4 Max Price = $12")
                print("X Back")

                max_price_choice = input("Enter your choice: ").strip().upper()

                if max_price_choice == "0":
                    preferences["maxPrice"] = -1
                elif max_price_choice == "1":
                    preferences["maxPrice"] = 5
                elif max_price_choice == "2":
                    preferences["maxPrice"] = 7
                elif max_price_choice == "3":
                    preferences["maxPrice"] = 9
                elif max_price_choice == "4":
                    preferences["maxPrice"] = 12
                elif choice == "X":
                    pass
                else:
                    print("Invalid choice. Please enter a valid option.")

            elif filter_choice == "2":
                print("Select which Genres to include: (Press ENTER to include and n/N to exclude)")
                for genre in preferences["Genres"].keys():
                    answer = input(f"{genre}: ").strip().upper()
                    if answer == "N":
                        preferences["Genres"][genre] = False
                    else:
                        preferences["Genres"][genre] = True
            elif filter_choice == "3":
                print("Select which Age-ratings to include: (Press ENTER to include and n/N to exclude)")
                for ageRating in preferences["ageRating"].keys():
                    answer = input(f"{ageRating}: ").strip().upper()
                    if answer == "N":
                        preferences["ageRating"][ageRating] = False
                    else:
                        preferences["ageRating"][ageRating] = True
            elif filter_choice == "4":
                cast_names = input("Enter cast name(s): ").strip()
                preferences["Cast"] += cast_names.split()
            elif filter_choice == "5":
                preferences = {"Sort": "Series_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": True, "Adventure": True, "Animation": True, "Biography": True, "Comedy": True, "Crime": True, "Drama": True, "Fantasy": True, "History": True, "Horror": True, "Mystery": True, "Romance": True, "Sci-Fi": True, "Thriller": True, "War": True}, "ageRating": {"G": True, "PG": True, "PG-13": True, "R": True, "NC-17": True}}
            elif choice == "X":
                pass
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == "X":
            print("Going back...")
            break
        elif choice.isnumeric():
            choice_num = int(choice)
            if choice_num >= 1 and choice_num <= n:
                series_page(conn, series_list[choice_num-1][0], userID)
        else:
            print("Invalid choice. Please enter a valid option.")

def series_results(conn, preferences):
    try:
        cursor = conn.cursor()

        # Construct the base query
        query = "SELECT Series_ID, Title, Price FROM Series WHERE"

        if preferences["Token"]:
            token = preferences["Token"]
            query += f" Title like '%{token}%' AND"

        # Apply filters based on preferences
        if preferences["maxPrice"] > 0:
            maxPrice = preferences["maxPrice"]
            query += f" Price <= {maxPrice} AND"

        if preferences["Genres"]:
            genres = [genre for genre, enabled in preferences["Genres"].items() if enabled]
            if genres:
                genre_conditions = " OR ".join([f"Genre LIKE '%{genre}%'" for genre in genres])
                query += f" ({genre_conditions}) AND "

        if preferences["Cast"]:
            casts = preferences["Cast"]
            if casts:
                cast_names = " OR ".join([f"Cast_Crew LIKE '%{cast}%'" for cast in casts])
                query += f" ({cast_names}) AND"

        if preferences["ageRating"]:
            age_ratings = [rating for rating, enabled in preferences["ageRating"].items() if enabled]
            # print("age_ratings", age_ratings)
            if age_ratings:
                placeholders = ",".join([f"'{age_rating}'" for age_rating in age_ratings])
                query += f" Age_Rating IN ({placeholders}) AND"

        # Remove the trailing "AND"
        query = query.rstrip()
        query = query.rstrip("AND")
        query = query.rstrip("WHERE")

        # Apply sorting
        query += f" ORDER BY {preferences['Sort']}"
        if preferences['Desc']:
            query += " DESC"

        # print(query)
        cursor.execute(query)
        series = cursor.fetchall()
        cursor.close()
        return series

    except mysql.connector.Error as e:
        print("Error retrieving webseries results:", e)
        print(query)
        return []
    finally:
        cursor.close()

def series_page(conn, seriesID, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Retrieve series information from the database
        cursor.execute("SELECT * FROM Series WHERE Series_ID = %s", (seriesID,))
        series = cursor.fetchone()

        if series:
            print("-" * 60)
            print(f"Title: {series['Title']}")
            print(f"Production Studio: {series['Production_Studio']}")
            print(f"Release Date: {series['Release_Date']}")
            print(f"Genres: {series['Genre']}")
            print(f"Description: {series['Description']}")
            print(f"Cast & Crew: {series['Cast_Crew']}")
            print(f"Languages: {series['Languages']}")
            print(f"Age Rating: {series['Age_Rating']}")
            print(f"Rating: {series['Rating']}")
            print(f"Price: ${series['Price']:.2f}")
            print(f"Download Size: {series['Download_Size']} MB")

            while True:
                print("A Add to Cart")
                print("T View Trailer")
                print("E View Episode List")
                print("X Back")

                choice = input("Enter your choice: ").strip().upper()

                if choice == "A":
                    add_series_to_cart(conn, seriesID, userID)
                elif choice == "T":
                    view_trailer(series["Trailer_Video"])
                elif choice == "E":
                    view_episode_list(conn, seriesID)
                elif choice == "X":
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error:", e)

    finally:
        cursor.close()

def add_series_to_cart(conn, seriesID, userID):
    try:
        cursor = conn.cursor()

        # Check if the series is already in the user's library
        cursor.execute("SELECT COUNT(*) FROM Library_WebSeries WHERE User_ID = %s AND Series_ID = %s", (userID, seriesID))
        library_count = cursor.fetchone()[0]

        if library_count > 0:
            print("You already own this series.")
            cursor.close()
            return

        # Check if the pair already exists in the Cart_Series table
        cursor.execute("SELECT COUNT(*) FROM Cart_WebSeries WHERE User_ID = %s AND Series_ID = %s", (userID, seriesID))
        count = cursor.fetchone()[0]

        if count > 0:
            print("This series is already in your cart.")
            return

        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()
        
        # Insert the pair into the Cart_Series table
        cursor.execute("INSERT INTO Cart_WebSeries (User_ID, Series_ID) VALUES (%s, %s)", (userID, seriesID))

        # Commit the transaction
        conn.commit()
        print("Series successfully added to cart.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error adding series to cart:", e)

    finally:
        cursor.close()

def view_episode_list(conn, seriesID):
    try:
        cursor = conn.cursor(dictionary=True)

        # Retrieve episodes information from the database for the given series ID
        cursor.execute("SELECT * FROM Episodes WHERE Series_ID = %s", (seriesID,))
        episodes = cursor.fetchall()

        if episodes:
            print("-" * 60)
            print("Episodes\n")
            print(f"{'No.':<5} {'Title':<50} {'Duration (min)':<20} {'Release Date'}")
            for episode in episodes:
                print(f"{episode['Episode_number']:<5} {episode['Title']:<50} {episode['Duration_minutes']:<20} {episode['Release_date']}")
        else:
            print("No episodes found for Series ID", seriesID)

    except mysql.connector.Error as e:
        print("Error:", e)

    finally:
        cursor.close()


def view_trailer(link):
    try:
        webbrowser.open(link)
    except Exception as e:
        print("Error opening the link:", e)


def view_recommendations(conn, userID):
    try:
        cursor = conn.cursor()

        while True:
            # Construct the query to fetch game suggestions
            cursor.execute("SELECT G.Category FROM Games G INNER JOIN Library_Games LG ON G.Game_ID = LG.Game_ID WHERE LG.User_ID = %s ", (userID,))
            game_preferences = {"Sort": "Game_ID", "Desc": False, "Token": "", "maxPrice": -1, "Genres": {"Action": False, "Adventure": False, "Battle": False, "FPS": False, "Party": False, "Racing": False, "Royale": False, "RPG": False, "Sports": False, "Sandbox": False, "Simulation": False}, "ageRating": {"E": False, "E10+": False, "T": False, "M": False, "AO": False}}
            game_genres = cursor.fetchall()
            for row in game_genres:
                if len(row[0].split()) > 1:
                    for genre in row[0].split():
                        game_preferences["Genres"][genre] = True
                elif len(row[0].split("-")) > 1:
                    for genre in row[0].split():
                        game_preferences["Genres"][genre] = True
                else:
                    game_preferences["Genres"][row[0]] = True

            # Construct the query to fetch movie suggestions
            cursor.execute("SELECT M.Genre FROM MOVIES M INNER JOIN Library_Movies LM ON M.Movie_ID = LM.Movie_ID WHERE LM.User_ID = %s", (userID,))
            movie_preferences = {"Sort": "Movie_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": False, "Adventure": False, "Animation": False, "Biography": False, "Crime": False, "Drama": False, "Fantasy": False, "History": False, "Romance": False, "Sci-Fi": False, "War": False}, "ageRating": {"G": False, "PG": False, "PG-13": False, "R": False, "NC-17": False}}
            movie_genres = cursor.fetchall()
            for row in movie_genres:
                for genre in row[0].split(","):
                    movie_preferences["Genres"][genre.strip()] = True
            
            # Construct the query to fetch web series suggestions
            cursor.execute("SELECT S.Genre FROM Series S INNER JOIN Library_WebSeries LW ON S.Series_ID = LW.Series_ID WHERE LW.User_ID = %s", (userID,))
            series_preferences = {"Sort": "Series_ID", "Desc": False, "Token": "", "maxPrice": -1, "Cast": [], "Genres": {"Action": False, "Adventure": False, "Animation": False, "Biography": False, "Comedy": False, "Crime": False, "Drama": False, "Fantasy": False, "History": False, "Horror": False, "Mystery": False, "Romance": False, "Sci-Fi": False, "Thriller": False, "War": False}, "ageRating": {"G": False, "PG": False, "PG-13": False, "R": False, "NC-17": False}}
            series_genres = cursor.fetchall()
            for row in series_genres:
                for genre in row[0].split(","):
                    series_preferences["Genres"][genre.strip()] = True
            
            game_list = game_results(conn, game_preferences)
            movie_list = movie_results(conn, movie_preferences)
            series_list = series_results(conn, series_preferences)
            
            print("-" * 60)
            print("Recommendations")
            if not(game_list or movie_list or series_list):
                print("\nNo Recommendations")
                break
            
            g = len(game_list)
            print("\nGames:")
            if(len(game_list)):
                for i in range(g):
                    print(f"{i+1:<5} {game_list[i][1]:<50} ${game_list[i][2]}")

            m = len(movie_list)
            print("\nMovies:")
            if(len(movie_list)):
                for i in range(m):
                    print(f"{i+1:<5} {movie_list[i][1]:<50} ${movie_list[i][2]}")

            w = len(series_list)
            print("\nWeb Series:")
            if(len(series_list)):
                for i in range(w):
                    print(f"{i+1:<5} {series_list[i][1]:<50} ${series_list[i][2]}")

            print("\nV View Item")
            print("X Back")
            choice = input("Enter your choice: ").strip().upper()
            if choice == "V":
                print("Item code: G for Games, M for Movies, W for Webseries, followed by serial number of the item e.g. 'M3'")
                query = input("Enter code of the item to be viewed : ").strip().upper()
                if not isValidItemID(query):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G" and int(query[1:]) > len(game_list)) or (query[0] == "M" and int(query[1:]) > len(movie_list)) or (query[0] == "W" and int(query[1:]) > len(series_list)):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G"): game_page(conn, game_list[int(query[1:]) - 1][0], userID)
                elif(query[0] == "M"): movie_page(conn, movie_list[int(query[1:]) - 1][0], userID)
                elif(query[0] == "W"): series_page(conn, series_list[int(query[1:]) - 1][0], userID)
            elif choice == "X":
                    break
            else:
                print("Invalid choice. Please enter a valid option.")
    except mysql.connector.Error as e:
        print("Error retrieving recommendations:", e)
    finally:
        cursor.close()


def library(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)

        while True:
            # Retrieve purchased games
            cursor.execute("SELECT Games.Game_ID, Title FROM Games INNER JOIN Library_Games ON Games.Game_ID = Library_Games.Game_ID WHERE User_ID = %s", (userID,))
            games = cursor.fetchall()
            game_list = list(enumerate(games))

            # Retrieve purchased movies
            cursor.execute("SELECT Movies.Movie_ID, Title FROM Movies INNER JOIN Library_Movies ON Movies.Movie_ID = Library_Movies.Movie_ID WHERE User_ID = %s", (userID,))
            movies = cursor.fetchall()
            movie_list = list(enumerate(movies))

            # Retrieve purchased web series
            cursor.execute("SELECT Series.Series_ID, Title FROM Series INNER JOIN Library_WebSeries ON Series.Series_ID = Library_WebSeries.Series_ID WHERE User_ID = %s", (userID,))
            webseries = cursor.fetchall()
            series_list = list(enumerate(webseries))
            
        
            print("-" * 60)
            print("Library")
            if((game_list + movie_list + series_list) == []):
                print("\nLibrary is empty")
                return
            print("\nGames:")
            for game in game_list:
                print(f"{game[0]+1:<5}{game[1]['Title']:<50}")

            print("\nMovies:")
            for movie in movie_list:
                print(f"{movie[0]+1:<5} {movie[1]['Title']:<50}")

            print("\nWeb Series:")
            for series in series_list:
                print(f"{series[0]+1:<5} {series[1]['Title']:<50}")
            
            print("\nV View Item")
            print("C Clear Library")
            print("X Back")
            choice = input("Enter your choice: ").strip().upper()
            if choice == "V":
                    print("Item code: G for Games, M for Movies, W for Webseries, followed by serial number of the item e.g. 'M3'")
                    query = input("Enter code of the item to be viewed : ").strip().upper()
                    if not isValidItemID(query):
                        print("Invalid item ID.")
                        continue
                    if(query[0] == "G" and int(query[1:]) > len(game_list)) or (query[0] == "M" and int(query[1:]) > len(movie_list)) or (query[0] == "W" and int(query[1:]) > len(series_list)):
                        print("Invalid item ID.")
                        continue
                    if(query[0] == "G"): game_page(conn, game_list[int(query[1:]) - 1][1]["Game_ID"], userID)
                    elif(query[0] == "M"): movie_page(conn, movie_list[int(query[1:]) - 1][1]["Movie_ID"], userID)
                    elif(query[0] == "W"): series_page(conn, series_list[int(query[1:]) - 1][1]["Series_ID"], userID)
            elif choice == "C":
                clear_library(conn, userID)
            elif choice == "X":
                    break
            else:
                print("Invalid choice. Please enter a valid option.")
    except mysql.connector.Error as e:
        print("Error retrieving library:", e)

    finally:
        cursor.close()

def clear_library(conn, userID):
    try:
        cursor = conn.cursor()

        # Start a transaction
        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Clear library for games
        cursor.execute("DELETE FROM Library_Games WHERE User_ID = %s", (userID,))

        # Clear library for movies
        cursor.execute("DELETE FROM Library_Movies WHERE User_ID = %s", (userID,))

        # Clear library for web series
        cursor.execute("DELETE FROM Library_WebSeries WHERE User_ID = %s", (userID,))

        # Commit the transaction
        conn.commit()
        print("Library cleared successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error clearing library:", e)
    finally:
        cursor.close() 

def view_cart(conn, userID):
    try:
        cursor = conn.cursor(dictionary=True)
        
        while True:
            # Retrieve games in the cart
            cursor.execute("SELECT Games.Game_ID, Title, Price FROM Games INNER JOIN Cart_Games ON Games.Game_ID = Cart_Games.Game_ID WHERE User_ID = %s", (userID,))
            games = cursor.fetchall()
            game_list = list(enumerate(games))

            # Retrieve movies in the cart
            cursor.execute("SELECT Movies.Movie_ID, Title, Price FROM Movies INNER JOIN Cart_Movies ON Movies.Movie_ID = Cart_Movies.Movie_ID WHERE User_ID = %s", (userID,))
            movies = cursor.fetchall()
            movie_list = list(enumerate(movies))

            # Retrieve web series in the cart
            cursor.execute("SELECT Series.Series_ID, Title, Price FROM Series INNER JOIN Cart_WebSeries ON Series.Series_ID = Cart_WebSeries.Series_ID WHERE User_ID = %s", (userID,))
            webseries = cursor.fetchall()
            series_list = list(enumerate(webseries))

            print("-" * 60)
            print("Cart")
            total_price = 0
            if((game_list + movie_list + series_list) == []):
                print("\nCart is empty")
                return

            # Print games in cart
            if games:
                print("\nGames:")
                for game in game_list:
                    print(f"{game[0]+1:<5}{game[1]['Title']:<50} ${game[1]['Price']:.2f}")
                    total_price += game[1]['Price']

            # Print movies in cart
            if movies:
                print("\nMovies:")
                for movie in movie_list:
                    print(f"{movie[0]+1:<5} {movie[1]['Title']:<50} ${movie[1]['Price']:.2f}")
                    total_price += movie[1]['Price']

            # Print web series in cart
            if webseries:
                print("\nWeb Series:")
                for series in series_list:
                    print(f"{series[0]+1:<5} {series[1]['Title']:<50} ${series[1]['Price']:.2f}")
                    total_price += series[1]['Price']

            print(f"\nTotal Price: ${total_price:.2f}\n")

            print("C Checkout")
            print("V View Item")
            print("R Remove Items")
            print("D Clear Cart")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "C":
                checkout(conn, userID)
            elif choice == "R":
                print("Item code: G for Games, M for Movies, W for Webseries, followed by serial number of the item e.g. 'M3'")
                query = input("Enter code of the item to be removed: ").strip().upper()
                if not isValidItemID(query):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G" and int(query[1:]) > len(game_list)) or (query[0] == "M" and int(query[1:]) > len(movie_list)) or (query[0] == "W" and int(query[1:]) > len(series_list)):
                    print("Invalid item ID.")
                    continue
                itemID = query[0]
                if(query[0] == "G"): itemID += str(game_list[int(query[1:]) - 1][1]["Game_ID"])
                elif(query[0] == "M"): itemID += str(movie_list[int(query[1:]) - 1][1]["Movie_ID"])
                elif(query[0] == "W"): itemID += str(series_list[int(query[1:]) - 1][1]["Series_ID"])
                remove_items(conn, userID, itemID)
            elif choice == "V":
                print("Item code: G for Games, M for Movies, W for Webseries, followed by serial number of the item e.g. 'M3'")
                query = input("Enter code of the item to be viewed : ").strip().upper()
                if not isValidItemID(query):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G" and int(query[1:]) > len(game_list)) or (query[0] == "M" and int(query[1:]) > len(movie_list)) or (query[0] == "W" and int(query[1:]) > len(series_list)):
                    print("Invalid item ID.")
                    continue
                if(query[0] == "G"): game_page(conn, game_list[int(query[1:]) - 1][1]["Game_ID"], userID)
                elif(query[0] == "M"): movie_page(conn, movie_list[int(query[1:]) - 1][1]["Movie_ID"], userID)
                elif(query[0] == "W"): series_page(conn, series_list[int(query[1:]) - 1][1]["Series_ID"], userID)
                
            elif choice == "D":
                clear_cart(conn, userID)
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")
                
    except mysql.connector.Error as e:
        print("Error retrieving cart:", e)

    finally:
        cursor.close()

def checkout(conn, userID):
    try:
        cursor = conn.cursor()
        
        if not conn.in_transaction:
            conn.start_transaction()

        # Calculate the total price of items in the cart
        cursor.execute("""
            SELECT SUM(price) 
            FROM (
                SELECT Price FROM Games INNER JOIN Cart_Games ON Games.Game_ID = Cart_Games.Game_ID WHERE User_ID = %s
                UNION ALL
                SELECT Price FROM Movies INNER JOIN Cart_Movies ON Movies.Movie_ID = Cart_Movies.Movie_ID WHERE User_ID = %s
                UNION ALL
                SELECT Price FROM Series INNER JOIN Cart_WebSeries ON Series.Series_ID = Cart_WebSeries.Series_ID WHERE User_ID = %s
            ) AS total_price
        """, (userID, userID, userID))
        total_price = cursor.fetchone()[0]

        # Check if the user has sufficient balance
        cursor.execute("SELECT Balance FROM Users WHERE User_ID = %s", (userID,))
        balance = cursor.fetchone()[0]

        if total_price > balance:
            print("Insufficient balance. Please add funds to your wallet.")
            return

        print(f"Current Wallet Balance: ${balance}")
        print(f"Total Cart Price: ${total_price}")
        print(f"Balance left after purchase: {balance - total_price}")
        confirm = input("Do you really want to check out? (y/Y) for yes: ").strip().upper()
        if confirm != "Y":
            return

        # Deduct the total price from the user's balance
        cursor.execute("UPDATE Users SET Balance = Balance - %s WHERE User_ID = %s", (total_price, userID))

        # Move items from cart to library
        cursor.execute("INSERT INTO Library_Games (User_ID, Game_ID) SELECT User_ID, Game_ID FROM Cart_Games WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Cart_Games WHERE User_ID = %s", (userID,))

        cursor.execute("INSERT INTO Library_Movies (User_ID, Movie_ID) SELECT User_ID, Movie_ID FROM Cart_Movies WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Cart_Movies WHERE User_ID = %s", (userID,))

        cursor.execute("INSERT INTO Library_WebSeries (User_ID, Series_ID) SELECT User_ID, Series_ID FROM Cart_WebSeries WHERE User_ID = %s", (userID,))
        cursor.execute("DELETE FROM Cart_WebSeries WHERE User_ID = %s", (userID,))

        # Commit the transaction
        conn.commit()
        print("Checkout successful. Items purchased and added to your library.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error during checkout:", e)

    finally:
        cursor.close()

def isValidItemID(itemID):
    if(len(itemID) < 2):
        return False
    if(itemID[0] not in ["G", "M", "W"]):
        return False
    if(not itemID[1:].isnumeric()):
        return False
    return True

def remove_items(conn, userID, itemID):
    try:
        cursor = conn.cursor()

        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Determine the table based on the itemID prefix ("G", "M", or "W")
        table_name = ""
        table_ID = ""
        if itemID[0] == "G":
            table_name = "Cart_Games"
            table_ID = "Game_ID"
        elif itemID[0] == "M":
            table_name = "Cart_Movies"
            table_ID = "Movie_ID"
        elif itemID[0] == "W":
            table_name = "Cart_WebSeries"
            table_ID = "Series_ID"

        if table_name:
            # Check if the item exists in the cart
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE User_ID = %s AND {table_ID} = %s", (userID, int(itemID[1:])))
            count = cursor.fetchone()[0]

            if count == 0:
                print("Item does not exist in the cart.")
            else:
                # Remove the item from the corresponding table
                cursor.execute(f"DELETE FROM {table_name} WHERE User_ID = %s AND {table_ID} = %s", (userID, itemID[1:]))

                # Commit the transaction
                conn.commit()

                print("Item successfully deleted from cart.")
        else:
            print("Invalid item ID.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error deleting item from cart:", e)

    finally:
        cursor.close()

def clear_cart(conn, userID):
    try:
        cursor = conn.cursor()

        if not conn.in_transaction:
            # Start a transaction
            conn.start_transaction()

        # Delete items from Cart_Games table
        cursor.execute("DELETE FROM Cart_Games WHERE User_ID = %s", (userID,))

        # Delete items from Cart_Movies table
        cursor.execute("DELETE FROM Cart_Movies WHERE User_ID = %s", (userID,))

        # Delete items from Cart_WebSeries table
        cursor.execute("DELETE FROM Cart_WebSeries WHERE User_ID = %s", (userID,))

        # Commit the transaction
        conn.commit()

        print("Cart successfully cleared.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error clearing cart:", e)

    finally:
        cursor.close()


def my_account(conn, userID):
    while True:
        print("-" * 60)
        print("My Account\n")
        print("1 Account Info")
        print("2 Change Password")
        print("3 ByteSized Wallet")
        print("X Back")

        choice = input("Enter your choice: ").strip().upper()

        if choice == "1":
            account_info(conn, userID)
        elif choice == "2":
            change_password(conn, userID)
        elif choice == "3":
            byteSized_wallet(conn, userID)
        elif choice == "X":
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def account_info(conn, userID):
    while True:
        # Retrieve account information from the database
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE User_ID = %s", (userID,))
        user = cursor.fetchone()

        if user:
            print("-" * 60)
            print("Account Information\n")
            print(f"Username: {user['Name']}")
            print(f"Email: {user['Email']}")
            print(f"Phone No.: {user['Phone_No']}")
            print(f"Balance: ${user['Balance']:.2f}\n")
            print("1 Change Username")
            print("2 Change Phone Number")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "1":
                new_username = input("Enter new username: ").strip()
                update_username(conn, userID, new_username)
            elif choice == "2":
                new_phone = input("Enter new phone number: ").strip()
                update_phone(conn, userID, new_phone)
            elif choice == "X":
                break  
            else:
                print("Invalid choice. Please enter a valid option.")
        else:
            print("User not found.")

def update_username(conn, userID, new_username):
    try:
        cursor = conn.cursor()
        if not conn.in_transaction:
            conn.start_transaction()
        cursor.execute("UPDATE Users SET Name = %s WHERE User_ID = %s", (new_username, userID))
        conn.commit()
        print("Username updated successfully.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Error updating username:", e)
    finally:
        cursor.close()

def update_phone(conn, userID, new_phone):
    try:
        cursor = conn.cursor()
        if not conn.in_transaction:
            conn.start_transaction()
        cursor.execute("UPDATE Users SET Phone_No = %s WHERE User_ID = %s", (new_phone, userID))

        # Commit the transaction
        conn.commit()
        print("Phone number updated successfully.")

    except mysql.connector.Error as e:
        # Roll back the transaction if an error occurs
        conn.rollback()
        print("Error updating phone number:", e)

    finally:
        cursor.close()

def change_password(conn, userID):
    try:
        cursor = conn.cursor()
        current_password = input("Enter your current password: ").strip()
        cursor.execute("SELECT Password FROM Users WHERE User_ID = %s", (userID,))
        stored_password = cursor.fetchone()[0]

        if current_password != stored_password:
            print("Incorrect current password. Password change failed.")
            return

        new_password = input("Enter your new password: ").strip()
        confirm_password = input("Confirm your new password: ").strip()

        if new_password != confirm_password:
            print("Passwords do not match. Password change failed.")
            return

        if not conn.in_transaction:
            conn.start_transaction()

        cursor.execute("UPDATE Users SET Password = %s WHERE User_ID = %s", (new_password, userID))

        conn.commit()
        print("Password changed successfully.")

    except mysql.connector.Error as e:
        conn.rollback()
        print("Error changing password:", e)

    finally:
        cursor.close()

def byteSized_wallet(conn, userID):
    try:
        cursor = conn.cursor()

        while True:

            cursor.execute("SELECT Balance FROM Users WHERE User_ID = %s", (userID,))
            balance = cursor.fetchone()[0]
            print("-" * 60)
            print("byteSized Wallet\n")
            print(f"Your current wallet balance is: ${balance:.2f}\n")
            print("A Add money to wallet")
            print("X Back")

            choice = input("Enter your choice: ").strip().upper()

            if choice == "A":
                amount = Decimal(input("Enter the amount to add to your wallet: ").strip().upper())

                if amount <= 0:
                    print("Invalid amount. Please enter a positive value.")
                    continue
                
                new_balance = balance + amount
                if not conn.in_transaction:
                    conn.start_transaction()
                cursor.execute("UPDATE Users SET Balance = %s WHERE User_ID = %s", (new_balance, userID))
                conn.commit()
                print(f"${amount:.2f} added to your wallet successfully.")
            elif choice == "X":
                break
            else:
                print("Invalid choice. Please enter a valid option.")

    except mysql.connector.Error as e:
        print("Error:", e)

    finally:
        cursor.close()

def main():
    conn = connect_to_database()
    if not conn:
        return

    while True:
        print("-"*60)
        print("Welcome to byteSized Entertainment.")
        response = input("Press any key to enter the application, or 'X' to exit: ").strip().upper()

        if response == "X":
            print("Exiting...")
            break
        else:
            welcome_page(conn)
    conn.close()
    print("Exited Successfully.")

if __name__ == "__main__":
    main()
