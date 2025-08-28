# from flask import Flask, request, render_template, redirect, url_for, session, flash
# import sqlite3
# import os
# import hashlib
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# DATABASE = "videos.db"

# def init_db():
#     conn = sqlite3.connect(DATABASE)
#     with open('schema.sql') as f:
#         conn.executescript(f.read())
#     conn.close()
#     # Add demo videos after creating tables
#     add_demo_videos()

# def add_demo_videos():
#     """Add some demo videos to the database"""
#     db = get_db()
    
#     # Check if demo videos already exist
#     count = db.execute('SELECT COUNT(*) as count FROM videos').fetchone()['count']
#     if count == 0:
#         # Add demo videos
#         demo_videos = [
#             {
#                 'title': 'Big Buck Bunny',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'G',
#                 'url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
#             },
#             {
#                 'title': 'Elephants Dream',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'PG',
#                 'url': 'https://sample-videos.com/video123/mp4/720/elephants-dream.mp4'
#             },
#             {
#                 'title': 'For Bigger Blazes',
#                 'publisher': 'Google',
#                 'producer': 'Google',
#                 'genre': 'Tech',
#                 'age_rating': 'G',
#                 'url': 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
#             }
#         ]
        
#         # Create a demo creator user
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 ('demo_creator', hash_password('demo123'), 'creator')
#             )
#             db.commit()
#             creator_id = db.execute(
#                 'SELECT id FROM users WHERE username = ?', 
#                 ('demo_creator',)
#             ).fetchone()['id']
            
#             # Insert demo videos
#             for video in demo_videos:
#                 db.execute('''
#                     INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) 
#                     VALUES (?, ?, ?, ?, ?, ?, ?)
#                 ''', (
#                     video['title'], 
#                     video['publisher'], 
#                     video['producer'], 
#                     video['genre'], 
#                     video['age_rating'], 
#                     video['url'], 
#                     creator_id
#                 ))
#             db.commit()
#             print("Demo videos added successfully!")
#         except sqlite3.IntegrityError:
#             pass  # Demo user already exists

# def get_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

# def hash_password(password):
#     """Simple password hashing"""
#     return hashlib.sha256(password.encode()).hexdigest()

# @app.route('/')
# def index():
#     db = get_db()
#     videos = db.execute('SELECT * FROM videos ORDER BY id DESC LIMIT 12').fetchall()
#     return render_template('index.html', videos=videos)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']
        
#         if not username or not password or not role:
#             flash('All fields are required!')
#             return render_template('register.html')
        
#         hashed_password = hash_password(password)
        
#         db = get_db()
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 (username, hashed_password, role)
#             )
#             db.commit()
#             flash('Registration successful! Please login.')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Username already exists!')
#             return render_template('register.html')
    
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         if not username or not password:
#             flash('Please enter both username and password!')
#             return render_template('login.html')
        
#         hashed_password = hash_password(password)
#         db = get_db()
#         user = db.execute(
#             'SELECT * FROM users WHERE username = ? AND password = ?', 
#             (username, hashed_password)
#         ).fetchone()
        
#         if user:
#             session['user'] = {
#                 'id': user['id'],
#                 'username': user['username'],
#                 'role': user['role']
#             }
#             # Redirect based on user role
#             if user['role'] == 'creator':
#                 flash(f'Welcome back, {username}! You are logged in as a Creator.')
#                 return redirect(url_for('dashboard'))
#             else:
#                 flash(f'Welcome back, {username}! You are logged in as a Consumer.')
#                 return redirect(url_for('index'))
#         else:
#             flash('Invalid username or password!')
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     flash('You have been logged out.')
#     return redirect(url_for('index'))

# @app.route('/dashboard')
# def dashboard():
#     if 'user' not in session:
#         flash('Please login first!')
#         return redirect(url_for('login'))
    
#     if session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can access this page.')
#         return redirect(url_for('index'))
    
#     db = get_db()
#     videos = db.execute(
#         'SELECT * FROM videos WHERE uploaded_by = ? ORDER BY id DESC', 
#         (session['user']['id'],)
#     ).fetchall()
#     return render_template('upload.html', videos=videos)

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     if 'user' not in session or session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can upload videos.')
#         return redirect(url_for('login'))
    
