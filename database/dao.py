import os
import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import func
from database.db import async_session_maker
from database.models import Category, RegCommand, Users, Member, Lectures, LectureRegistrations
from typing import Optional, Dict, Any
from datetime import datetime


class BaseDAO:

    @staticmethod
    async def check_auth(first_name: str, last_name: str, user_tg: str, username_tg: str):
        f'''
        Метод, который проверят тип пользователя

        Аргументы:
            - first_name
            - last_name
            - tg_id

        Вохвращает: 
            - True - пользователь админ 
            - False - пользователь обычный
        '''

        async with async_session_maker() as session: 
            query = select(Users).filter_by(user_tg=username_tg)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if user.is_admin: 
                return user.is_admin
            else: 
                user_name = f"{first_name} {last_name}".stripe()
                new_user = Users(user_name=user_name,
                                 user_tg=user_tg,
                                 is_admin=False,
                                 username_tg=username_tg, 
                                 )
                session.add(new_user)
                await session.commit()
                return new_user.is_admin
    

    @staticmethod
    async def get_all_lectures():
        f'''
        Получение списка всех лекций с количеством оставшихся мест и новыми полями.

        Возвращает:
            Список лекций с полями: id, title, speaker, date, end_time, max_seats, remaining_seats,
            format, conference_link, offline_map_link, offline_photo.
        '''
        async with async_session_maker() as session:
            subquery = (
                select(LectureRegistrations.lecture_id, func.count().label("registration_count"))
                .group_by(LectureRegistrations.lecture_id)
                .subquery()
            )

            query = (
                select(
                    Lectures,
                    (Lectures.max_seats - func.coalesce(subquery.c.registration_count, 0)).label("remaining_seats")
                )
                .outerjoin(subquery, Lectures.id == subquery.c.lecture_id)
            )

            result = await session.execute(query)
            lectures = result.all()

            return [
                {
                    "id": lecture.Lectures.id,
                    "title": lecture.Lectures.title,
                    "speaker": lecture.Lectures.speaker,
                    "date": lecture.Lectures.date,
                    "end_time": lecture.Lectures.end_time,
                    "max_seats": lecture.Lectures.max_seats,
                    "remaining_seats": lecture.remaining_seats,
                    "format": lecture.Lectures.format,
                    "conference_link": lecture.Lectures.conference_link,
                    "offline_map_link": lecture.Lectures.offline_map_link,
                    "offline_photo": lecture.Lectures.offline_photo
                }
                for lecture in lectures
            ]


    @staticmethod
    async def register_for_lecture(lecture_id: int, username_tg: str):
        f'''
        Регистрация пользователя на лекцию.

        Аргументы:
            - lecture_id: ID лекции.
            - tg_id: Telegram ID пользователя.

        Возвращает:
            Кортеж (сообщение, флаг успешной регистрации).
        '''
        async with async_session_maker() as session:
            user_query = select(Users).filter_by(username_tg=username_tg)
            user_result = await session.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                return "Пользователь не найден", False

            lecture_query = select(Lectures).filter_by(id=lecture_id)
            lecture_result = await session.execute(lecture_query)
            lecture = lecture_result.scalar_one_or_none()

            if not lecture:
                return "Лекция не найдена", False

            registration_query = select(LectureRegistrations).filter_by(user_id=user.id, lecture_id=lecture_id)
            registration_result = await session.execute(registration_query)
            existing_registration = registration_result.scalar_one_or_none()

            if existing_registration:
                return "Вы уже зарегистрированы на эту лекцию", False

            registration_count_query = select(func.count()).select_from(LectureRegistrations).filter_by(lecture_id=lecture_id)
            registration_count_result = await session.execute(registration_count_query)
            registration_count = registration_count_result.scalar() or 0

            remaining_seats = lecture.max_seats - registration_count

            if remaining_seats <= 0:
                return "Места на лекцию закончились", False

            new_registration = LectureRegistrations(user_id=user.id, lecture_id=lecture_id)
            session.add(new_registration)
            await session.commit()
            return "Вы успешно зарегистрированы на лекцию", True


    @staticmethod
    async def check_registration_and_get_qr(lecture_id: int, username_tg: str):
        f'''
        Проверка регистрации пользователя на лекцию и получение QR-кода.

        Аргументы:
            - lecture_id: ID лекции.
            - username_tg: Telegram username пользователя.

        Возвращает:
            Сообщение (либо заглушка, либо QR-код, если он будет реализован).
        '''
        async with async_session_maker() as session:
            user_query = select(Users).filter_by(username_tg=username_tg)
            user_result = await session.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                return "Пользователь не найден"

            registration_query = select(LectureRegistrations).filter_by(user_id=user.id, lecture_id=lecture_id)
            registration_result = await session.execute(registration_query)
            registration = registration_result.scalar_one_or_none()

            if not registration:
                return "Вы не зарегистрированы на эту лекцию"

            lecture_query = select(Lectures).filter_by(id=lecture_id)
            lecture_result = await session.execute(lecture_query)
            lecture = lecture_result.scalar_one_or_none()

            if not lecture:
                return "Лекция не найдена"

            current_date = datetime.now().date()
            lecture_date = lecture.date.date()

            if current_date < lecture_date:
                return "QR-код будет доступен в день лекции"
            else:
                return "QR-код будет доступен в день лекции"  # Заглушка


    @staticmethod
    async def create_lecture(lecture_data: Dict[str, Any], offline_photo: Optional[Any] = None) -> Dict[str, Any]:
        f'''
        Создание новой лекции с поддержкой загрузки файла offline_photo.

        Аргументы:
            - lecture_data: Словарь с данными лекции.
            - offline_photo: Загруженный файл (UploadFile) или None.

        Возвращает:
            Данные созданной лекции с remaining_seats.
        '''
        async with async_session_maker() as session:
            # Преобразуем строки date и end_time в объекты datetime
            if isinstance(lecture_data.get("date"), str):
                lecture_data["date"] = datetime.fromisoformat(lecture_data["date"].replace("Z", "+00:00"))
            if isinstance(lecture_data.get("end_time"), str):
                lecture_data["end_time"] = datetime.fromisoformat(lecture_data["end_time"].replace("Z", "+00:00"))

            # Обрабатываем загрузку файла
            offline_photo_path = None
            if offline_photo:
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_extension = offline_photo.filename.split('.')[-1]
                file_name = f"{uuid.uuid4()}.{file_extension}"
                file_path = os.path.join(upload_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(await offline_photo.read())
                offline_photo_path = f"/{file_path}"

            # Если файл загружен, обновляем lecture_data
            lecture_data["offline_photo"] = offline_photo_path or lecture_data.get("offline_photo")

            new_lecture = Lectures(**lecture_data)
            session.add(new_lecture)
            await session.commit()
            await session.refresh(new_lecture)
            return {
                "id": new_lecture.id,
                "title": new_lecture.title,
                "speaker": new_lecture.speaker,
                "date": new_lecture.date,
                "end_time": new_lecture.end_time,
                "max_seats": new_lecture.max_seats,
                "remaining_seats": new_lecture.max_seats,  # Новая лекция, регистраций пока нет
                "format": new_lecture.format,
                "conference_link": new_lecture.conference_link,
                "offline_map_link": new_lecture.offline_map_link,
                "offline_photo": new_lecture.offline_photo
            }


    @staticmethod
    async def update_lecture(lecture_id: int, lecture_data: Dict[str, Any], offline_photo: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        f'''
        Обновление данных лекции с поддержкой загрузки файла offline_photo.

        Аргументы:
            - lecture_id: ID лекции.
            - lecture_data: Словарь с обновленными данными.
            - offline_photo: Загруженный файл (UploadFile) или None.

        Возвращает:
            Данные обновленной лекции с remaining_seats или None, если лекция не найдена.
        '''
        async with async_session_maker() as session:
            query = select(Lectures).filter_by(id=lecture_id)
            result = await session.execute(query)
            lecture = result.scalar_one_or_none()

            if not lecture:
                return None

            # Преобразуем строки date и end_time в объекты datetime
            if isinstance(lecture_data.get("date"), str):
                lecture_data["date"] = datetime.fromisoformat(lecture_data["date"].replace("Z", "+00:00"))
            if isinstance(lecture_data.get("end_time"), str):
                lecture_data["end_time"] = datetime.fromisoformat(lecture_data["end_time"].replace("Z", "+00:00"))

            # Обрабатываем загрузку нового файла
            if offline_photo:
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_extension = offline_photo.filename.split('.')[-1]
                file_name = f"{uuid.uuid4()}.{file_extension}"
                file_path = os.path.join(upload_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(await offline_photo.read())
                lecture_data["offline_photo"] = f"/{file_path}"
            else:
                lecture_data["offline_photo"] = lecture_data.get("offline_photo", lecture.offline_photo)

            for key, value in lecture_data.items():
                setattr(lecture, key, value)

            await session.commit()
            await session.refresh(lecture)

            registration_count_query = select(func.count()).select_from(LectureRegistrations).filter_by(lecture_id=lecture_id)
            registration_count_result = await session.execute(registration_count_query)
            registration_count = registration_count_result.scalar() or 0
            remaining_seats = lecture.max_seats - registration_count

            return {
                "id": lecture.id,
                "title": lecture.title,
                "speaker": lecture.speaker,
                "date": lecture.date,
                "end_time": lecture.end_time,
                "max_seats": lecture.max_seats,
                "remaining_seats": remaining_seats,
                "format": lecture.format,
                "conference_link": lecture.conference_link,
                "offline_map_link": lecture.offline_map_link,
                "offline_photo": lecture.offline_photo
            }


    @staticmethod
    async def delete_lecture(lecture_id: int) -> bool:
        f'''
        Удаление лекции по ID с удалением связанного файла offline_photo.

        Аргументы:
            - lecture_id: ID лекции.

        Возвращает:
            True, если удаление успешно, False, если лекция не найдена.
        '''
        async with async_session_maker() as session:
            query = select(Lectures).filter_by(id=lecture_id)
            result = await session.execute(query)
            lecture = result.scalar_one_or_none()

            if not lecture:
                return False

            # Удаляем файл, если он есть
            if lecture.offline_photo:
                file_path = lecture.offline_photo.lstrip('/')
                if os.path.exists(file_path):
                    os.remove(file_path)

            await session.delete(lecture)
            await session.commit()
            return True
        
        
    @staticmethod
    async def find_user_by_tg_id(username_tg: str) -> Optional[Users]:
        f'''
        Метод для поиска пользователя по tg_id.

        Аргументы:
            - tg_id: Telegram ID пользователя (строка)

        Возвращает:
            Объект Users или None, если пользователь не найден.
        '''
        async with async_session_maker() as session:
            query = select(Users).filter_by(username_tg=username_tg)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user


    @staticmethod
    async def find_category_by_name(category_name: str) -> Optional[Category]:
        f'''
        Метод для поиска категории по имени.

        Аргументы:
            - category_name: Название категории (например, "Дизайн")

        Возвращает:
            Объект Category или None, если категория не найдена.
        '''
        async with async_session_maker() as session:
            query = select(Category).filter_by(name_category=category_name)
            result = await session.execute(query)
            category = result.scalar_one_or_none()
            return category


    @staticmethod
    async def create_team(
        team_name: str,
        category_id: int,
        participants: list[dict],
        tg_id: str
    ) -> RegCommand:
        f'''
----------------------- СКОРЕЕ ВСЕГО НЕ ПРИГОДИТСЯ -------------------------------------------------------------------

        Метод для создания команды и связанных участников.

        Аргументы:
            - team_name: Название команды
            - category_id: ID категории (направления)
            - participants: Список участников (каждый участник — словарь с полями telegram, first_name, last_name)
            - tg_id: Telegram ID пользователя, который регистрирует команду

        Возвращает:
            Созданный объект RegCommand.

        Выбрасывает:
            SQLAlchemyError, если произошла ошибка при сохранении.
        '''
        async with async_session_maker() as session:
            try:
                # Создаем команду
                new_team = RegCommand(
                    command_name=team_name,
                    category_id=category_id
                )
                session.add(new_team)
                await session.commit()
                await session.refresh(new_team)

                # Создаем участников
                for participant in participants:
                    new_member = Member(
                        first_name=participant["first_name"],
                        last_name=participant["last_name"],
                        telegram=participant["telegram"],
                        command_id=new_team.id
                    )
                    session.add(new_member)

                await session.commit()
                return new_team
            except SQLAlchemyError as e:
                await session.rollback()
                raise e