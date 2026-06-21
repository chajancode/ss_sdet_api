class YandexError:
    """Коды ошибок Яндекс.Диска, встречающиеся в тестах."""
    NOT_FOUND = 'DiskNotFoundError'
    FIELD_VALIDATION = 'FieldValidationError'
    PATH_DOESNT_EXIST = 'DiskPathDoesntExistsError'
    PATH_EXISTS = 'DiskPathPointsToExistentDirectoryError'
    UNAUTHORIZED = 'UnauthorizedError'
    RESOURSE_EXISTS = 'DiskResourceAlreadyExistsError'


def assert_api_error(
        result,
        status_code: int,
        error: str | None = None
) -> None:
    """
    Проверяет, что ответ - ошибка с заданным статусом и непустым телом.

    Args:
        result (FullAPIResponse): Ответ сервиса.
        status_code (int): Ожидаемый статус-код.
        error (str | None): Ожидаемая ошибка API Яндекса. Если None -
            конкретный код ошибкм не проверяется (только наличие полей).
    """
    assert result.status_code == status_code
    assert result.error is not None
    assert result.error.error == error
    assert result.error.description
    assert result.error.message


def assert_success_link(
        result,
        status_code: int = 201
) -> None:
    """
    Проверяет успешный ответ-ссылку (создание/восстановление папки).

    Args:
        result (FullAPIResponse): Ответ сервиса.
        status_code (int): Ожидаемый статус-код (по умолчанию 201).
    """
    assert result.status_code == status_code
    assert result.response_body is not None
    assert result.response_body.method == 'GET'
    assert result.response_body.href