#     title = request.form['title']
#     publisher = request.form['publisher']
#     producer = request.form.get('producer', '')
#     genre = request.form.get('genre', '')
#     age_rating = request.form['age_rating']
#     url = request.form['url']

#     if not all([title, publisher, age_rating, url]):
#         flash('Please fill in all required fields!')
#         return redirect(url_for('dashboard'))

#     db = get_db()
#     db.execute(
#         'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
#         (title, publisher, producer, genre, age_rating, url, session['user']['id'])
#     )
#     db.commit()
#     flash(f'🎉 Video "{title}" uploaded successfully!')
#     return redirect(url_for('dashboard'))

# @app.route('/watch/<int:video_id>')
# def watch(video_id):
#     db = get_db()
#     video = db.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
#     if not video:
#         flash('Video not found!')
#         return redirect(url_for('index'))
    
#     comments = db.execute('''
#         SELECT c.comment, c.rating, u.username 
#         FROM comments c 
#         JOIN users u ON c.user_id = u.id 
#         WHERE c.video_id = ? 
#         ORDER BY c.id DESC
#     ''', (video_id,)).fetchall()
    
#     return render_template('watch.html', video=video, comments=comments)

# @app.route('/comment', methods=['POST'])
# def add_comment():
#     if 'user' not in session:
#         flash('Please login to comment!')
#         return redirect(url_for('login'))
    
#     video_id = request.form['video_id']
#     comment = request.form['comment']
#     rating = request.form['rating']

#     if not comment or not rating:
#         flash('Please fill in all fields!')
#         return redirect(url_for('watch', video_id=video_id))

#     db = get_db()
#     db.execute(
#         'INSERT INTO comments (video_id, user_id, comment, rating) VALUES (?, ?, ?, ?)', 
#         (video_id, session['user']['id'], comment, rating)
#     )
#     db.commit()
#     flash('✅ Comment added successfully!')
#     return redirect(url_for('watch', video_id=video_id))

# if __name__ == '__main__':
#     if not os.path.exists(DATABASE):
#         init_db()
#     app.run(debug=True, host='0.0.0.0', port=5000)











# new working code

# from flask import Flask, request, render_template, redirect, url_for, session, flash
# import sqlite3
# import os
# import hashlib
# from werkzeug.utils import secure_filename
# import uuid

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # Configuration for file uploads
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
# MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# DATABASE = "videos.db"

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def init_db():
#     conn = sqlite3.connect(DATABASE)
#     with open('schema.sql') as f:
#         conn.executescript(f.read())
#     conn.close()
#     # Add demo videos after creating tables
#     add_demo_videos()

# def add_demo_videos():
#     """Add some demo videos to the database"""
#     db = get_db()
    
#     # Check if demo videos already exist
#     count = db.execute('SELECT COUNT(*) as count FROM videos').fetchone()['count']
#     if count == 0:
#         # Add demo videos
#         demo_videos = [
#             {
#                 'title': 'Big Buck Bunny',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'G',
#                 'url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
#             },
#             {
#                 'title': 'Elephants Dream',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'PG',
#                 'url': 'https://sample-videos.com/video123/mp4/720/elephants-dream.mp4'
#             },
#             {
#                 'title': 'For Bigger Blazes',
#                 'publisher': 'Google',
#                 'producer': 'Google',
#                 'genre': 'Tech',
#                 'age_rating': 'G',
#                 'url': 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
#             }
#         ]
        
#         # Create a demo creator user
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 ('demo_creator', hash_password('demo123'), 'creator')
#             )
#             db.commit()
#             creator_id = db.execute(
#                 'SELECT id FROM users WHERE username = ?', 
#                 ('demo_creator',)
#             ).fetchone()['id']
            
