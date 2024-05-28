# from firebase_functions import https_fn, options
# from firebase_admin import initialize_app 
from chargingPlanService import ChargingPlanService as cps
# import json

# initialize_app()


# @https_fn.on_request(region='europe-west3', cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post", "options"]))
# def on_report_request(req: https_fn.Request) -> https_fn.Response:
        
#     body = req.get_json()
    
#     try:
#         settings = body['settings']
#     except Exception as e:
#         return https_fn.Response("Please provide a valid json: settings missing", status=400)
    
#     try:
#         sim_data = body['sim_data']
#     except Exception as e:
#         return https_fn.Response("Please provide a valid json: sim_data missing", status=400)
   
#     try:
#         cars = body['cars']
#     except Exception as e:
#         return https_fn.Response("Please provide a valid json: cars missing", status=400)
    
#     report = cps.getJSONReport(sim_data, cars, settings)
    
#     return https_fn.Response(report)


import functions_framework


@functions_framework.http
def on_report_request(request):
    
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    headers = {"Access-Control-Allow-Origin": "*"}
    
    body = request.get_json(silent = True)
    
    try:
        settings = body['settings']
    except Exception as e:
        return ("Please provide a valid json: settings missing", 400, headers)
    
    try:
        sim_data = body['sim_data']
    except Exception as e:
        return ("Please provide a valid json: sim_data missing", 400, headers)
   
    try:
        cars = body['cars']
    except Exception as e:
        return ("Please provide a valid json: cars missing", 400, headers)
    
    report = cps.getJSONReport(sim_data, cars, settings)
    
    return (report, 200, headers)

