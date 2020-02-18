from django.http import HttpRequest, JsonResponse


def health(_: HttpRequest) -> JsonResponse:
    return JsonResponse("ok", safe=False)