#             # Insert demo videos
#             for video in demo_videos:
#                 db.execute('''
#                     INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) 
#                     VALUES (?, ?, ?, ?, ?, ?, ?)
#                 ''', (
#                     video['title'], 
#                     video['publisher'], 
#                     video['producer'], 
#                     video['genre'], 
#                     video['age_rating'], 
#                     video['url'], 
#                     creator_id
#                 ))
#             db.commit()
#             print("Demo videos added successfully!")
#         except sqlite3.IntegrityError:
#             pass  # Demo user already exists

# def get_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

# def hash_password(password):
#     """Simple password hashing"""
#     return hashlib.sha256(password.encode()).hexdigest()

# @app.route('/')
# def index():
#     if 'user' in session:
#         # If user is logged in, redirect to shorts view
#         return redirect(url_for('shorts'))
#     db = get_db()
#     videos = db.execute('SELECT * FROM videos ORDER BY id DESC LIMIT 12').fetchall()
#     return render_template('index.html', videos=videos)

# @app.route('/shorts')
# def shorts():
#     db = get_db()
#     videos = db.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
#     return render_template('shorts.html', videos=videos)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']
        
#         if not username or not password or not role:
#             flash('All fields are required!')
#             return render_template('register.html')
        
#         hashed_password = hash_password(password)
        
#         db = get_db()
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 (username, hashed_password, role)
#             )
#             db.commit()
#             flash('Registration successful! Please login.')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Username already exists!')
#             return render_template('register.html')
    
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         if not username or not password:
#             flash('Please enter both username and password!')
#             return render_template('login.html')
        
#         hashed_password = hash_password(password)
#         db = get_db()
#         user = db.execute(
#             'SELECT * FROM users WHERE username = ? AND password = ?', 
#             (username, hashed_password)
#         ).fetchone()
        
#         if user:
#             session['user'] = {
#                 'id': user['id'],
#                 'username': user['username'],
#                 'role': user['role']
#             }
#             # Redirect based on user role
#             if user['role'] == 'creator':
#                 flash(f'Welcome back, {username}! You are logged in as a Creator.')
#                 return redirect(url_for('dashboard'))
#             else:
#                 flash(f'Welcome back, {username}! You are logged in as a Consumer.')
#                 return redirect(url_for('shorts'))  # Consumers go to shorts view
#         else:
#             flash('Invalid username or password!')
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     flash('You have been logged out.')
#     return redirect(url_for('index'))

# @app.route('/dashboard')
# def dashboard():
#     if 'user' not in session:
#         flash('Please login first!')
#         return redirect(url_for('login'))
    
#     if session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can access this page.')
#         return redirect(url_for('index'))
    
#     db = get_db()
#     videos = db.execute(
#         'SELECT * FROM videos WHERE uploaded_by = ? ORDER BY id DESC', 
#         (session['user']['id'],)
#     ).fetchall()
#     return render_template('upload.html', videos=videos)

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     if 'user' not in session or session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can upload videos.')
#         return redirect(url_for('login'))
    
#     upload_type = request.form.get('upload_type', 'link')
#     title = request.form['title']
#     publisher = request.form['publisher']
#     producer = request.form.get('producer', '')
#     genre = request.form.get('genre', '')
#     age_rating = request.form['age_rating']
    
#     video_url = ""
    
#     if upload_type == 'file':
#         # Handle file upload
#         if 'video_file' not in request.files:
#             flash('No file selected!')
#             return redirect(url_for('dashboard'))
        
#         file = request.files['video_file']
#         if file.filename == '':
#             flash('No file selected!')
#             return redirect(url_for('dashboard'))
        
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             # Generate unique filename
#             unique_filename = str(uuid.uuid4()) + "_" + filename
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
#             file.save(file_path)
#             video_url = url_for('static', filename=f'uploads/{unique_filename}')
#         else:
#             flash('Invalid file type! Please upload MP4, MOV, AVI, MKV, or WEBM files.')
#             return redirect(url_for('dashboard'))
#     else:
#         # Handle URL upload
#         video_url = request.form['video_url']
#         if not video_url:
#             flash('Please provide a video URL!')
#             return redirect(url_for('dashboard'))

#     if not all([title, publisher, age_rating, video_url]):
#         flash('Please fill in all required fields!')
#         return redirect(url_for('dashboard'))

