import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.API.database_sql import CityObject, Base, Session  # Импортируйте ваши модели и Base из файла с БД


csv.field_size_limit(1000000)
def import_csv_to_mysql(csv_file_path, db_connection_string):
    # Создаем подключение к MySQL
    
    # Создаем таблицы (если они еще не существуют)
    
    # Создаем сессию
    session = Session()
    
    try:
        # Открываем CSV файл
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # Преобразуем строку в нужные типы данных
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                last_check = datetime.strptime(row['last_check'], '%Y-%m-%d %H:%M:%S')
                photo = row['photo']
                
                # Создаем объект CityObject
                city_object = CityObject(
                    latitude=latitude,
                    longitude=longitude,
                    last_check=last_check,
                    photo=photo
                )
                
                # Добавляем объект в сессию
                session.add(city_object)
            
            # Фиксируем изменения в БД
            session.commit()
            print(f"Успешно импортировано {csv_reader.line_num - 1} записей.")
    
    except Exception as e:
        # В случае ошибки откатываем изменения
        session.rollback()
        print(f"Произошла ошибка: {e}")
    
    finally:
        # Закрываем сессию
        session.close()

# Пример использования
if __name__ == '__main__':
    # Замените на путь к вашему CSV файлу
    csv_file_path = 'ads_dataset_500.csv'
    
    db_connection_string = 'sqlite:///city_objects.db'
    
    import_csv_to_mysql(csv_file_path, db_connection_string)