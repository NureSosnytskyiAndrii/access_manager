import os

from django.http import JsonResponse
from django.views import View
from .ml_logic.predict import predict_access


class PredictAccessView(View):
    def get(self, request):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(BASE_DIR, 'ml', 'ml_logic', 'user_data.xlsx')
        result = predict_access(file_path)
        response_data = result[["username", "recommend_change"]].to_dict(orient="records")
        return JsonResponse({"recommendations": response_data})