#     db = get_db()
#     db.execute(
#         'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
#         (title, publisher, producer, genre, age_rating, video_url, session['user']['id'])
#     )
#     db.commit()
#     flash(f'🎉 Video "{title}" uploaded successfully!')
#     return redirect(url_for('dashboard'))

# @app.route('/watch/<int:video_id>')
# def watch(video_id):
#     db = get_db()
#     video = db.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
#     if not video:
#         flash('Video not found!')
#         return redirect(url_for('index'))
    
#     comments = db.execute('''
#         SELECT c.comment, c.rating, u.username 
#         FROM comments c 
#         JOIN users u ON c.user_id = u.id 
#         WHERE c.video_id = ? 
#         ORDER BY c.id DESC
#     ''', (video_id,)).fetchall()
    
#     return render_template('watch.html', video=video, comments=comments)

# @app.route('/comment', methods=['POST'])
# def add_comment():
#     if 'user' not in session:
#         flash('Please login to comment!')
#         return redirect(url_for('login'))
    
#     video_id = request.form['video_id']
#     comment = request.form['comment']
#     rating = request.form['rating']

#     if not comment or not rating:
#         flash('Please fill in all fields!')
#         return redirect(url_for('watch', video_id=video_id))

#     db = get_db()
#     db.execute(
#         'INSERT INTO comments (video_id, user_id, comment, rating) VALUES (?, ?, ?, ?)', 
#         (video_id, session['user']['id'], comment, rating)
#     )
#     db.commit()
#     flash('✅ Comment added successfully!')
#     return redirect(url_for('watch', video_id=video_id))

# if __name__ == '__main__':
#     # Create upload directory if it doesn't exist
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
    
#     if not os.path.exists(DATABASE):
#         init_db()
#     app.run(debug=True, host='0.0.0.0', port=5000)









# from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
# import sqlite3
# import os
# import hashlib
# from datetime import datetime

# from sqlalchemy import false, true

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# DATABASE = "videos.db"

# def init_db():
#     conn = sqlite3.connect(DATABASE)
#     with open('schema.sql') as f:
#         conn.executescript(f.read())
#     conn.close()
#     add_demo_videos()

# def add_demo_videos():
#     db = get_db()
#     count = db.execute('SELECT COUNT(*) as count FROM videos').fetchone()['count']
#     if count == 0:
#         demo_videos = [
#             {
#                 'title': 'Big Buck Bunny',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'G',
#                 'url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
#             },
#             {
#                 'title': 'Elephants Dream',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'PG',
#                 'url': 'https://sample-videos.com/video123/mp4/720/elephants-dream.mp4'
#             },
#             {
#                 'title': 'For Bigger Blazes',
#                 'publisher': 'Google',
#                 'producer': 'Google',
#                 'genre': 'Tech',
#                 'age_rating': 'G',
#                 'url': 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
#             }
#         ]
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 ('demo_creator', hash_password('demo123'), 'creator')
#             )
#             db.commit()
#             creator_id = db.execute(
#                 'SELECT id FROM users WHERE username = ?', 
#                 ('demo_creator',)
#             ).fetchone()['id']
#             for video in demo_videos:
#                 db.execute(
#                     'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) '
#                     'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                     (video['title'], video['publisher'], video['producer'], video['genre'], 
#                      video['age_rating'], video['url'], creator_id)
#                 )
#             db.commit()
#             print("Demo videos added successfully!")
#         except sqlite3.IntegrityError:
#             pass

# def get_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# @app.route('/')
# def index():
#     if 'user' in session:
#         return redirect(url_for('shorts'))
#     db = get_db()
#     videos = db.execute('SELECT * FROM videos ORDER BY id DESC LIMIT 12').fetchall()
#     return render_template('index.html', videos=videos)

