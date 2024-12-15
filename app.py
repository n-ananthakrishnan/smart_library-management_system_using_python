from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import cv2
from pyzbar.pyzbar import decode
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    rack_no = db.Column(db.String(20), nullable=False)
    genre = db.Column(db.String(50), nullable=False)


# Home page
@app.route('/')
def index():
    return render_template('index.html')

# View total books
@app.route('/books')
def view_books():
    books = Book.query.all()
    return render_template('list_books.html', books=books)

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Add a new book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        barcode = request.form['barcode']
        rack_no = request.form['rack_no']
        genre = request.form['genre']
        

        if title and barcode and rack_no and genre:
            

            new_book = Book(title=title, barcode=barcode, rack_no=rack_no, genre=genre)
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('view_books'))
        flash('All fields are required!', 'danger')
    return render_template('add_book.html')

# Barcode scanning
@app.route('/scan', methods=['GET', 'POST'])
def scan_book():
    if request.method == 'POST':
        rack_no = request.form.get('rack_no')
        if not rack_no:
            return render_template('scan.html', error="Please enter a rack number.")

        # Initialize camera to scan barcode
        cap = cv2.VideoCapture(0)
        scanned_data = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Decode barcodes
            barcodes = decode(frame)
            for barcode in barcodes:
                scanned_data = barcode.data.decode('utf-8')
                break

            # Stop scanning if data is found
            if scanned_data:
                break

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if not scanned_data:
            return render_template('scan.html', error="No barcode detected. Try again.")

        # Check book placement
        book = Book.query.filter_by(barcode=scanned_data).first()
        if book:
            if book.rack_no == rack_no:
                # Correct rack
                recommendations = Book.query.filter(Book.genre == book.genre, Book.id != book.id).limit(3).all()
                return render_template(
                    'scan_result.html',
                    message=f"The book '{book.title}' is in the correct rack.",
                    recommendations=recommendations
                )
            else:
                # Incorrect rack
                return render_template(
                    'scan_result.html',
                    message=f"The book '{book.title}' is in the wrong rack. It should be in rack {book.rack_no}."
                )
        else:
            return render_template('scan_result.html', message="Book not found in the database.")
    return render_template('scan.html')

# Edit book details
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        # Update book details with form data
        book.title = request.form['title']
        book.barcode = request.form['barcode']
        book.genre = request.form['genre']
        book.rack_no = request.form['rack_no']  # Use rack_no instead of rack
        
        db.session.commit()  # Save changes to the database
        flash("Book details updated successfully!", "success")
        return redirect(url_for('view_books'))  # Redirect to view books after saving changes
    
    return render_template('edit_book.html', book=book)

# Delete book
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('view_books'))

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()  # Create tables if not already created
    app.run(debug=True)
