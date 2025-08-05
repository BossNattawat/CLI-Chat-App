# 💬 CLI Chat App

A simple, and secure command-line chat application built with Python!  
Supports user registration, login, chat rooms with passwords, and real-time messaging.  
Styled client output with [Rich](https://github.com/Textualize/rich) for a better terminal experience.

---

## 🚀 Features

- **User Registration & Login** (with bcrypt password hashing)
- **Create or Join Chat Rooms** (rooms are password-protected)
- **Real-time Messaging** between users in the same room
- **/clients** command to list users in your room
- **Rich Terminal Output** for a modern CLI feel

---

## 🛠️ Setup

1. **Clone or Download** this repository.

2. **Install dependencies**  
   Run in your terminal:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Server**  

   ```bash
   python server.py
   ```

4. **Start the Client** (in a new terminal window, can be run multiple times)

   ```bash
   python chat_client.py
   ```

---

## 💬 Usage

1. **Register** or **Login** when prompted.
2. **Create** a new chat room or **Join** an existing one (room IDs and passwords are required).
3. **Chat** with others in the same room!
4. Type `/clients` to see who is in your room.
5. Type `exit` or `quit` to leave the chat.

---

## ⚠️ Notes

- All data is stored locally in `chat.db`.
- Passwords are securely hashed using bcrypt.
- The server must be running before clients can connect.
- Only users in the same room can see each other's messages.

---

## 🧑‍💻 Authors

- Made with ❤️ using Python, sockets, and Rich.

---

## License

This project is licensed under the MIT License. Feel free to use and modify it as needed.