# @app.route('/shorts')
# def shorts():
#     db = get_db()
#     videos = db.execute('''
#         SELECT v.*, 
#                (SELECT COUNT(*) FROM comments c WHERE c.video_id = v.id) as comment_count,
#                (SELECT COUNT(*) FROM likes l WHERE l.video_id = v.id) as like_count
#         FROM videos v
#         ORDER BY v.id DESC
#     ''').fetchall()
#     video_list = []
#     for video in videos:
#         comments = db.execute('''
#             SELECT c.comment, c.rating, u.username, c.created_at
#             FROM comments c 
#             JOIN users u ON c.user_id = u.id 
#             WHERE c.video_id = ? 
#             ORDER BY c.id DESC
#         ''', (video['id'],)).fetchall()
#         video_dict = dict(video)
#         video_dict['comments'] = comments
#         video_dict['comment_count'] = video['comment_count'] or 0
#         video_dict['like_count'] = video['like_count'] or 0
#         video_list.append(video_dict)
#     return render_template('shorts.html', videos=video_list)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']
#         if not username or not password or not role:
#             flash('All fields are required!')
#             return render_template('register.html')
#         hashed_password = hash_password(password)
#         db = get_db()
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 (username, hashed_password, role)
#             )
#             db.commit()
#             flash('Registration successful! Please login.')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Username already exists!')
#             return render_template('register.html')
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if not username or not password:
#             flash('Please enter both username and password!')
#             return render_template('login.html')
#         hashed_password = hash_password(password)
#         db = get_db()
#         user = db.execute(
#             'SELECT * FROM users WHERE username = ? AND password = ?', 
#             (username, hashed_password)
#         ).fetchone()
#         if user:
#             session['user'] = {
#                 'id': user['id'],
#                 'username': user['username'],
#                 'role': user['role']
#             }
#             if user['role'] == 'creator':
#                 flash(f'Welcome back, {username}! You are logged in as a Creator.')
#                 return redirect(url_for('dashboard'))
#             else:
#                 flash(f'Welcome back, {username}! You are logged in as a Consumer.')
#                 return redirect(url_for('shorts'))
#         else:
#             flash('Invalid username or password!')
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     flash('You have been logged out.')
#     return redirect(url_for('index'))

# @app.route('/dashboard')
# def dashboard():
#     if 'user' not in session:
#         flash('Please login first!')
#         return redirect(url_for('login'))
#     if session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can access this page.')
#         return redirect(url_for('index'))
#     db = get_db()
#     videos = db.execute(
#         'SELECT * FROM videos WHERE uploaded_by = ? ORDER BY id DESC', 
#         (session['user']['id'],)
#     ).fetchall()
#     return render_template('upload.html', videos=videos)

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     if 'user' not in session or session['user']['role'] != 'creator':
#         flash('Access denied! Only creators can upload videos.')
#         return redirect(url_for('login'))
#     title = request.form['title']
#     publisher = request.form['publisher']
#     producer = request.form.get('producer', '')
#     genre = request.form.get('genre', '')
#     age_rating = request.form['age_rating']
#     url = request.form['url']
#     if not all([title, publisher, age_rating, url]):
#         flash('Please fill in all required fields!')
#         return redirect(url_for('dashboard'))
#     db = get_db()
#     db.execute(
#         'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) '
#         'VALUES (?, ?, ?, ?, ?, ?, ?)',
#         (title, publisher, producer, genre, age_rating, url, session['user']['id'])
#     )
#     db.commit()
#     flash(f'🎉 Video "{title}" uploaded successfully!')
#     return redirect(url_for('dashboard'))

# @app.route('/watch/<int:video_id>')
# def watch(video_id):
#     db = get_db()
#     video = db.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
#     if not video:
#         flash('Video not found!')
#         return redirect(url_for('index'))
#     comments = db.execute('''
#         SELECT c.comment, c.rating, u.username, c.created_at
#         FROM comments c 
#         JOIN users u ON c.user_id = u.id 
#         WHERE c.video_id = ? 
#         ORDER BY c.id DESC
#     ''', (video_id,)).fetchall()
#     return render_template('watch.html', video=video, comments=comments)

