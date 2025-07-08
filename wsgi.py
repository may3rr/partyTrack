from app import create_app

app = create_app()

# Vercel需要这个变量名
application = app

if __name__ == '__main__':
    app.run() 