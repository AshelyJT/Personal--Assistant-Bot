from backend.app import app

if __name__ == "__main__":
    print("🚀 Starting Personal Assistant Bot...")
    app.run(debug=True, port=5000)