# @app.route('/comment', methods=['POST'])
# def add_comment():
#     if 'user' not in session:
#         return jsonify({"success": false, "message": "Please login to comment!"}), 401
#     video_id = request.form.get('video_id')
#     comment = request.form.get('comment')
#     rating = request.form.get('rating')
#     if not comment or not rating or not video_id:
#         return jsonify({"success": false, "message": "Please fill in all fields!"}), 400
#     try:
#         db = get_db()
#         db.execute(
#             'INSERT INTO comments (video_id, user_id, comment, rating, created_at) '
#             'VALUES (?, ?, ?, ?, ?)',
#             (video_id, session['user']['id'], comment, rating, datetime.utcnow())
#         )
#         db.commit()
#         return jsonify({
#             "success": true,
#             "username": session['user']['username'],
#             "comment": comment,
#             "rating": int(rating),
#             "created_at": "Just now"
#         })
#     except Exception as e:
#         return jsonify({"success": false, "message": str(e)}), 500

# @app.route('/like', methods=['POST'])
# def like():
#     if 'user' not in session:
#         return jsonify({"success": false, "message": "Please login to like!"}), 401
#     video_id = request.form.get('video_id')
#     liked = request.form.get('liked') == 'true'
#     db = get_db()
#     if liked:
#         try:
#             db.execute(
#                 'INSERT INTO likes (video_id, user_id) VALUES (?, ?)',
#                 (video_id, session['user']['id'])
#             )
#             db.commit()
#         except sqlite3.IntegrityError:
#             pass
#     else:
#         db.execute(
#             'DELETE FROM likes WHERE video_id = ? AND user_id = ?',
#             (video_id, session['user']['id'])
#         )
#         db.commit()
#     like_count = db.execute(
#         'SELECT COUNT(*) as count FROM likes WHERE video_id = ?', (video_id,)
#     ).fetchone()['count']
#     return jsonify({"success": true, "like_count": like_count})

# if __name__ == '__main__':
#     if not os.path.exists(DATABASE):
#         init_db()
#     app.run(debug=True, host='0.0.0.0', port=5000)













from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import hashlib
from datetime import datetime
import uuid
import logging

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "videoapp.db"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DATABASE)
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.close()
    add_demo_videos()

# def add_demo_videos():
#     db = get_db()
#     count = db.execute('SELECT COUNT(*) as count FROM videos').fetchone()['count']
#     if count == 0:
#         demo_videos = [
#             {
#                 'title': 'Big Buck Bunny',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'G',
#                 'url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
#             },
#             {
#                 'title': 'Elephants Dream',
#                 'publisher': 'Blender Foundation',
#                 'producer': 'Blender Institute',
#                 'genre': 'Animation',
#                 'age_rating': 'PG',
#                 'url': 'https://sample-videos.com/video123/mp4/720/elephants-dream.mp4'
#             },
#             {
#                 'title': 'For Bigger Blazes',
#                 'publisher': 'Google',
#                 'producer': 'Google',
#                 'genre': 'Tech',
#                 'age_rating': 'G',
#                 'url': 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
#             }
#         ]
#         try:
#             db.execute(
#                 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
#                 ('demo_creator', hash_password('demo123'), 'creator')
#             )
#             db.commit()
#             creator_id = db.execute(
#                 'SELECT id FROM users WHERE username = ?', 
#                 ('demo_creator',)
#             ).fetchone()['id']
#             for video in demo_videos:
#                 db.execute(
#                     'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) '
#                     'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                     (video['title'], video['publisher'], video['producer'], video['genre'], 
#                      video['age_rating'], video['url'], creator_id)
#                 )
#             db.commit()
#             app.logger.info("Demo videos added successfully!")
#         except sqlite3.IntegrityError as e:
#             app.logger.error(f"Error adding demo videos: {e}")

