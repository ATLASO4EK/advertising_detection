from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

Base = declarative_base()

class CityObject(Base):
    __tablename__ = 'city_objects'
    id = Column(Integer, primary_key=True)
    photo = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    last_check = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "photo": self.photo,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "last_check": self.last_check.isoformat() if self.last_check else None
        }
    
    def print(self):
        print(self.id)
        print(self.last_check)
        print(self.latitude)
        print(self.longitude)
        print(self.photo)



# Database setup
engine = create_engine('sqlite:///data/city_objects.db')
Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(engine)

def add_city_object(photo, latitude, longitude, last_check=None):
    session = Session()
    if last_check is None:
        last_check = datetime.datetime.utcnow()
    obj = CityObject(photo=photo, latitude=latitude, longitude=longitude, last_check=last_check)
    session.add(obj)
    session.commit()
    session.close()
    return obj

def get_objects():
    session = Session()
    objs = session.query(CityObject).all()
    session.close()
    return objs


if __name__ == '__main__':
    create_db()