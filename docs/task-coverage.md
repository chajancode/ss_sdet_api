# Что автоматизировано

Тест-кейсы написаны и проверены ментором, затем автоматизированы. Автотесты сами создают тестовые данные и убирают их за собой, поэтому не зависят от конкретных id из ручных кейсов.

## D1. CRUD через REST API со сверкой в БД (WordPress)

- №1 Создание поста: 201, поля в теле ответа + запись с верными полями в `wp_posts` → [`test_interactions_with_posts.py::test_post_creation`](../tests/test_posts/test_interactions_with_posts.py)
- №2 Редактирование поста: 200, изменённые `post_title`/`post_content` в БД → [`test_post_patching`](../tests/test_posts/test_interactions_with_posts.py)
- №3 Удаление поста: 200 `deleted:true`, записи нет в БД, повторное удаление 404 → [`test_post_deletion`](../tests/test_posts/test_interactions_with_posts.py)
- №4 Создание комментария: 201, запись в `wp_comments` → [`test_interactions_with_comments.py::test_post_creation`](../tests/test_comments/test_interactions_with_comments.py)
- №5 Редактирование комментария: 200, изменённый `comment_content` в БД → [`test_post_patching`](../tests/test_comments/test_interactions_with_comments.py)
- №6 Удаление комментария: 200 `deleted:true`, повторное удаление 404 → [`test_post_deletion`](../tests/test_comments/test_interactions_with_comments.py)

## D2. Получение данных через API + подготовка тест-данных в БД

- D2-1 Список постов без параметров (5 шт., все `publish`) → [`test_get_posts_from_db.py::test_get_all_created_posts`](../tests/test_posts/test_get_posts_from_db.py)
- D2-2 Получение поста по id → [`test_get_post_by_id`](../tests/test_posts/test_get_posts_from_db.py)
- D2-3 Несуществующий пост: 404 `rest_post_invalid_id` → [`test_get_post_not_exists`](../tests/test_posts/test_get_posts_from_db.py)
- D2-4 / D2-5 Фильтрация постов по статусу `publish` и `draft` (параметризация) → [`test_get_post_by_status`](../tests/test_posts/test_get_posts_from_db.py)
- D2-6 Список комментариев к посту (5 шт., `approved`) → [`test_get_comms_from_db.py::test_all_created_comms`](../tests/test_comments/test_get_comms_from_db.py)
- D2-7 Получение комментария по id → [`test_get_comm_by_id`](../tests/test_comments/test_get_comms_from_db.py)
- D2-8 Несуществующий комментарий: 404 `rest_comment_invalid_id` → [`test_get_comm_not_exists`](../tests/test_comments/test_get_comms_from_db.py)
- D2-9 / D2-10 Фильтрация комментариев по статусу `approved` и `trash` (параметризация) → [`test_get_comm_by_status`](../tests/test_comments/test_get_comms_from_db.py)

Тестовые данные создаются прямо в БД через слой repository/DAO и удаляются в teardown фикстур → [`tests/fixtures/`](../tests/fixtures), [`database/repositories/`](../database/repositories)

## D3. Автотесты REST (Yandex.Disk, тест-кейсы №1 и №2)

- №1 Авторизация с валидным токеном: `GET v1/disk/`, 200, поля `user.login`/`user.display_name` → [`test_get_user_data.py::test_authorize_with_valid_token`](../tests/test_yandex/test_get_user_data.py)
- №2 Авторизация без токена: 401, поля `error`/`description`/`message` → [`test_authorize_without_token`](../tests/test_yandex/test_get_user_data.py)

## D4. Папки Yandex.Disk (создание / удаление / восстановление)

- C-1 Создание папки: 201, тело со `method`/`href`/`templated` → [`test_create_folder.py::test_create_folder`](../tests/test_yandex/test_create_folder.py)
- C-2 Создание с `path=/`: 409 `DiskPathDoesntExistsError` → [`test_create_folder_with_slash`](../tests/test_yandex/test_create_folder.py)
- C-3 Создание без имени: 400 `FieldValidationError` → [`test_create_folder_without_folder_name`](../tests/test_yandex/test_create_folder.py)
- C-4 Создание уже существующей: 409 `DiskPathPointsToExistentDirectoryError` → [`test_create_folder_with_existing_folder_name`](../tests/test_yandex/test_create_folder.py)
- D-1 Удаление в корзину: 204, папка в корзине → [`test_delete_folder.py::test_delete_folder`](../tests/test_yandex/test_delete_folder.py)
- D-2 Удаление безвозвратно (`permanently=true`): 204, не в корзине → [`test_delete_permanently`](../tests/test_yandex/test_delete_folder.py)
- D-3 Удаление несуществующей: 404 `DiskNotFoundError` → [`test_delete_folder_doesnt_exist`](../tests/test_yandex/test_delete_folder.py)
- D-4 Удаление без параметров: 400 `FieldValidationError` → [`test_delete_folder_without_params`](../tests/test_yandex/test_delete_folder.py)
- R-1 Восстановление из корзины: 201 → [`test_restore_folder.py::test_restore_folder_from_trash`](../tests/test_yandex/test_restore_folder.py)
- R-2 Восстановление несуществующей: 404 `DiskNotFoundError` → [`test_restore_folder_doesnt_exist`](../tests/test_yandex/test_restore_folder.py)

## D5. Параллельный запуск тестов (pytest-xdist)

- Запуск в один поток → [`run_tests.sh`](../bash_scripts/run_tests.sh)
- Запуск в 3 потока → [`run_tests_parallel.sh`](../bash_scripts/run_tests_parallel.sh)

## D6. Полная валидация (Yandex.Disk, тест-кейсы №3 и №4)

- №3 Загрузка и копирование файла: 200 / 201 / 409 при повторном копировании, поля ответа → [`test_upload_copy_download_file.py::test_upload_and_copy_file`](../tests/test_yandex/test_upload_copy_download_file.py)
- №4 Скачивание файла и сверка содержимого → [`test_download_file`](../tests/test_yandex/test_upload_copy_download_file.py)
- Data-классы для сериализации запросов и десериализации ответов → [`models/yandex/`](../models/yandex)

## D7. JSON Schema Validation

- Получение списка файлов + проверка тела ответа на соответствие структуре через JSON Schema → [`test_get_files_list.py::test_get_files_list`](../tests/test_yandex/test_get_files_list.py), [`schemas/file_list_schema.py`](../schemas/file_list_schema.py)