def add_demo_videos():
    db = get_db()
    count = db.execute('SELECT COUNT(*) as count FROM videos').fetchone()['count']
    if count == 0:
        demo_videos = [
            {
                'title': 'Wonders of the Deep Ocean',
                'publisher': 'Blue Horizon Media',
                'producer': 'Marina Clarke',
                'genre': 'Nature',
                'age_rating': 'G',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
            },
            {
                'title': 'Cooking Made Simple: Quick Pasta',
                'publisher': 'KitchenCraft',
                'producer': 'Liam Bennett',
                'genre': 'Cooking',
                'age_rating': 'G',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4'
            },
            {
                'title': 'Street Dance Showcase',
                'publisher': 'Urban Beat Studios',
                'producer': 'Sofia Delgado',
                'genre': 'Dance',
                'age_rating': 'PG',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4'
            },
            {
                'title': 'Adventures in Virtual Reality',
                'publisher': 'FutureVision',
                'producer': 'Daniel Iqbal',
                'genre': 'Technology',
                'age_rating': 'PG',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
            },
            {
                'title': 'Beginner Yoga Flow',
                'publisher': 'Mind & Motion',
                'producer': 'Anya Patel',
                'genre': 'Health & Fitness',
                'age_rating': 'G',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4'
            }
        ]

        try:
            db.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                ('demo_creator', hash_password('demo123'), 'creator')
            )
            db.commit()
            creator_id = db.execute(
                'SELECT id FROM users WHERE username = ?', 
                ('demo_creator',)
            ).fetchone()['id']
            for video in demo_videos:
                db.execute(
                    'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (video['title'], video['publisher'], video['producer'], video['genre'], 
                     video['age_rating'], video['url'], creator_id)
                )
            db.commit()
            app.logger.info("Demo educational videos added successfully!")
        except sqlite3.IntegrityError as e:
            app.logger.error(f"Error adding demo videos: {e}")



def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('shorts'))
    db = get_db()
    videos = db.execute('SELECT * FROM videos ORDER BY id DESC LIMIT 12').fetchall()
    return render_template('index.html', videos=videos)

@app.route('/shorts')
def shorts():
    db = get_db()
    try:
        videos = db.execute('''
            SELECT v.*, 
                   (SELECT COUNT(*) FROM comments c WHERE c.video_id = v.id) as comment_count,
                   (SELECT COUNT(*) FROM likes l WHERE l.video_id = v.id) as like_count
            FROM videos v
            ORDER BY v.id DESC
        ''').fetchall()
        video_list = []
        for video in videos:
            comments = db.execute('''
                SELECT c.comment, c.rating, u.username, c.created_at
                FROM comments c 
                JOIN users u ON c.user_id = u.id 
                WHERE c.video_id = ? 
                ORDER BY c.id DESC
            ''', (video['id'],)).fetchall()
            video_dict = dict(video)
            video_dict['comments'] = comments
            video_dict['comment_count'] = video['comment_count'] or 0
            video_dict['like_count'] = video['like_count'] or 0
            video_list.append(video_dict)
        return render_template('shorts.html', videos=video_list)
    except sqlite3.Error as e:
        app.logger.error(f"Error in /shorts route: {e}")
        flash('An error occurred while loading videos.')
        return render_template('shorts.html', videos=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if not username or not password or not role:
            flash('All fields are required!')
            return render_template('register.html')
        hashed_password = hash_password(password)
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role)
            )
            db.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Please enter both username and password!')
            return render_template('login.html')
        hashed_password = hash_password(password)
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', 
            (username, hashed_password)
        ).fetchone()
        if user:
            session['user'] = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
            if user['role'] == 'creator':
                flash(f'Welcome back, {username}! You are logged in as a Creator.')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Welcome back, {username}! You are logged in as a Consumer.')
                return redirect(url_for('shorts'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))
    if session['user']['role'] != 'creator':
        flash('Access denied! Only creators can access this page.')
        return redirect(url_for('index'))
    db = get_db()
    videos = db.execute(
        'SELECT * FROM videos WHERE uploaded_by = ? ORDER BY id DESC', 
        (session['user']['id'],)
    ).fetchall()
    return render_template('upload.html', videos=videos)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'user' not in session or session['user']['role'] != 'creator':
        flash('Access denied! Only creators can upload videos.')
        return redirect(url_for('login'))
    title = request.form['title']
    publisher = request.form['publisher']
    producer = request.form.get('producer', '')
    genre = request.form.get('genre', '')
    age_rating = request.form['age_rating']
    file = request.files.get('file')
    url = request.form.get('url', '')

    if not all([title, publisher, age_rating]):
        flash('Please fill in all required fields!')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        url = f"/{file_path}"
    elif not url:
        flash('Please provide a video file or URL!')
        return redirect(url_for('dashboard'))

    db = get_db()
    try:
        db.execute(
            'INSERT INTO videos (title, publisher, producer, genre, age_rating, url, uploaded_by) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, publisher, producer, genre, age_rating, url, session['user']['id'])
        )
        db.commit()
        flash(f'🎉 Video "{title}" uploaded successfully!')
    except sqlite3.Error as e:
        app.logger.error(f"Error uploading video: {e}")
        flash('An error occurred while uploading the video.')
    return redirect(url_for('dashboard'))

