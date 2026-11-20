import json
from http import HTTPStatus

from django.http import JsonResponse


def json_error(message: str, status: HTTPStatus) -> JsonResponse:
    return JsonResponse({'status': 'error', 'message': message}, status=status)


def read_body(request) -> dict:
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body or '{}')
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}
    return request.POST
