from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reference_image_path = db.Column(db.String(255), nullable=False)
    display_image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reference_image_path': self.reference_image_path,
            'display_image_path': self.display_image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