@app.route('/watch/<int:video_id>')
def watch(video_id):
    db = get_db()
    try:
        video = db.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
        if not video:
            flash('Video not found!')
            return redirect(url_for('index'))
        comments = db.execute('''
            SELECT c.comment, c.rating, u.username, c.created_at
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.video_id = ? 
            ORDER BY c.id DESC
        ''', (video_id,)).fetchall()
        app.logger.debug(f"Comments for video {video_id}: {comments}")

        return render_template('watch.html', video=video, comments=comments)
    except sqlite3.Error as e:
        app.logger.error(f"Error in /watch route: {e}")
        flash('An error occurred while loading the video.')
        return redirect(url_for('index'))

@app.route('/comment', methods=['POST'])
def add_comment():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please login to comment!"}), 401
    video_id = request.form.get('video_id')
    comment = request.form.get('comment')
    rating = request.form.get('rating')

    if not all([video_id, comment, rating]):
        return jsonify({"success": False, "message": "Please fill in all fields!"}), 400
    
    try:
        video_id = int(video_id)
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"success": False, "message": "Rating must be between 1 and 5!"}), 400
        
        db = get_db()
        # Verify video_id exists
        video = db.execute('SELECT id FROM videos WHERE id = ?', (video_id,)).fetchone()
        if not video:
            return jsonify({"success": False, "message": "Invalid video ID!"}), 400
        
        db.execute(
            'INSERT INTO comments (video_id, user_id, comment, rating, created_at) '
            'VALUES (?, ?, ?, ?, ?)',
            (video_id, session['user']['id'], comment, rating, datetime.utcnow())
        )
        db.commit()
        return jsonify({
            "success": True,
            "username": session['user']['username'],
            "comment": comment,
            "rating": rating,
            "created_at": "Just now"
        })
    except (ValueError, sqlite3.Error) as e:
        app.logger.error(f"Error in /comment route: {e}")
        return jsonify({"success": False, "message": f"Error posting comment: {str(e)}"}), 500

@app.route('/like', methods=['POST'])
def like():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please login to like!"}), 401
    video_id = request.form.get('video_id')
    liked = request.form.get('liked') == 'true'

    if not video_id:
        return jsonify({"success": False, "message": "Video ID is required!"}), 400
    
    try:
        video_id = int(video_id)
        db = get_db()
        # Verify video_id exists
        video = db.execute('SELECT id FROM videos WHERE id = ?', (video_id,)).fetchone()
        if not video:
            return jsonify({"success": False, "message": "Invalid video ID!"}), 400
        
        if liked:
            try:
                db.execute(
                    'INSERT INTO likes (video_id, user_id) VALUES (?, ?)',
                    (video_id, session['user']['id'])
                )
                db.commit()
            except sqlite3.IntegrityError:
                pass  # Already liked, ignore
        else:
            db.execute(
                'DELETE FROM likes WHERE video_id = ? AND user_id = ?',
                (video_id, session['user']['id'])
            )
            db.commit()
        
        like_count = db.execute(
            'SELECT COUNT(*) as count FROM likes WHERE video_id = ?', (video_id,)
        ).fetchone()['count']
        return jsonify({"success": True, "like_count": like_count})
    except (ValueError, sqlite3.Error) as e:
        app.logger.error(f"Error in /like route: {e}")
        return jsonify({"success": False, "message": f"Error updating like: {str(e)}"}), 500

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)