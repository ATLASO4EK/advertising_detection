from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

Base = declarative_base()

class TicketObject(Base):
    __tablename__ = 'ticket_objects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, nullable=False)
    user_id = Column(String, nullable=False)
    user_photo = Column(String, nullable=False)
    user_lat = Column(Float, nullable=False)
    user_lon = Column(Float, nullable=False)
    user_time = Column(DateTime, nullable=False)
    not_fake = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "create_time": self.create_time,
            "user_id": self.user_id,
            "user_photo": self.user_photo,
            "user_lat": self.user_lat,
            "user_lon": self.user_lon,
            "user_time": self.user_time,
            "not_fake": self.not_fake
        }

    def print(self):
        print(self.id)
        print(self.create_time)
        print(self.user_id)
        print(self.user_photo)
        print(self.user_lat)
        print(self.user_lon)
        print(self.user_time)
        print(self.not_fake)


# Database setup
engine = create_engine('sqlite:///src/API/data/ticket_objects.db')
Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(engine)


def add_ticket_object(create_time, user_id, user_photo, user_lat, user_lon, user_time, not_fake):
    session = Session()
    obj = TicketObject(create_time=create_time, user_id=user_id, user_photo=user_photo, user_lat=user_lat, user_lon=user_lon, user_time=user_time, not_fake=not_fake)
    session.add(obj)
    session.commit()
    session.close()
    return obj


def get_objects():
    session = Session()
    objs = session.query(TicketObject).all()
    session.close()
    return objs


if __name__ == '__main__':
    create_db()