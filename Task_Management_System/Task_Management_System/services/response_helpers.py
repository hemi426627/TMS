from flask import jsonify  # type: ignore
from django.http import JsonResponse


def success(data=None, message="Success"):
    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data if data is not None else [],
            }
        ),
        200,
    )  # always HTTP 200 for success


def error(message="Something went wrong", status=400):
    return jsonify({"success": False, "message": message, "data": []}), status


def successRes(data):
    return JsonResponse({"success": True, "data": data}, safe=False)


def errorRes(message):
    return JsonResponse({"success": False, "message": message}, status=400)